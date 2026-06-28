import discord

from views.settings.game import GameSettingsView
from views.settings.language import LanguageSettingsView
from views.settings.players import PlayersSettingsView
from views.settings.stats import StatsSettingsView
from views.settings.announcements import AnnouncementsSettingsView


class SettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Game", style=discord.ButtonStyle.green, emoji="🎮")
    async def game(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="🎮 **Game Settings**",
            view=GameSettingsView()
        )

    @discord.ui.button(label="Languages", style=discord.ButtonStyle.blurple, emoji="🌍")
    async def languages(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="🌍 **Language Settings**",
            view=LanguageSettingsView()
        )

    @discord.ui.button(label="Players", style=discord.ButtonStyle.gray, emoji="👥")
    async def players(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="👥 **Player Settings**",
            view=PlayersSettingsView()
        )

    @discord.ui.button(label="Stats", style=discord.ButtonStyle.gray, emoji="📊")
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📊 **Statistics**",
            view=StatsSettingsView()
        )

    @discord.ui.button(label="Announcements", style=discord.ButtonStyle.gray, emoji="📢")
    async def announcements(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📢 **Announcement Settings**",
            view=AnnouncementsSettingsView()
        )