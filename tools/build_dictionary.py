import os


INPUT_FILE = "assets/dictionaries/french/fr_FR.dic"
OUTPUT_FILE = "assets/dictionaries/french/words.txt"


def clean_dictionary():
    words = set()

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file):
            line = line.strip()

            if line_number == 0 and line.isdigit():
                continue

            if not line:
                continue

            word = line.split("/")[0].lower().strip()

            if word:
                words.add(word)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for word in sorted(words):
            file.write(word + "\n")

    print(f"Done. Saved {len(words)} words to {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_dictionary()