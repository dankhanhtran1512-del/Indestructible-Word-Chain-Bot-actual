import json
import os


RAW_INPUT_FILE = "assets/dictionaries/vietnamese/raw_phrases.txt"
PATTERN_FILE = "assets/dictionaries/vietnamese/patterns.json"
OUTPUT_FILE = "assets/dictionaries/vietnamese/phrases.txt"


def add_raw_phrases(phrases):
    if not os.path.exists(RAW_INPUT_FILE):
        print(f"Raw phrase file not found: {RAW_INPUT_FILE}")
        return

    with open(RAW_INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            phrase = line.strip().lower()

            if not phrase:
                continue

            parts = phrase.split()

            if len(parts) == 2:
                phrases.add(" ".join(parts))


def add_pattern_phrases(phrases):
    if not os.path.exists(PATTERN_FILE):
        print(f"Pattern file not found: {PATTERN_FILE}")
        return

    with open(PATTERN_FILE, "r", encoding="utf-8") as file:
        patterns = json.load(file)

    for pattern_name, pattern_data in patterns.items():
        first_words = pattern_data.get("first_words", [])
        second_words = pattern_data.get("second_words", [])

        for first in first_words:
            for second in second_words:
                phrase = f"{first.strip().lower()} {second.strip().lower()}"
                phrases.add(phrase)


def build_vietnamese_phrases():
    phrases = set()

    add_raw_phrases(phrases)
    add_pattern_phrases(phrases)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for phrase in sorted(phrases):
            file.write(phrase + "\n")

    print(f"Done. Saved {len(phrases)} Vietnamese phrases to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_vietnamese_phrases()