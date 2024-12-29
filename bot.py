import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1323029319160954941
MESSAGE_ID = 1323043964361900123

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

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

# Define the Vega URL for checking pairings
VEGA_URL = "https://redfrogdude.com/"

# Store the last set of pairings to avoid redundant notifications
last_pairings = ""

# Function to check for updates
async def check_for_updates():
    global last_pairings

    try:
        # Send a GET request to the page
        response = requests.get(VEGA_URL)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            h2_text = soup.find('h2').get_text(strip=True) if soup.find('h2') else ""
            h4_text = soup.find('h4').get_text(strip=True) if soup.find('h4') else ""

            intro_message = f"{h2_text} - {h4_text}" if h2_text and h4_text else "New round pairings are available:"

            pairings_section = soup.find_all('table', {'class': 'table'})

            if pairings_section:
                pairings = ""
                for table in pairings_section:
                    rows = table.find_all('tr')
                    for row in rows[1:]:
                        cols = row.find_all('td')
                        if len(cols) > 1:
                            board = cols[0].get_text(strip=True)
                            white = cols[2].get_text(strip=True)
                            black = cols[8].get_text(strip=True)
                            pairings += f"{board} **{white}** *vs* **{black}**\n"

                if pairings != last_pairings:
                    last_pairings = pairings
                    new_pairing_message = f":bangbang: **{intro_message}** <@&{CHAMPIONSHIP}> :bangbang:\n\n{pairings}"

                    channel = client.get_channel(int(CHANNEL_ID))
                    await channel.send(new_pairing_message)

    except Exception as e:
        print(f"Error fetching updates: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    while True:
        await check_for_updates()
        await asyncio.sleep(60)

@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(payload.guild_id)
    if guild:
        role_id = ROLE_EMOJI_MAPPING.get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)
                print(f"Assigned {role.name} to {member.name}")
            else:
                print(f"Role or member not found. Role: {role}, Member: {member}")

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(payload.guild_id)
    if guild:
        role_id = ROLE_EMOJI_MAPPING.get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)
                print(f"Removed {role.name} from {member.name}")
            else:
                print(f"Role or member not found. Role: {role}, Member: {member}")

client.run(TOKEN)