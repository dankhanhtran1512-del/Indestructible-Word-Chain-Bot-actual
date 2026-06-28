import os
import random


class WordValidator:
    def __init__(self):
        self.words = {}
        self.indexes = {}
        self.phrases = {}

    def load_dictionary(self, language):
        file_path = f"assets/dictionaries/{language}/words.txt"

        if not os.path.exists(file_path):
            print(f"⚠️ Dictionary not found for {language}: {file_path}")
            self.words[language] = set()
            self.indexes[language] = {}
            return

        with open(file_path, "r", encoding="utf-8") as file:
            word_set = {
                line.strip().lower()
                for line in file
                if line.strip() and len(line.strip()) > 1
            }

        self.words[language] = word_set
        self.indexes[language] = self.build_index(word_set)

        print(f"Loaded {len(word_set)} {language} words.")

    def load_vietnamese(self):
        file_path = "assets/dictionaries/vietnamese/phrases.txt"

        if not os.path.exists(file_path):
            print(f"⚠️ Vietnamese phrase file not found: {file_path}")
            self.words["vietnamese"] = set()
            self.phrases["vietnamese"] = set()
            self.indexes["vietnamese"] = {}
            return

        with open(file_path, "r", encoding="utf-8") as file:
            phrase_set = {
                line.strip().lower()
                for line in file
                if line.strip() and len(line.strip().split()) == 2
            }

        self.words["vietnamese"] = phrase_set
        self.phrases["vietnamese"] = phrase_set
        self.indexes["vietnamese"] = self.build_vietnamese_index(phrase_set)

        print(f"Loaded {len(phrase_set)} Vietnamese phrases.")

    def load_english(self):
        self.load_dictionary("english")

    def load_french(self):
        self.load_dictionary("french")

    def load_all(self):
        self.load_dictionary("english")
        self.load_dictionary("french")
        self.load_vietnamese()

    def build_index(self, word_set):
        index = {}

        for word in word_set:
            first_letter = word[0]

            if first_letter not in index:
                index[first_letter] = []

            index[first_letter].append(word)

        return index

    def build_vietnamese_index(self, phrase_set):
        index = {}

        for phrase in phrase_set:
            first_part = phrase.split()[0]

            if first_part not in index:
                index[first_part] = []

            index[first_part].append(phrase)

        return index

    def is_valid(self, word, languages):
        word = word.lower().strip()

        if isinstance(languages, str):
            languages = [languages]

        for language in languages:
            if language in self.words and word in self.words[language]:
                return True

        return False

    def random_word(self, languages, starts_with=None):
        if isinstance(languages, str):
            languages = [languages]

        candidates = []

        if starts_with is None:
            for language in languages:
                candidates.extend(list(self.words.get(language, [])))
        else:
            starts_with = starts_with.lower().strip()

            for language in languages:
                candidates.extend(
                    self.indexes.get(language, {}).get(starts_with, [])
                )

        if not candidates:
            return None

        return random.choice(candidates)

    def is_valid_vietnamese_phrase(self, phrase):
        phrase = phrase.lower().strip()
        return phrase in self.phrases.get("vietnamese", set())

    def random_vietnamese_phrase(self, starts_with=None):
        return self.random_word(["vietnamese"], starts_with)

    def is_valid_english(self, word):
        return self.is_valid(word, ["english"])

    def random_english_word(self, starts_with=None):
        return self.random_word(["english"], starts_with)


if __name__ == "__main__":
    validator = WordValidator()
    validator.load_all()

    print(validator.is_valid("apple", ["english"]))
    print(validator.is_valid("bonjour", ["french"]))
    print(validator.is_valid_vietnamese_phrase("con mèo"))
    print(validator.random_word(["english"], "e"))
    print(validator.random_word(["french"], "b"))
    print(validator.random_vietnamese_phrase("mèo"))