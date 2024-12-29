import discord
from discord.ext import commands
import os

# Set up intents (Make sure to enable 'Message Content Intent' in the Developer Portal)
intents = discord.Intents.default()
intents.message_content = True  # This line enables reading message content

# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot is ready and sends a message
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    
    # Get the channel you want to send the message to (use the channel ID)
    channel_id = 1185784461674151950
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
