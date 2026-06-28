import discord

from database.database import get_server_settings, update_server_setting


GAME_LANGUAGE_LABELS = {
    "english": "English",
    "french": "French",
    "mixed_en_fr": "Mixed English + French",
    "vietnamese": "Vietnamese Nối Chữ",
}

BOT_LANGUAGE_LABELS = {
    "english": "English",
    "vietnamese": "Tiếng Việt",
    "french": "Français",
}


class GameLanguageSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="English", value="english", emoji="🇺🇸"),
            discord.SelectOption(label="French", value="french", emoji="🇫🇷"),
            discord.SelectOption(label="Mixed English + French", value="mixed_en_fr", emoji="🌍"),
            discord.SelectOption(label="Vietnamese Nối Chữ", value="vietnamese", emoji="🇻🇳"),
        ]

        super().__init__(
            placeholder="Choose default game language",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]

        update_server_setting(
            interaction.guild.id,
            "game_language",
            selected
        )

        await interaction.response.edit_message(
            content=(
                "🎮 **Game Language Updated**\n"
                f"Default game language is now: **{GAME_LANGUAGE_LABELS[selected]}**"
            ),
            view=LanguageSettingsView()
        )


class BotLanguageSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="English", value="english", emoji="🇺🇸"),
            discord.SelectOption(label="Tiếng Việt", value="vietnamese", emoji="🇻🇳"),
            discord.SelectOption(label="Français", value="french", emoji="🇫🇷"),
        ]

        super().__init__(
            placeholder="Choose bot interface language",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]

        update_server_setting(
            interaction.guild.id,
            "bot_language",
            selected
        )

        if selected == "vietnamese":
            content = (
                "🤖 **Đã cập nhật ngôn ngữ bot**\n"
                "Ngôn ngữ giao diện bot hiện tại: **Tiếng Việt**"
            )
        elif selected == "french":
            content = (
                "🤖 **Langue du bot mise à jour**\n"
                "La langue actuelle du bot est: **Français**"
            )
        else:
            content = (
                "🤖 **Bot Language Updated**\n"
                "Current bot interface language: **English**"
            )

        await interaction.response.edit_message(
            content=content,
            view=LanguageSettingsView()
        )


class GameLanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(GameLanguageSelect())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="🌍 **Language Settings**",
            view=LanguageSettingsView()
        )


class BotLanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(BotLanguageSelect())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="🌍 **Language Settings**",
            view=LanguageSettingsView()
        )


class LanguageSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Game Language", style=discord.ButtonStyle.blurple, emoji="🎮")
    async def game_language(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = get_server_settings(interaction.guild.id)
        current = settings["game_language"]

        await interaction.response.edit_message(
            content=(
                "🎮 **Game Language Settings**\n"
                f"Current default game language: **{GAME_LANGUAGE_LABELS.get(current, current)}**\n"
                "Choose a new default game language below."
            ),
            view=GameLanguageView()
        )

    @discord.ui.button(label="Bot Language", style=discord.ButtonStyle.blurple, emoji="🤖")
    async def bot_language(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = get_server_settings(interaction.guild.id)
        current = settings["bot_language"]

        await interaction.response.edit_message(
            content=(
                "🤖 **Bot Language Settings**\n"
                f"Current bot interface language: **{BOT_LANGUAGE_LABELS.get(current, current)}**\n"
                "Choose a new bot language below."
            ),
            view=BotLanguageView()
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from views.settings.main import SettingsView

        await interaction.response.edit_message(
            content="⚙️ **Word Chain Settings**\nChoose a category:",
            view=SettingsView()
        )