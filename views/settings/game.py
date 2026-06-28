import discord

from views.game.start_game import GameModeView, game_manager


class GameSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Start New Game", style=discord.ButtonStyle.green, emoji="▶️")
    async def start_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🎮 Choose a game mode:",
            view=GameModeView(),
            ephemeral=True
        )

    @discord.ui.button(label="End Current Game", style=discord.ButtonStyle.red, emoji="🛑")
    async def end_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel.id

        if not game_manager.end_game(channel_id):
            await interaction.response.send_message(
                "❌ No game is running in this channel.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🛑 Current game ended.",
            ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from views.settings.main import SettingsView

        await interaction.response.edit_message(
            content="⚙️ **Word Chain Settings**\nChoose a category:",
            view=SettingsView()
        )