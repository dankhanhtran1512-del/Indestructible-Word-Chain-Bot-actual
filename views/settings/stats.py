import discord

from database.database import get_stats


class StatsSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="My Stats", style=discord.ButtonStyle.blurple, emoji="📊")
    async def my_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        stats = get_stats(interaction.user.id, interaction.user.display_name)

        await interaction.response.send_message(
            f"📊 **Stats for {interaction.user.display_name}**\n"
            f"💰 Score: **{stats['score']}**\n"
            f"✅ Correct words: **{stats['correct_words']}**\n"
            f"❌ Wrong words: **{stats['wrong_words']}**\n"
            f"🔁 Repeated words: **{stats['repeated_words']}**\n"
            f"💡 Hints used: **{stats['hints_used']}**",
            ephemeral=True
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from views.settings.main import SettingsView

        await interaction.response.edit_message(
            content="⚙️ **Word Chain Settings**\nChoose a category:",
            view=SettingsView()
        )