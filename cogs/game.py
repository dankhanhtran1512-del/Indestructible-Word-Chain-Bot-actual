import discord
from discord import app_commands
from discord.ext import commands, tasks

from managers.word_validator import WordValidator
from managers.vietnamese_ai import VietnameseAI
from database.database import (
    add_points,
    get_score,
    get_stats,
    get_leaderboard,
    get_server_settings,
)
from views.settings.main import SettingsView
from views.game.start_game import GameModeView, game_manager


def get_bot_language(guild_id):
    try:
        settings = get_server_settings(guild_id)
        return settings.get("bot_language", "english")
    except Exception:
        return "english"


class HintRejectView(discord.ui.View):
    def __init__(self, cog, user_id, game, current_hint, guild_id):
        super().__init__(timeout=120)
        self.cog = cog
        self.user_id = user_id
        self.game = game
        self.current_hint = current_hint
        self.guild_id = guild_id

    @discord.ui.button(label="Reject Hint", style=discord.ButtonStyle.red)
    async def reject_hint(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_bot_language(self.guild_id)

        if interaction.user.id != self.user_id:
            if lang == "vietnamese":
                text = "❌ Có mua đâu mà đòi từ chối."
            elif lang == "french":
                text = "❌ Seul le joueur qui a acheté cet indice peut le refuser."
            else:
                text = "❌ Only the player who bought this hint can reject it."

            await interaction.response.send_message(text, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        self.cog.vietnamese_ai.reject_hint(
            game=self.game,
            phrase=self.current_hint
        )

        new_hint = self.cog.vietnamese_ai.get_hint(self.game)

        if new_hint is None:
            if lang == "vietnamese":
                content = (
                    f"❌ Đã từ chối và lưu gợi ý **{self.current_hint}**.\n"
                    "Không tìm thấy gợi ý hợp lệ mới."
                )
            elif lang == "french":
                content = (
                    f"❌ L’indice **{self.current_hint}** a été refusé et enregistré.\n"
                    "Aucun nouvel indice valide n’a été trouvé."
                )
            else:
                content = (
                    f"❌ Hint **{self.current_hint}** was rejected and saved.\n"
                    "No new valid hint could be found."
                )

            await interaction.edit_original_response(content=content, view=None)
            return

        self.current_hint = new_hint

        if lang == "vietnamese":
            content = (
                "🔁 Gợi ý trước đã bị từ chối và lưu lại. Sau còn gợi ý từ không có thật thì hãy cứ nhấn reject nhé.\n"
                f"💡 Gợi ý miễn phí mới: **{new_hint}**"
            )
        elif lang == "french":
            content = (
                "🔁 L’indice précédent a été refusé et enregistré.\n"
                f"💡 Nouvel indice gratuit : **{new_hint}**"
            )
        else:
            content = (
                "🔁 Previous hint was rejected and saved.\n"
                f"💡 New free hint: **{new_hint}**"
            )

        await interaction.edit_original_response(content=content, view=self)


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.validator = WordValidator()
        self.validator.load_all()
        self.vietnamese_ai = VietnameseAI()
        self.daily_announcement.start()

    def lang(self, guild_id):
        return get_bot_language(guild_id)

    def translate_reason(self, lang, reason, required=None):
        if lang == "vietnamese":
            reasons = {
                "same_player": "Ai cho mà tự chơi mình vậy, rủ bạn chơi cùng đê.",
                "already_used": "Từ này đã nãy dùng rồi.",
                "game_not_running": "Trò chơi đã kết thúc.",
                "wrong_start": f"Từ phải bắt đầu bằng: {required}",
                "dictionary_invalid": "Từ này không có trong từ điển, nếu nó có nghĩa thật hãy liên hệ cho chủ bot để chỉnh sửa.",
                "word_accepted": "Từ được chấp nhận."
            }
        elif lang == "french":
            reasons = {
                "same_player": "Vous ne pouvez pas jouer deux fois de suite.",
                "already_used": "Ce mot a déjà été utilisé.",
                "game_not_running": "La partie est terminée.",
                "wrong_start": f"Le mot doit commencer par : {required}",
                "dictionary_invalid": "Ce mot n’est pas dans le dictionnaire sélectionné.",
                "word_accepted": "Mot accepté."
            }
        else:
            reasons = {
                "same_player": "You cannot play twice in a row.",
                "already_used": "This word has already been used.",
                "game_not_running": "Game is not running.",
                "wrong_start": f"Word must start with: {required}",
                "dictionary_invalid": "This word is not in the selected dictionary.",
                "word_accepted": "Word accepted."
            }

        return reasons.get(reason, reason)

    def text_startgame_prompt(self, lang):
        if lang == "vietnamese":
            return "🎮 Chọn chế độ chơi:"
        if lang == "french":
            return "🎮 Choisissez un mode de jeu :"
        return "🎮 Choose a game mode:"

    def text_settings_prompt(self, lang):
        if lang == "vietnamese":
            return "⚙️ **Cài đặt Nối Chữ**\nChọn một mục bên dưới:"
        if lang == "french":
            return "⚙️ **Paramètres du jeu**\nChoisissez une option ci-dessous :"
        return "⚙️ **Word Chain Settings**\nChoose an action below:"

    def text_no_game(self, lang):
        if lang == "vietnamese":
            return "❌ Hiện không có trò chơi nào trong kênh này."
        if lang == "french":
            return "❌ Aucun jeu n’est en cours dans ce salon."
        return "❌ No game is running in this channel."

    def text_game_ended(self, lang):
        if lang == "vietnamese":
            return "🛑 Trò nối chữ đã kết thúc."
        if lang == "french":
            return "🛑 Le jeu de mots en chaîne est terminé."
        return "🛑 Word Chain game ended."

    def format_score(self, lang, name, score):
        if lang == "vietnamese":
            return f"💰 **{name}**\nĐiểm hiện tại: **{score}**"
        if lang == "french":
            return f"💰 **{name}**\nScore actuel : **{score}**"
        return f"💰 **{name}**\nCurrent Score: **{score}**"

    def format_stats(self, lang, name, stats):
        if lang == "vietnamese":
            return (
                f"📊 **Thống kê của {name}**\n"
                f"💰 Điểm: **{stats['score']}**\n"
                f"✅ Từ đúng: **{stats['correct_words']}**\n"
                f"❌ Từ sai: **{stats['wrong_words']}**\n"
                f"🔁 Từ lặp lại: **{stats['repeated_words']}**\n"
                f"💡 Gợi ý đã dùng: **{stats['hints_used']}**"
            )
        if lang == "french":
            return (
                f"📊 **Statistiques de {name}**\n"
                f"💰 Score : **{stats['score']}**\n"
                f"✅ Mots corrects : **{stats['correct_words']}**\n"
                f"❌ Mots incorrects : **{stats['wrong_words']}**\n"
                f"🔁 Mots répétés : **{stats['repeated_words']}**\n"
                f"💡 Indices utilisés : **{stats['hints_used']}**"
            )
        return (
            f"📊 **Stats for {name}**\n"
            f"💰 Score: **{stats['score']}**\n"
            f"✅ Correct words: **{stats['correct_words']}**\n"
            f"❌ Wrong words: **{stats['wrong_words']}**\n"
            f"🔁 Repeated words: **{stats['repeated_words']}**\n"
            f"💡 Hints used: **{stats['hints_used']}**"
        )

    def format_leaderboard(self, lang, top_players):
        if not top_players:
            if lang == "vietnamese":
                return "🏆 Chưa có điểm nào."
            if lang == "french":
                return "🏆 Aucun score pour le moment."
            return "🏆 No scores yet."

        if lang == "vietnamese":
            lines = ["🏆 **Bảng xếp hạng**"]
        elif lang == "french":
            lines = ["🏆 **Classement**"]
        else:
            lines = ["🏆 **Leaderboard**"]

        for index, (name, score) in enumerate(top_players, start=1):
            if lang == "vietnamese":
                lines.append(f"**{index}.** {name} — **{score}** điểm")
            elif lang == "french":
                lines.append(f"**{index}.** {name} — **{score}** points")
            else:
                lines.append(f"**{index}.** {name} — **{score}** points")

        return "\n".join(lines)

    def format_hint_result(self, lang, hint_word, new_score):
        if lang == "vietnamese":
            return (
                f"💡 Đã xúc 1 gợi ý với giá **10 điểm**.\n"
                f"Gợi ý: **{hint_word}**\n"
                f"💰 Điểm mới: **{new_score}**"
            )
        if lang == "french":
            return (
                f"💡 Indice acheté pour **10 points**.\n"
                f"Mot suggéré : **{hint_word}**\n"
                f"💰 Nouveau score : **{new_score}**"
            )
        return (
            f"💡 Hint purchased for **10 points**.\n"
            f"Suggested word: **{hint_word}**\n"
            f"💰 New Score: **{new_score}**"
        )

    def format_accepted(self, lang, word, score, streak, required, milestone, is_vietnamese):
        next_text = required if is_vietnamese else required.upper()

        if lang == "vietnamese":
            response = (
                f"✅ Đã chấp nhận: **{word}**!\n"
                f"➕ **+5 điểm**\n"
                f"💰 Điểm: **{score}**\n"
                f"🔥 Chuỗi hiện tại: **{streak}**\n"
                f"➡️ Từ tiếp theo phải bắt đầu bằng: **{next_text}**"
            )

            if milestone:
                response += (
                    f"\n\n🎉 **MỐC CHUỖI MỚI!**\n"
                    f"Kênh này đã đạt **{streak}** từ đúng liên tiếp! Cố lên các cu nhang."
                )

            return response

        if lang == "french":
            response = (
                f"✅ **{word}** accepté !\n"
                f"➕ **+5 points**\n"
                f"💰 Score : **{score}**\n"
                f"🔥 Série actuelle : **{streak}**\n"
                f"➡️ Le prochain mot doit commencer par : **{next_text}**"
            )

            if milestone:
                response += (
                    f"\n\n🎉 **NOUVEAU PALIER !**\n"
                    f"Ce salon a atteint **{streak}** mots corrects d’affilée !"
                )

            return response

        response = (
            f"✅ **{word}** accepted!\n"
            f"➕ **+5 points**\n"
            f"💰 Score: **{score}**\n"
            f"🔥 Chain streak: **{streak}**\n"
            f"➡️ Next must start with: **{next_text}**"
        )

        if milestone:
            response += (
                f"\n\n🎉 **CHAIN MILESTONE!**\n"
                f"This channel reached **{streak}** correct words!"
            )

        return response

    def format_rejected(self, lang, word, reason, score, last_word, required, streak):
        if lang == "vietnamese":
            return (
                f"❌ **{word}** không được chấp nhận.\n"
                f"Lý do: {reason}\n"
                f"➖ **-3 điểm**\n"
                f"💰 Điểm: **{score}**\n"
                f"📖 Cụm cuối đã chấp nhận: **{last_word}**\n"
                f"➡️ Cần bắt đầu bằng: **{required}**\n"
                f"🔥 Chuỗi hiện tại: **{streak}**"
            )
        if lang == "french":
            return (
                f"❌ **{word}** n’est pas accepté.\n"
                f"Raison : {reason}\n"
                f"➖ **-3 points**\n"
                f"💰 Score : **{score}**\n"
                f"📖 Dernier mot accepté : **{last_word}**\n"
                f"➡️ Il faut commencer par : **{required}**\n"
                f"🔥 Série actuelle : **{streak}**"
            )
        return (
            f"❌ **{word}** is not allowed.\n"
            f"Reason: {reason}\n"
            f"➖ **-3 points**\n"
            f"💰 Score: **{score}**\n"
            f"📖 Last accepted phrase: **{last_word}**\n"
            f"➡️ Need: **{required}**\n"
            f"🔥 Chain streak: **{streak}**"
        )

    def format_repeat(self, lang, word, score, last_word, required, streak):
        if lang == "vietnamese":
            return (
                f"❌ **{word}** đã được dùng rồi.\n"
                f"➖ **-3 điểm**\n"
                f"💰 Điểm: **{score}**\n"
                f"📖 Cụm cuối đã chấp nhận: **{last_word}**\n"
                f"➡️ Cần bắt đầu bằng: **{required}**\n"
                f"🔥 Chuỗi hiện tại: **{streak}**"
            )
        if lang == "french":
            return (
                f"❌ **{word}** a déjà été utilisé.\n"
                f"➖ **-3 points**\n"
                f"💰 Score : **{score}**\n"
                f"📖 Dernier mot accepté : **{last_word}**\n"
                f"➡️ Il faut commencer par : **{required}**\n"
                f"🔥 Série actuelle : **{streak}**"
            )
        return (
            f"❌ **{word}** has already been used.\n"
            f"➖ **-3 points**\n"
            f"💰 Score: **{score}**\n"
            f"📖 Last accepted phrase: **{last_word}**\n"
            f"➡️ Need: **{required}**\n"
            f"🔥 Chain streak: **{streak}**"
        )

    def format_dead_end(self, lang, streak):
        if lang == "vietnamese":
            return (
                f"\n\n🏁 **Chuỗi đã kết thúc!**\n"
                f"Không tìm thấy cụm nối tiếp chưa dùng.\n"
                f"Chuỗi cuối cùng: **{streak}**"
            )
        if lang == "french":
            return (
                f"\n\n🏁 **Chaîne terminée !**\n"
                f"Aucune continuation inutilisée n’a été trouvée.\n"
                f"Série finale : **{streak}**"
            )
        return (
            f"\n\n🏁 **Chain ended!**\n"
            f"No known unused continuation was found.\n"
            f"Final streak: **{streak}**"
        )

    @tasks.loop(minutes=1)
    async def daily_announcement(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))

        if now.hour == 0 and now.minute == 0:
            top_players = get_leaderboard(1)

            if not top_players:
                return

            name, score = top_players[0]

            for channel_id in game_manager.active_channel_ids():
                channel = self.bot.get_channel(channel_id)

                if channel:
                    lang = self.lang(channel.guild.id)

                    if lang == "vietnamese":
                        text = f"🏆 **Người đỉnh nhất hôm nay**\n🥇 {name} với **{score}** điểm!"
                    elif lang == "french":
                        text = f"🏆 **Gagnant du jour**\n🥇 {name} avec **{score}** points !"
                    else:
                        text = f"🏆 **Daily Winner**\n🥇 {name} with **{score}** points!"

                    await channel.send(text)

    @daily_announcement.before_loop
    async def before_daily_announcement(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="startgame", description="Start a word chain game.")
    async def startgame(self, interaction: discord.Interaction):
        lang = self.lang(interaction.guild.id)

        await interaction.response.send_message(
            self.text_startgame_prompt(lang),
            view=GameModeView()
        )

    @app_commands.command(name="endgame", description="End the word chain game in this channel.")
    async def endgame(self, interaction: discord.Interaction):
        lang = self.lang(interaction.guild.id)
        channel_id = interaction.channel.id

        if not game_manager.end_game(channel_id):
            await interaction.response.send_message(self.text_no_game(lang))
            return

        await interaction.response.send_message(self.text_game_ended(lang))

    @app_commands.command(name="score", description="Check your current score.")
    async def score(self, interaction: discord.Interaction):
        lang = self.lang(interaction.guild.id)
        score = get_score(interaction.user.id, interaction.user.display_name)

        await interaction.response.send_message(
            self.format_score(lang, interaction.user.display_name, score)
        )

    @app_commands.command(name="stats", description="Show your game stats.")
    async def stats(self, interaction: discord.Interaction):
        lang = self.lang(interaction.guild.id)
        stats = get_stats(interaction.user.id, interaction.user.display_name)

        await interaction.response.send_message(
            self.format_stats(lang, interaction.user.display_name, stats)
        )

    @app_commands.command(name="leaderboard", description="Show the top players.")
    async def leaderboard(self, interaction: discord.Interaction):
        lang = self.lang(interaction.guild.id)
        top_players = get_leaderboard()

        await interaction.response.send_message(
            self.format_leaderboard(lang, top_players)
        )

    @app_commands.command(name="settings", description="Open the bot settings panel.")
    async def settings(self, interaction: discord.Interaction):
        lang = self.lang(interaction.guild.id)

        await interaction.response.send_message(
            self.text_settings_prompt(lang),
            view=SettingsView(),
            ephemeral=True
        )

    @app_commands.command(name="hint", description="Buy a random hint for 10 points.")
    async def hint(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        lang = self.lang(interaction.guild.id)
        channel_id = interaction.channel.id
        game = game_manager.get_game(channel_id)

        if game is None:
            await interaction.followup.send(self.text_no_game(lang), ephemeral=True)
            return

        if not getattr(game, "running", True):
            if lang == "vietnamese":
                text = "❌ Bí rồi, bắt đầu trò chơi mới đê."
            elif lang == "french":
                text = "❌ Ce jeu est déjà terminé. Lancez une nouvelle partie pour continuer."
            else:
                text = "❌ This game has already ended. Start a new game to continue."

            await interaction.followup.send(text, ephemeral=True)
            return

        score = get_score(interaction.user.id, interaction.user.display_name)

        if score < 10:
            if lang == "vietnamese":
                text = f"❌ Nghèo quá **10 điểm** cũng không đủ để mua gợi ý.\nĐiểm hiện tại: **{score}**"
            elif lang == "french":
                text = f"❌ Il vous faut au moins **10 points** pour acheter un indice.\nScore actuel : **{score}**"
            else:
                text = f"❌ You need at least **10 points** to buy a hint.\nCurrent Score: **{score}**"

            await interaction.followup.send(text, ephemeral=True)
            return

        if game.required_text is None:
            if lang == "vietnamese":
                text = "❌ Từ đầu tiên cần gì gợi ý má."
            elif lang == "french":
                text = "❌ Aucun indice disponible. Le premier mot peut être n’importe quoi."
            else:
                text = "❌ No hint available yet. The first word can be anything."

            await interaction.followup.send(text, ephemeral=True)
            return

        if game.language == "vietnamese":
            hint_word = self.vietnamese_ai.get_hint(game)
        else:
            hint_word = None

            for _ in range(100):
                candidate = self.validator.random_word(game.languages, game.required_text)

                if candidate is None:
                    break

                if candidate not in game.used_words:
                    hint_word = candidate
                    break

        if hint_word is None:
            if lang == "vietnamese":
                text = "❌ Không tìm thấy gợi ý hợp lệ."
            elif lang == "french":
                text = "❌ Aucun indice valide inutilisé n’a été trouvé."
            else:
                text = "❌ No valid hint could be found."

            await interaction.followup.send(text, ephemeral=True)
            return

        new_score = add_points(
            interaction.user.id,
            interaction.user.display_name,
            -10,
            "hint"
        )

        view = None

        if game.language == "vietnamese":
            view = HintRejectView(
                cog=self,
                user_id=interaction.user.id,
                game=game,
                current_hint=hint_word,
                guild_id=interaction.guild.id
            )

        if view is None:
            await interaction.followup.send(
                self.format_hint_result(lang, hint_word, new_score),
                ephemeral=True
            )
        else:
            await interaction.followup.send(
        self.format_hint_result(lang, hint_word, new_score),
        view=view,
        ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        game = game_manager.get_game(channel_id)

        if game is None:
            return

        lang = self.lang(message.guild.id)
        word = message.content.lower().strip()

        if game.language == "vietnamese":
            if word in game.used_words:
                new_score = add_points(
                    message.author.id,
                    message.author.display_name,
                    -3,
                    "repeat"
                )

                await message.channel.send(
                    self.format_repeat(
                        lang,
                        word,
                        new_score,
                        game.current_word,
                        game.required_text,
                        game.chain_streak
                    )
                )
                return

            ai_result = self.vietnamese_ai.process_move(
                game=game,
                phrase=word
            )

            if not ai_result["accepted"]:
                new_score = add_points(
                    message.author.id,
                    message.author.display_name,
                    -3,
                    "wrong"
                )

                await message.channel.send(
                    self.format_rejected(
                        lang,
                        word,
                        ai_result["reason"],
                        new_score,
                        game.current_word,
                        game.required_text,
                        game.chain_streak
                    )
                )
                return

        elif game.language in ["english", "french"]:
            if not self.validator.is_valid(word, game.languages):
                new_score = add_points(
                    message.author.id,
                    message.author.display_name,
                    -3,
                    "wrong"
                )

                await message.channel.send(
                    self.format_rejected(
                        lang,
                        word,
                        self.translate_reason(lang, "dictionary_invalid", game.required_text),
                        new_score,
                        game.current_word,
                        game.required_text,
                        game.chain_streak
                    )
                )
                return

        result = game.play_word(
            player_id=message.author.id,
            player_name=message.author.display_name,
            word=word
        )

        if result["accepted"]:
            new_score = add_points(
                message.author.id,
                message.author.display_name,
                5,
                "correct"
            )

            response = self.format_accepted(
                lang=lang,
                word=word,
                score=new_score,
                streak=result["chain_streak"],
                required=result["required_text"],
                milestone=result["milestone"],
                is_vietnamese=(game.language == "vietnamese")
            )

            if game.language == "vietnamese":
                if self.vietnamese_ai.check_dead_end(game):
                    game.running = False
                    response += self.format_dead_end(lang, result["chain_streak"])

            await message.channel.send(response)

        else:
            event_type = "repeat" if result["reason"] == "already_used" else "wrong"

            new_score = add_points(
                message.author.id,
                message.author.display_name,
                -3,
                event_type
            )

            await message.channel.send(
                self.format_rejected(
                    lang,
                    word,
                    self.translate_reason(
                        lang,
                        result["reason"],
                        result.get("required_text")
                    ),
                    new_score,
                    result["last_word"],
                    result["required_text"],
                    result["chain_streak"]
                )
            )


async def setup(bot):
    await bot.add_cog(Game(bot))