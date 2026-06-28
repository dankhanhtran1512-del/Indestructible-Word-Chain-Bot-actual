import re


VIETNAMESE_PATTERN = re.compile(
    r"^[a-zA-Zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễ"
    r"ìíịỉĩòóọỏõôồốộổỗơờớợởỡ"
    r"ùúụủũưừứựửữỳýỵỷỹđ"
    r"ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄ"
    r"ÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ"
    r"ÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s]+$"
)


COMMON_ENGLISH_WORDS = {
    "hello", "hi", "bye", "ok", "yes", "no", "apple", "banana",
    "cat", "dog", "car", "phone", "computer", "game", "love"
}


BLOCKED_WORDS = {
    "lol", "haha", "hihi", "hehe", "wtf", "omg", "idk", "brb",
    "cpu", "ram", "usb", "html", "http", "https", "www"
}


class VietnameseRules:
    def validate(self, phrase, previous_phrase=None):
        phrase = phrase.lower().strip()

        if not phrase:
            return {
                "valid": False,
                "reason": "Phrase cannot be empty."
            }

        parts = phrase.split()

        if len(parts) != 2:
            return {
                "valid": False,
                "reason": "Vietnamese nối chữ phrase must have exactly two words."
            }

        first_word = parts[0]
        second_word = parts[1]

        if first_word == second_word:
            return {
                "valid": False,
                "reason": "Phrase cannot repeat the same word twice."
            }

        if any(char.isdigit() for char in phrase):
            return {
                "valid": False,
                "reason": "Phrase cannot contain numbers."
            }

        if not VIETNAMESE_PATTERN.match(phrase):
            return {
                "valid": False,
                "reason": "Phrase can only contain Vietnamese letters and spaces."
            }

        if first_word in COMMON_ENGLISH_WORDS or second_word in COMMON_ENGLISH_WORDS:
            return {
                "valid": False,
                "reason": "Phrase cannot contain common English words."
            }

        if first_word in BLOCKED_WORDS or second_word in BLOCKED_WORDS:
            return {
                "valid": False,
                "reason": "Phrase contains blocked slang or abbreviation."
            }

        if previous_phrase:
            previous_parts = previous_phrase.lower().strip().split()

            if len(previous_parts) == 2:
                previous_first = previous_parts[0]
                previous_second = previous_parts[1]

                if first_word != previous_second:
                    return {
                        "valid": False,
                        "reason": f"Phrase must start with: {previous_second}"
                    }

                if second_word == previous_first:
                    return {
                        "valid": False,
                        "reason": "Cannot reverse the previous phrase."
                    }

                if second_word == previous_second:
                    return {
                        "valid": False,
                        "reason": "Cannot repeat the required word twice."
                    }

        return {
            "valid": True,
            "reason": "Passed local Vietnamese rules."
        }


if __name__ == "__main__":
    rules = VietnameseRules()

    tests = [
        ("lâu dài", None),
        ("dài lâu", "lâu dài"),
        ("dài dài", "lâu dài"),
        ("dài hạn", "lâu dài"),
        ("mũi heo", None),
        ("hello bạn", None),
        ("mèo 123", None),
        ("mèo!", None),
    ]

    for phrase, previous in tests:
        print(phrase, "=>", rules.validate(phrase, previous))