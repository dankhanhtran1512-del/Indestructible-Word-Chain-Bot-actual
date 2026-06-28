import discord

from managers.game_manager import GameManager
from database.database import get_server_settings

game_manager = GameManager()


def t(guild_id, key):
    settings = get_server_settings(guild_id)
    lang = settings["bot_language"]

    texts = {
        "english": {
            "placeholder": "Choose game mode",
            "started": "🎮 Word Chain started in",
            "first": "First word can be anything.",
        },
        "vietnamese": {
            "placeholder": "Chọn ngôn ngữ chơi",
            "started": "🎮 Trò chơi nối chữ đã bắt đầu",
            "first": "Từ đầu tiên có thể là bất kỳ từ nào.",
        },
        "french": {
            "placeholder": "Choisissez le mode de jeu",
            "started": "🎮 Le jeu de mots en chaîne a commencé en",
            "first": "Le premier mot peut être n'importe quoi.",
        },
    }

    return texts.get(lang, texts["english"])[key]


class GameModeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="English", value="english", emoji="🇺🇸"),
            discord.SelectOption(label="French", value="french", emoji="🇫🇷"),
            discord.SelectOption(label="Mixed English + French", value="mixed_en_fr", emoji="🌍"),
            discord.SelectOption(label="Nối Chữ", value="vietnamese", emoji="🇻🇳"),
        ]

        super().__init__(
            placeholder="Choose game mode",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        channel_id = interaction.channel.id
        game_mode = self.values[0]

        if game_mode == "mixed_en_fr":
            game_manager.start_game(channel_id, ["english", "french"])
            display_name = "Mixed English + French"
        elif game_mode == "vietnamese":
            game_manager.start_game(channel_id, "vietnamese")
            display_name = "Nối Chữ"
        else:
            game_manager.start_game(channel_id, game_mode)
            display_name = game_mode.title()

        await interaction.response.edit_message(
            content=(
                f"{t(interaction.guild.id, 'started')} **{display_name}**!\n"
                f"{t(interaction.guild.id, 'first')}"
            ),
            view=None
        )


class GameModeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(GameModeSelect())