import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database.database import setup_database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Indestructible Word Chain Bot is online!")

async def load_cogs():
    await bot.load_extension("cogs.game")

@bot.event
async def setup_hook():
    setup_database()
    await load_cogs()
    await bot.tree.sync()

if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN was not found in your .env file.")
else:
    bot.run(TOKEN)