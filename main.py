import os
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Replace 'YOUR_USER_ID' with your Discord user ID (as an integer)
YOUR_USER_ID = ***REMOVED***  # Example: 182746352918273645

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot is logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent infinite loops
    if message.author == client.user:
        return

    # Check if the message author is the specified user
    if message.author.id == YOUR_USER_ID:
        try:
            await message.reply("U Maniac")
            print(f"Replied to {message.author.display_name} in #{message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

client.run(DISCORD_TOKEN)
