import os
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Define your user IDs and their corresponding replies
# Fetching environment variables directly into the dictionary
user_replies = {
    int(os.getenv('USER_ID_1')): "Cutie", 
    int(os.getenv('USER_ID_2')): "U Maniac",
    int(os.getenv('USER_ID_3')): "U Imbecile",
    int(os.getenv('USER_ID_4')): "King Man",
}

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

    reply_message = user_replies.get(message.author.id)

    if reply_message:  # Check if a reply message exists for the author
        try:
            await message.reply(reply_message)
            print(f"Replied to {message.author.display_name} in #{message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

client.run(DISCORD_TOKEN)
