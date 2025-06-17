import os
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Sepcify your targets Discord user ID (as an integer)
***REMOVED***_user_id = int(os.getenv('MY_USER_ID'))
***REMOVED***_user_id = int(os.getenv('***REMOVED***_USER_ID'))
***REMOVED***_user_id = int(os.getenv('***REMOVED***_USER_ID'))

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

    # Response if ***REMOVED*** messages
    if message.author.id == ***REMOVED***_user_id:
        try:
            await message.reply("U Maniac")
            print(f"Replied to {message.author.display_name} in #{message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Response if ***REMOVED*** messages
    if message.author.id == ***REMOVED***_user_id:
        try:
            await message.reply("U Imbecile")
            print(f"Replied to {message.author.display_name} in #{message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Response if ***REMOVED*** messages
    if message.author.id == ***REMOVED***_user_id:
        try:
            await message.reply("Cutie")
            print(f"Replied to {message.author.display_name} in #{message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

client.run(DISCORD_TOKEN)
