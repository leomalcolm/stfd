import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import os

# Your bot token and channel ID
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Define the Vega URL for checking pairings
VEGA_URL = "https://newzealandchess.co.nz/tournaments/misc/2024/www2024%20New%20Zealand%20Championship/pairs9.html"

# Store the last set of pairings to avoid redundant notifications
last_pairings = ""

# Function to check for updates
async def check_for_updates():
    global last_pairings
    
    try:
        # Send a GET request to the page
        response = requests.get(VEGA_URL)

        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the first <h2> and <h4> tags to use in the message
            h2_text = soup.find('h2').get_text(strip=True) if soup.find('h2') else ""
            h4_text = soup.find('h4').get_text(strip=True) if soup.find('h4') else ""

            # Combine the h2 and h4 texts for the message intro
            intro_message = f"{h2_text} - {h4_text}" if h2_text and h4_text else "New round pairings are available:"

            # Find the pairing data (adjust based on structure of the page)
            pairings_section = soup.find_all('table', {'class': 'table'})  # Adjust class if needed

            if pairings_section:
                # Extract the rows from the table
                pairings = ""
                for table in pairings_section:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header row
                        cols = row.find_all('td')
                        # Adjust column indexes if needed
                        if len(cols) > 1:
                            board = cols[0].get_text(strip=True)
                            white = cols[2].get_text(strip=True)
                            black = cols[8].get_text(strip=True)
                            pairings += f"{board} **{white}** *vs* **{black}**\n"

                # Check if the pairings have changed
                if pairings != last_pairings:
                    # If new pairings are detected, update the stored pairings and notify on Discord
                    last_pairings = pairings
                    new_pairing_message = f":bangbang: **{intro_message}** @championship :bangbang:\n\n{pairings}"

                    # Send the message to Discord
                    channel = client.get_channel(int(CHANNEL_ID))
                    await channel.send(new_pairing_message)

    except Exception as e:
        print(f"Error fetching updates: {e}")

# When the bot is ready, start checking for updates
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Check every 60 seconds (adjust as needed)
    while True:
        await check_for_updates()
        await asyncio.sleep(60)

# Run the bot
client.run(TOKEN)
