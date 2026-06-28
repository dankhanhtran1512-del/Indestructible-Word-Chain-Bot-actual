import discord

from database.database import get_server_settings


class AnnouncementsSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Daily Winner", style=discord.ButtonStyle.blurple, emoji="📅")
    async def daily_winner(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = get_server_settings(interaction.guild.id)

        await interaction.response.send_message(
            f"📅 Daily winner announcements are planned for **{settings['daily_announcement_time']}** "
            f"({settings['timezone']}).",
            ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from views.settings.main import SettingsView

        await interaction.response.edit_message(
            content="⚙️ **Word Chain Settings**\nChoose a category:",
            view=SettingsView()
        )