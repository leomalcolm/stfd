import discord
from discord.ext import commands
import os

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot is ready and sends a message
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    
    # Get the channel you want to send the message to (use the channel ID)
    channel_id = 123456789012345678  # Replace this with your actual channel ID
    channel = bot.get_channel(channel_id)
    
    # Send a message to the channel
    if channel:
        await channel.send("Hello! I'm online and ready to go!")
    else:
        print("Couldn't find the channel to send the message!")

# Command: Ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Run the bot
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
