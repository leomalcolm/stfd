import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1324489271348039763
MESSAGE_ID = 1324274216983593031

CHAMPIONSHIP = 1322881877333508118
MAJOR_OPEN = 1323073564261351475
JUNIOR = 1323073745157623919
RAPID = 1323073911541465130
BLITZ = 1323074042550554735

ROLE_EMOJI_MAPPING = {
    "🏆": CHAMPIONSHIP,
    "🥇": MAJOR_OPEN,
    "👶": JUNIOR
}

# Tournament-specific URLs
TOURNAMENT_URLS = {
    "CHAMPIONSHIP": "https://newzealandchess.co.nz/tournaments/ch/2025/CongressNZChampionship2025/wwwCongressNZChampionship2025/pairs3.html",
    "MAJOR_OPEN": "https://newzealandchess.co.nz/tournaments/ch/2025/CongressMajorOpen2025/wwwCongressMajorOpen2025/pairs3.html",
    "JUNIOR": "https://newzealandchess.co.nz/tournaments/ch/2025/CongressJunior2025/wwwCongressJunior2025/pairs1.html"
}

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

# Store pairings in variables (initial load)
last_pairings = {
    "CHAMPIONSHIP": "",
    "MAJOR_OPEN": "",
    "JUNIOR": ""
}

# Flag to indicate if it's the first check after startup
is_first_check = True

async def check_for_updates():
    global last_pairings, is_first_check

    try:
        # Iterate over each tournament and check for updates
        for tournament, url in TOURNAMENT_URLS.items():
            response = requests.get(url)

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
                                white = cols[3].get_text(strip=True)
                                black = cols[9].get_text(strip=True)
                                pairings += f"{board} **{white}** *vs* **{black}**\n"

                    if pairings != last_pairings[tournament]:
                        last_pairings[tournament] = pairings  # Update pairings for the tournament

                        # Prepare the full message
                        new_pairing_message = f":bangbang: **{intro_message}** :bangbang:\n\n{pairings}"
                        
                        # Send the message to the same channel
                        channel = client.get_channel(int(CHANNEL_ID))
                        
                        # Check message length and split if necessary
                        if len(new_pairing_message) > 2000:
                            chunks = [new_pairing_message[i:i+2000] for i in range(0, len(new_pairing_message), 2000)]
                            for chunk in chunks:
                                await channel.send(chunk)
                        else:
                            await channel.send(new_pairing_message)


                # Set flag to False after the first check to allow message sending
                if is_first_check:
                    is_first_check = False

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