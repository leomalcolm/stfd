import discord
from discord.ext import commands
import os

# Set up intents (required for modern bots)
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# Command: Ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Run the bot
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
