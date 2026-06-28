import json
import os


SOURCE_FILE = "assets/dictionaries/vietnamese/Viet74K.txt"
CATEGORY_FILE = "assets/dictionaries/vietnamese/categories.json"


DEFAULT_CATEGORIES = [
    "animals",
    "body_parts",
    "colors",
    "foods",
    "drinks",
    "eating_verbs",
    "drinking_verbs",
    "cooking_methods",
    "objects",
    "materials",
    "people",
    "places",
    "descriptions",
    "skip"
]


def load_categories():
    if not os.path.exists(CATEGORY_FILE):
        return {cat: [] for cat in DEFAULT_CATEGORIES if cat != "skip"}

    with open(CATEGORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_categories(categories):
    os.makedirs(os.path.dirname(CATEGORY_FILE), exist_ok=True)

    clean_categories = {}

    for category, words in categories.items():
        clean_categories[category] = sorted(set(words))

    with open(CATEGORY_FILE, "w", encoding="utf-8") as file:
        json.dump(clean_categories, file, ensure_ascii=False, indent=2)


def load_words():
    words = []

    with open(SOURCE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            word = line.strip().lower()

            if not word:
                continue

            if "," in word or "(" in word or ")" in word:
                continue

            if len(word.split()) != 1:
                continue

            if "-" in word:
                continue

            if len(word) <= 1:
                continue

            words.append(word)

    return sorted(set(words))


def already_categorized(word, categories):
    for word_list in categories.values():
        if word in word_list:
            return True

    return False


def show_menu():
    print("\nChoose category:")

    for index, category in enumerate(DEFAULT_CATEGORIES, start=1):
        print(f"{index}. {category}")

    print("n. create new category")
    print("q. quit")


def main():
    categories = load_categories()
    words = load_words()

    print(f"Loaded {len(words)} candidate words.")
    print(f"Saving to {CATEGORY_FILE}")

    for word in words:
        if already_categorized(word, categories):
            continue

        print("\n-------------------------")
        print(f"Word: {word}")
        show_menu()

        choice = input("Your choice: ").strip().lower()

        if choice == "q":
            save_categories(categories)
            print("Saved. Goodbye.")
            return

        if choice == "n":
            new_category = input("New category name: ").strip().lower()

            if not new_category:
                continue

            if new_category not in categories:
                categories[new_category] = []

            categories[new_category].append(word)
            save_categories(categories)
            continue

        if not choice.isdigit():
            continue

        choice_number = int(choice)

        if choice_number < 1 or choice_number > len(DEFAULT_CATEGORIES):
            continue

        selected_category = DEFAULT_CATEGORIES[choice_number - 1]

        if selected_category == "skip":
            continue

        if selected_category not in categories:
            categories[selected_category] = []

        categories[selected_category].append(word)
        save_categories(categories)

    save_categories(categories)
    print("Finished all words.")


if __name__ == "__main__":
    main()