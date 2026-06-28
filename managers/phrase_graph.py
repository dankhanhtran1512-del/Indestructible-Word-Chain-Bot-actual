import json
import os
from datetime import datetime


GRAPH_FILE = "assets/dictionaries/vietnamese/phrase_graph.json"


class PhraseGraph:
    def __init__(self):
        self.graph = self.load_graph()

    def now(self):
        return datetime.now().isoformat(timespec="seconds")

    def load_graph(self):
        if not os.path.exists(GRAPH_FILE):
            return {}

        with open(GRAPH_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_graph(self):
        os.makedirs(os.path.dirname(GRAPH_FILE), exist_ok=True)

        with open(GRAPH_FILE, "w", encoding="utf-8") as file:
            json.dump(self.graph, file, ensure_ascii=False, indent=2)

    def add_phrase(self, phrase, source="manual", confidence=1.0):
        phrase = phrase.lower().strip()
        parts = phrase.split()

        if len(parts) != 2:
            return False

        first_word, second_word = parts

        if first_word not in self.graph:
            self.graph[first_word] = {}

        if second_word not in self.graph[first_word]:
            self.graph[first_word][second_word] = {
                "phrase": phrase,
                "source": source,
                "confidence": confidence,
                "times_used": 0,
                "times_rejected": 0,
                "times_hint": 0,
                "created_at": self.now(),
                "last_used": None
            }
        else:
            self.graph[first_word][second_word]["confidence"] = max(
                self.graph[first_word][second_word].get("confidence", 0),
                confidence
            )

        self.save_graph()
        return True

    def remove_phrase(self, phrase):
        phrase = phrase.lower().strip()
        parts = phrase.split()

        if len(parts) != 2:
            return False

        first_word, second_word = parts

        if first_word not in self.graph:
            return False

        if second_word not in self.graph[first_word]:
            return False

        del self.graph[first_word][second_word]

        if not self.graph[first_word]:
            del self.graph[first_word]

        self.save_graph()
        return True

    def get_entry(self, phrase):
        phrase = phrase.lower().strip()
        parts = phrase.split()

        if len(parts) != 2:
            return None

        first_word, second_word = parts

        return self.graph.get(first_word, {}).get(second_word)

    def get_phrases_starting_with(self, required_word):
        required_word = required_word.lower().strip()

        if required_word not in self.graph:
            return []

        entries = list(self.graph[required_word].values())

        entries.sort(
            key=lambda item: (
                -item.get("confidence", 0),
                item.get("times_rejected", 0),
                -item.get("times_used", 0),
                -item.get("times_hint", 0)
            )
        )

        return [entry["phrase"] for entry in entries]

    def has_continuation(self, required_word, used_phrases=None, rejected_phrases=None):
        used_phrases = used_phrases or []
        rejected_phrases = rejected_phrases or []

        used_set = {phrase.lower().strip() for phrase in used_phrases}
        rejected_set = {phrase.lower().strip() for phrase in rejected_phrases}

        for phrase in self.get_phrases_starting_with(required_word):
            if phrase in used_set:
                continue

            if phrase in rejected_set:
                continue

            return True

        return False

    def get_hint(self, required_word, used_phrases=None, rejected_phrases=None):
        used_phrases = used_phrases or []
        rejected_phrases = rejected_phrases or []

        used_set = {phrase.lower().strip() for phrase in used_phrases}
        rejected_set = {phrase.lower().strip() for phrase in rejected_phrases}

        for phrase in self.get_phrases_starting_with(required_word):
            if phrase in used_set:
                continue

            if phrase in rejected_set:
                continue

            self.mark_hint(phrase)
            return phrase

        return None

    def mark_used(self, phrase):
        entry = self.get_entry(phrase)

        if entry is None:
            self.add_phrase(phrase, source="player", confidence=1.0)
            entry = self.get_entry(phrase)

        entry["times_used"] = entry.get("times_used", 0) + 1
        entry["last_used"] = self.now()

        self.save_graph()

    def mark_rejected(self, phrase):
        entry = self.get_entry(phrase)

        if entry is None:
            self.add_phrase(phrase, source="rejected_hint", confidence=0.0)
            entry = self.get_entry(phrase)

        entry["times_rejected"] = entry.get("times_rejected", 0) + 1
        entry["confidence"] = max(0, entry.get("confidence", 0) - 0.2)

        self.save_graph()

    def mark_hint(self, phrase):
        entry = self.get_entry(phrase)

        if entry is None:
            return

        entry["times_hint"] = entry.get("times_hint", 0) + 1

        self.save_graph()


if __name__ == "__main__":
    graph = PhraseGraph()

    graph.add_phrase("mũi heo", source="test")
    graph.add_phrase("mũi dao", source="test", confidence=0.95)
    graph.add_phrase("heo rừng", source="test")

    graph.mark_used("mũi heo")
    graph.mark_hint("mũi dao")
    graph.mark_rejected("mũi dao")

    print(graph.get_phrases_starting_with("mũi"))
    print(graph.get_hint("mũi"))
    print(graph.has_continuation("heo"))