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

            # Find the pairing data (adjust based on structure of the page)
            # Assuming pairings are inside a <pre> tag, but you may need to inspect the page structure
            pairings_section = soup.find_all('table', {'class': 'table'})  # Adjust the class name if necessary

            if pairings_section:
                # Extract the rows from the table (adjust if table structure is different)
                pairings = ""
                for table in pairings_section:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header row
                        cols = row.find_all('td')
                        # Adjust column indexes if needed
                        if len(cols) > 1:
                            player1 = cols[0].get_text(strip=True)
                            player2 = cols[1].get_text(strip=True)
                            pairings += f"{player1} vs {player2}\n"

                # Check if the pairings have changed
                if pairings != last_pairings:
                    # If new pairings are detected, update the stored pairings and notify on Discord
                    last_pairings = pairings
                    new_pairing_message = "New round pairings are available:\n" + pairings

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
