class GameEngine:
    def __init__(self, languages):
        if isinstance(languages, str):
            languages = [languages]

        self.languages = languages
        self.language = languages[0]

        self.running = True
        self.current_word = None
        self.required_text = None
        self.used_words = {}
        self.last_player_id = None
        self.last_player_name = None
        self.chain_streak = 0

    def is_vietnamese_mode(self):
        return self.language == "vietnamese"

    def is_streak_milestone(self):
        return self.chain_streak == 10 or (
            self.chain_streak >= 50 and self.chain_streak % 50 == 0
        )

    def get_next_required_text(self, text):
        if self.is_vietnamese_mode():
            return text.split()[-1]

        return text[-1]

    def starts_correctly(self, text):
        if self.current_word is None:
            return True

        if self.is_vietnamese_mode():
            parts = text.split()

            if len(parts) != 2:
                return False

            return parts[0] == self.required_text

        return text.startswith(self.required_text)

    def play_word(self, player_id, player_name, word):
        word = word.lower().strip()

        if not self.running:
            return {
                "accepted": False,
                "reason": "game_not_running",
                "last_word": self.current_word,
                "required_text": self.required_text,
                "chain_streak": self.chain_streak
            }

        if self.last_player_id == player_id:
            return {
                "accepted": False,
                "reason": "same_player",
                "last_word": self.current_word,
                "required_text": self.required_text,
                "chain_streak": self.chain_streak
            }

        if word in self.used_words:
            old_info = self.used_words[word]

            return {
                "accepted": False,
                "reason": "already_used",
                "last_word": self.current_word,
                "required_text": self.required_text,
                "chain_streak": self.chain_streak,
                "used_by": old_info["player_name"],
                "used_at": old_info["chain_number"]
            }

        if not self.starts_correctly(word):
            return {
                "accepted": False,
                "reason": "wrong_start",
                "last_word": self.current_word,
                "required_text": self.required_text,
                "chain_streak": self.chain_streak
            }

        self.chain_streak += 1
        self.current_word = word
        self.required_text = self.get_next_required_text(word)

        self.used_words[word] = {
            "player_id": player_id,
            "player_name": player_name,
            "chain_number": self.chain_streak
        }

        self.last_player_id = player_id
        self.last_player_name = player_name

        return {
            "accepted": True,
            "reason": "word_accepted",
            "current_word": self.current_word,
            "required_text": self.required_text,
            "chain_streak": self.chain_streak,
            "milestone": self.is_streak_milestone()
        }