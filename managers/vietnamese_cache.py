import json
import os


CONTINUATION_CACHE_FILE = "assets/dictionaries/vietnamese/continuation_cache.json"


class VietnameseCache:
    def __init__(self):
        self.cache = self.load_cache()

    def load_cache(self):
        if not os.path.exists(CONTINUATION_CACHE_FILE):
            return {}

        with open(CONTINUATION_CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_cache(self):
        os.makedirs(os.path.dirname(CONTINUATION_CACHE_FILE), exist_ok=True)

        with open(CONTINUATION_CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump(self.cache, file, ensure_ascii=False, indent=2)

    def get_continuations(self, required_word):
        required_word = required_word.lower().strip()
        return self.cache.get(required_word, [])

    def set_continuations(self, required_word, continuations):
        required_word = required_word.lower().strip()

        clean_continuations = []

        for phrase in continuations:
            phrase = phrase.lower().strip()

            if phrase and phrase not in clean_continuations:
                clean_continuations.append(phrase)

        self.cache[required_word] = clean_continuations
        self.save_cache()

    def add_continuation(self, required_word, phrase):
        required_word = required_word.lower().strip()
        phrase = phrase.lower().strip()

        if required_word not in self.cache:
            self.cache[required_word] = []

        if phrase not in self.cache[required_word]:
            self.cache[required_word].append(phrase)

        self.save_cache()

    def remove_continuation(self, required_word, phrase):
        required_word = required_word.lower().strip()
        phrase = phrase.lower().strip()

        if required_word not in self.cache:
            return

        self.cache[required_word] = [
            item for item in self.cache[required_word]
            if item != phrase
        ]

        self.save_cache()


if __name__ == "__main__":
    cache = VietnameseCache()

    cache.set_continuations("găm", ["găm hàng", "găm tiền", "găm kim"])
    cache.add_continuation("mũi", "mũi heo")
    cache.remove_continuation("găm", "găm kim")

    print(cache.get_continuations("găm"))
    print(cache.get_continuations("mũi"))