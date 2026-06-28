MESSAGES = {
    "english": {
        "choose_game_mode": "🎮 Choose the game mode:",
        "choose_display_language": "🌐 Choose the bot display language:",
        "game_started": "🎮 Word Chain started!",
        "first_word": "First word can be anything.",
        "word_accepted": "✅ Word accepted!",
        "invalid_move": "❌ Invalid move.",
        "last_word": "📖 Last accepted word:",
        "need": "➡️ Need:",
        "chain_streak": "🔥 Chain streak:",
    },

    "vietnamese": {
        "choose_game_mode": "🎮 Chọn chế độ chơi:",
        "choose_display_language": "🌐 Chọn ngôn ngữ hiển thị của bot:",
        "game_started": "🎮 Đã bắt đầu trò chơi!",
        "first_word": "Bạn có thể nhập bất kỳ từ nào để bắt đầu.",
        "word_accepted": "✅ Từ hợp lệ!",
        "invalid_move": "❌ Nước đi không hợp lệ.",
        "last_word": "📖 Từ hợp lệ gần nhất:",
        "need": "➡️ Cần bắt đầu bằng:",
        "chain_streak": "🔥 Độ dài chuỗi:",
    },

    "french": {
        "choose_game_mode": "🎮 Choisissez le mode de jeu :",
        "choose_display_language": "🌐 Choisissez la langue d’affichage du bot :",
        "game_started": "🎮 La partie commence !",
        "first_word": "Le premier mot peut être n’importe quoi.",
        "word_accepted": "✅ Mot accepté !",
        "invalid_move": "❌ Coup invalide.",
        "last_word": "📖 Dernier mot accepté :",
        "need": "➡️ Il faut commencer par :",
        "chain_streak": "🔥 Longueur de la chaîne :",
    }
}


def get_message(display_language, key):
    return MESSAGES.get(display_language, MESSAGES["english"]).get(key, key)