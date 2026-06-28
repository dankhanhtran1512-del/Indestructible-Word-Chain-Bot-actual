import os

from managers.cache_manager import CacheManager
from managers.gemini_client import GeminiClient
from managers.phrase_graph import PhraseGraph
from managers.prompt_builder import PromptBuilder
from managers.vietnamese_cache import VietnameseCache
from managers.vietnamese_rules import VietnameseRules


LOCAL_PHRASES_FILE = "assets/dictionaries/vietnamese/phrases.txt"


class VietnameseAI:
    def __init__(self):
        self.cache_manager = CacheManager()
        self.phrase_graph = PhraseGraph()
        self.vietnamese_cache = VietnameseCache()
        self.rules = VietnameseRules()
        self.gemini = GeminiClient()
        self.local_phrases = self.load_local_phrases()
        self.last_continuation_status = "unknown"

    def load_local_phrases(self):
        if not os.path.exists(LOCAL_PHRASES_FILE):
            return set()

        with open(LOCAL_PHRASES_FILE, "r", encoding="utf-8") as file:
            return {
                line.strip().lower()
                for line in file
                if line.strip() and len(line.strip().split()) == 2
            }

    def process_move(self, game, phrase):
        phrase = phrase.lower().strip()
        validation = self.validate_move(game, phrase)

        if not validation.get("valid"):
            return {
                "accepted": False,
                "reason": validation.get("reason", "Invalid Vietnamese phrase."),
                "dead_end": False
            }

        self.phrase_graph.add_phrase(
            phrase,
            source=validation.get("source", "player"),
            confidence=validation.get("confidence", 1.0)
        )

        self.phrase_graph.mark_used(phrase)

        return {
            "accepted": True,
            "reason": validation.get("reason", "Valid Vietnamese phrase."),
            "dead_end": False
        }

    def get_continuations(self, required_word, used_phrases=None):
        required_word = required_word.lower().strip()
        used_phrases = used_phrases or []
        self.last_continuation_status = "unknown"

        graph_continuations = self.phrase_graph.get_phrases_starting_with(required_word)

        if graph_continuations:
            self.last_continuation_status = "graph_found"
            return graph_continuations

        local_continuations = [
            phrase for phrase in self.local_phrases
            if phrase.startswith(required_word + " ")
            and phrase not in used_phrases
            and not self.cache_manager.is_rejected(phrase)
        ]

        if local_continuations:
            for phrase in local_continuations:
                self.phrase_graph.add_phrase(
                    phrase,
                    source="local_phrases",
                    confidence=1.0
                )

            self.vietnamese_cache.set_continuations(required_word, local_continuations)
            self.last_continuation_status = "local_found"
            return local_continuations

        cached = self.vietnamese_cache.get_continuations(required_word)

        if cached:
            cached = [
                phrase for phrase in cached
                if phrase not in used_phrases
                and not self.cache_manager.is_rejected(phrase)
            ]

            if cached:
                for phrase in cached:
                    self.phrase_graph.add_phrase(
                        phrase,
                        source="continuation_cache",
                        confidence=0.8
                    )

                self.last_continuation_status = "cache_found"
                return cached

        prompt = PromptBuilder.build_continuation_prompt(
            required_word=required_word,
            used_phrases=used_phrases,
            rejected_phrases=list(self.cache_manager.rejected_cache.keys()),
            limit=20
        )

        result = self.gemini.ask(prompt)

        if not result.get("success"):
            self.last_continuation_status = "ai_failed"
            return []

        if result.get("has_continuation") is False:
            self.last_continuation_status = "confirmed_empty"
            return []

        continuations = result.get("continuations", [])
        clean_continuations = []

        for phrase in continuations:
            phrase = phrase.lower().strip()

            if not phrase:
                continue

            if phrase in clean_continuations:
                continue

            local_result = self.rules.validate(
                phrase=phrase,
                previous_phrase=None
            )

            if not local_result["valid"]:
                continue

            if self.cache_manager.is_rejected(phrase):
                continue

            clean_continuations.append(phrase)

            self.phrase_graph.add_phrase(
                phrase,
                source="gemini_continuation",
                confidence=0.8
            )

        if clean_continuations:
            self.last_continuation_status = "ai_found"
        else:
            self.last_continuation_status = "confirmed_empty"

        self.vietnamese_cache.set_continuations(required_word, clean_continuations)

        return clean_continuations

    def get_hint(self, game):
        required_word = game.required_text

        if not required_word:
            return None

        used_phrases = list(game.used_words.keys())
        rejected_phrases = list(self.cache_manager.rejected_cache.keys())

        graph_hint = self.phrase_graph.get_hint(
            required_word=required_word,
            used_phrases=used_phrases,
            rejected_phrases=rejected_phrases
        )

        if graph_hint:
            return graph_hint

        continuations = self.get_continuations(
            required_word=required_word,
            used_phrases=used_phrases
        )

        for phrase in continuations:
            phrase = phrase.lower().strip()

            if phrase in game.used_words:
                continue

            if self.cache_manager.is_rejected(phrase):
                continue

            local_result = self.rules.validate(
                phrase=phrase,
                previous_phrase=game.current_word
            )

            if not local_result["valid"]:
                continue

            self.phrase_graph.mark_hint(phrase)
            return phrase

        return None

    def reject_hint(self, game, phrase):
        self.reject_phrase(
            game=game,
            phrase=phrase,
            rejected_by_id=None,
            rejected_by_name=None
        )

    def reject_phrase(self, game, phrase, rejected_by_id=None, rejected_by_name=None):
        phrase = phrase.lower().strip()

        reason = "Rejected by player because the phrase does not have a real Vietnamese meaning."
        source = "player_rejected_phrase"

        if rejected_by_name:
            reason = f"Rejected by player {rejected_by_name} because the phrase does not have a real Vietnamese meaning."

        self.cache_manager.reject(
            phrase,
            reason=reason,
            source=source,
            confidence=1.0
        )

        self.phrase_graph.mark_rejected(phrase)
        self.phrase_graph.remove_phrase(phrase)

        self.local_phrases.discard(phrase)

        if game is not None and getattr(game, "required_text", None):
            self.vietnamese_cache.remove_continuation(game.required_text, phrase)

        first_word = phrase.split()[0] if phrase.split() else None

        if first_word:
            self.vietnamese_cache.remove_continuation(first_word, phrase)

    def validate_move(self, game, phrase):
        phrase = phrase.lower().strip()

        local_result = self.rules.validate(
            phrase=phrase,
            previous_phrase=game.current_word
        )

        if not local_result["valid"]:
            return local_result

        rejected_result = self.cache_manager.get_rejected(phrase)

        if rejected_result is not None:
            reason = rejected_result.get("reason", "").lower()

            if "ai is unavailable" not in reason:
                return rejected_result

        approved_result = self.cache_manager.get_approved(phrase)

        if approved_result is not None:
            self.phrase_graph.add_phrase(
                phrase,
                source="approved_cache",
                confidence=approved_result.get("confidence", 1.0)
            )

            return approved_result

        if phrase in self.local_phrases:
            self.cache_manager.approve(
                phrase,
                reason="Found in local Vietnamese phrase dictionary.",
                source="local_phrases",
                confidence=1.0
            )

            self.phrase_graph.add_phrase(
                phrase,
                source="local_phrases",
                confidence=1.0
            )

            return {
                "valid": True,
                "reason": "Found in local Vietnamese phrase dictionary.",
                "source": "local_phrases",
                "confidence": 1.0
            }

        prompt = PromptBuilder.build_validation_prompt(phrase)
        result = self.gemini.ask(prompt)

        if not result.get("success"):
            return {
                "valid": False,
                "reason": "AI is unavailable right now. Please try another phrase."
            }

        if result.get("valid"):
            self.cache_manager.approve(
                phrase,
                reason=result.get("reason", "Approved by AI."),
                source="gemini",
                confidence=result.get("confidence", 0.8)
            )

            self.phrase_graph.add_phrase(
                phrase,
                source="gemini_validated",
                confidence=result.get("confidence", 0.8)
            )

        else:
            self.cache_manager.reject(
                phrase,
                reason=result.get("reason", "Rejected by AI."),
                source="gemini",
                confidence=result.get("confidence", 0.8)
            )

            self.phrase_graph.mark_rejected(phrase)

        return result

    def check_dead_end(self, game):
        required_word = game.required_text

        if not required_word:
            return False

        used_phrases = list(game.used_words.keys())
        rejected_phrases = list(self.cache_manager.rejected_cache.keys())

        if self.phrase_graph.has_continuation(
            required_word=required_word,
            used_phrases=used_phrases,
            rejected_phrases=rejected_phrases
        ):
            return False

        continuations = self.get_continuations(
            required_word=required_word,
            used_phrases=used_phrases
        )

        if continuations:
            return False

        return self.last_continuation_status == "confirmed_empty"