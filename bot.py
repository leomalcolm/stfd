import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import asyncio
import os

# Load environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Role IDs
CHAMPIONSHIP = 1322881877333508118
MAJOR_OPEN = 1323073564261351475
JUNIOR = 1323073745157623919
RAPID = 1323073911541465130
BLITZ = 1323074042550554735

ROLE_EMOJI_MAPPING = {
    "🏆": CHAMPIONSHIP,
    "🥇": MAJOR_OPEN,
    "👶": JUNIOR,
    "🔥": RAPID,
    "⚡": BLITZ
}

# Tournament-specific URLs
TOURNAMENT_URLS = {
    "CHAMPIONSHIP": "https://newzealandchess.co.nz/tournaments/ch/2025/CongressNZChampionship2025/wwwCongressNZChampionship2025/pairs3.html",
    "MAJOR_OPEN": "https://newzealandchess.co.nz/tournaments/ch/2025/CongressMajorOpen2025/wwwCongressMajorOpen2025/pairs3.html",
    "JUNIOR": "https://newzealandchess.co.nz/tournaments/ch/2025/CongressJunior2025/wwwCongressJunior2025/pairs1.html",
    "RAPID": "https://redfrogdude.com/",
    "BLITZ": "https://redfrogdude.com/"
}

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Store pairings in memory
last_pairings = {key: "" for key in TOURNAMENT_URLS}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Periodically check for updates
async def check_for_updates():
    while True:
        try:
            for tournament, url in TOURNAMENT_URLS.items():
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    pairings_section = soup.find_all('table', {'class': 'table'})

                    if pairings_section:
                        pairings = ""
                        for table in pairings_section:
                            rows = table.find_all('tr')
                            for row in rows[1:]:
                                cols = row.find_all('td')
                                if len(cols) > 1:
                                    board = cols[0].get_text(strip=True)
                                    white = cols[3].get_text(strip=True)
                                    black = cols[9].get_text(strip=True)
                                    pairings += f"{board} **{white}** *vs* **{black}**\n"

                        if pairings != last_pairings[tournament]:
                            last_pairings[tournament] = pairings
                            channel = bot.get_channel(CHAMPIONSHIP)  # Change to your desired channel
                            if channel:
                                await channel.send(f"New pairings for {tournament}:\n\n{pairings}")

        except Exception as e:
            print(f"Error during pairing update: {e}")

        await asyncio.sleep(60)

@bot.command(name="c")
async def championship(ctx):
    pairings = last_pairings.get("CHAMPIONSHIP", "No pairings available.")
    await ctx.send(f":chess_pawn: **Pairings for Championship** :chess_pawn:\n\n{pairings}")

@bot.command(name="m")
async def major_open(ctx):
    pairings = last_pairings.get("MAJOR_OPEN", "No pairings available.")
    await ctx.send(f":chess_pawn: **Pairings for Major Open** :chess_pawn:\n\n{pairings}")

@bot.command(name="j")
async def junior(ctx):
    pairings = last_pairings.get("JUNIOR", "No pairings available.")
    await ctx.send(f":chess_pawn: **Pairings for Junior** :chess_pawn:\n\n{pairings}")

@bot.command(name="r")
async def rapid(ctx):
    pairings = last_pairings.get("RAPID", "No pairings available.")
    await ctx.send(f":chess_pawn: **Pairings for Rapid** :chess_pawn:\n\n{pairings}")

@bot.command(name="b")
async def blitz(ctx):
    pairings = last_pairings.get("BLITZ", "No pairings available.")
    await ctx.send(f":chess_pawn: **Pairings for Blitz** :chess_pawn:\n\n{pairings}")

# Start update checker
bot.loop.create_task(check_for_updates())
bot.run(TOKEN)
