from managers.vietnamese_ai import VietnameseAI


class AIValidator:
    def __init__(self):
        self.vietnamese_ai = VietnameseAI()

    def validate_vietnamese_phrase(self, phrase, previous_phrase=None):
        class DummyGame:
            current_word = previous_phrase
            required_text = None
            used_words = {}

        dummy = DummyGame()

        return self.vietnamese_ai.validate_move(
            game=dummy,
            phrase=phrase
        )