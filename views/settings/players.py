import discord

from database.database import get_leaderboard


class PlayersSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.blurple, emoji="🏆")
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        top = get_leaderboard()

        if not top:
            await interaction.response.send_message("🏆 No scores yet.", ephemeral=True)
            return

        lines = ["🏆 **Leaderboard**"]

        for i, (name, score) in enumerate(top, start=1):
            lines.append(f"**{i}.** {name} — **{score}** points")

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from views.settings.main import SettingsView

        await interaction.response.edit_message(
            content="⚙️ **Word Chain Settings**\nChoose a category:",
            view=SettingsView()
        )