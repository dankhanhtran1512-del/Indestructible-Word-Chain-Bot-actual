import json
import os
from datetime import datetime


APPROVED_CACHE_FILE = "assets/dictionaries/vietnamese/approved_cache.json"
REJECTED_CACHE_FILE = "assets/dictionaries/vietnamese/rejected_cache.json"


class CacheManager:
    def __init__(self):
        self.approved_cache = self.load_json(APPROVED_CACHE_FILE)
        self.rejected_cache = self.load_json(REJECTED_CACHE_FILE)

    def load_json(self, file_path):
        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_json(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def save_all(self):
        self.save_json(APPROVED_CACHE_FILE, self.approved_cache)
        self.save_json(REJECTED_CACHE_FILE, self.rejected_cache)

    def is_approved(self, phrase):
        phrase = phrase.lower().strip()
        return phrase in self.approved_cache

    def is_rejected(self, phrase):
        phrase = phrase.lower().strip()
        return phrase in self.rejected_cache

    def get_approved(self, phrase):
        phrase = phrase.lower().strip()
        return self.approved_cache.get(phrase)

    def get_rejected(self, phrase):
        phrase = phrase.lower().strip()
        return self.rejected_cache.get(phrase)

    def approve(self, phrase, reason="Approved manually.", source="manual", confidence=1.0):
        phrase = phrase.lower().strip()

        self.rejected_cache.pop(phrase, None)

        self.approved_cache[phrase] = {
            "valid": True,
            "reason": reason,
            "source": source,
            "confidence": confidence,
            "checked_at": datetime.now().isoformat(timespec="seconds")
        }

        self.save_all()

    def reject(self, phrase, reason="Rejected manually.", source="manual", confidence=1.0):
        phrase = phrase.lower().strip()

        self.approved_cache.pop(phrase, None)

        self.rejected_cache[phrase] = {
            "valid": False,
            "reason": reason,
            "source": source,
            "confidence": confidence,
            "checked_at": datetime.now().isoformat(timespec="seconds")
        }

        self.save_all()

    def get_result(self, phrase):
        phrase = phrase.lower().strip()

        if phrase in self.approved_cache:
            return self.approved_cache[phrase]

        if phrase in self.rejected_cache:
            return self.rejected_cache[phrase]

        return None


if __name__ == "__main__":
    cache = CacheManager()

    cache.approve("mũi heo", "Test approved phrase.")
    cache.reject("heo mũi", "Test rejected phrase.")

    print(cache.get_result("mũi heo"))
    print(cache.get_result("heo mũi"))