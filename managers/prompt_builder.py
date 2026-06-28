class PromptBuilder:
    """
    Builds every prompt sent to Gemini.

    GeminiClient should NEVER contain prompt text.
    """

    @staticmethod
    def build_validation_prompt(phrase):
        return f"""
You are an expert in the Vietnamese language.

Determine whether the following phrase is a natural Vietnamese two-word phrase suitable for a Vietnamese nối chữ game.

Phrase:
"{phrase}"

Rules:

- Exactly two Vietnamese words.
- Commonly understood.
- Natural Vietnamese.
- No slang.
- No abbreviations.
- No proper names.
- No offensive content.
- Not an invented phrase.

Reply ONLY as JSON.

{{
    "valid": true,
    "confidence": 0.98,
    "reason": "Natural Vietnamese phrase."
}}
"""

    @staticmethod
    def build_continuation_prompt(
        required_word,
        used_phrases=None,
        rejected_phrases=None,
        limit=20
    ):
        used_phrases = used_phrases or []
        rejected_phrases = rejected_phrases or []

        used = "\n".join(f"- {x}" for x in used_phrases)
        rejected = "\n".join(f"- {x}" for x in rejected_phrases)

        return f"""
You are an expert in Vietnamese.

Generate up to {limit} natural Vietnamese two-word phrases.

Requirements:

- FIRST word MUST be "{required_word}".
- SECOND word may be anything natural.
- Exactly two words.
- Commonly understood.
- Do NOT invent phrases.
- Do NOT return slang.
- Do NOT return abbreviations.
- Do NOT return proper names.
- Do NOT repeat words.
- Do NOT include phrases from the Used list.
- Do NOT include phrases from the Rejected list.

Used phrases

{used}

Rejected phrases

{rejected}

Reply ONLY as JSON.

{{
    "has_continuation": true,
    "continuations": [
        "example phrase 1",
        "example phrase 2"
    ]
}}
"""

    @staticmethod
    def build_dead_end_prompt(required_word, used_phrases):
        used = "\n".join(f"- {x}" for x in used_phrases)

        return f"""
You are an expert in Vietnamese.

Determine whether any natural Vietnamese two-word phrase exists whose first word is:

"{required_word}"

Already used:

{used}

If every natural continuation has already been used, return

{{
    "dead_end": true
}}

Otherwise return

{{
    "dead_end": false
}}
"""

    @staticmethod
    def build_definition_prompt(phrase):
        return f"""
Explain this Vietnamese phrase briefly.

Phrase:

"{phrase}"

Reply ONLY as JSON.

{{
    "definition":"..."
}}
"""

    @staticmethod
    def build_synonym_prompt(word):
        return f"""
Give several Vietnamese synonyms.

Word:

"{word}"

Reply ONLY as JSON.

{{
    "synonyms":[]
}}
"""

    @staticmethod
    def build_quality_check_prompt(phrase):
        return f"""
Rate how common this Vietnamese phrase is.

Phrase:

"{phrase}"

Reply ONLY as JSON.

{{
    "common":true,
    "confidence":0.97
}}
"""