import os


SOURCE_FILE = "assets/dictionaries/vietnamese/Viet74K.txt"
OUTPUT_FILE = "assets/dictionaries/vietnamese/phrases.txt"


def clean_phrase(text):
    text = text.strip().lower()

    if not text:
        return None

    if any(char.isdigit() for char in text):
        return None

    if any(char in text for char in [",", ".", "!", "?", ":", ";", "(", ")", "[", "]", "{", "}", "\"", "'"]):
        return None

    parts = text.split()

    if len(parts) != 2:
        return None

    if parts[0] == parts[1]:
        return None

    return " ".join(parts)


def main():
    phrases = set()

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            for line in file:
                phrase = clean_phrase(line)
                if phrase:
                    phrases.add(phrase)

    with open(SOURCE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            phrase = clean_phrase(line)
            if phrase:
                phrases.add(phrase)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for phrase in sorted(phrases):
            file.write(phrase + "\n")

    print(f"Done. Saved {len(phrases)} Vietnamese two-word phrases to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()