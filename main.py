#Import libraries
import os
import discord
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

# Loads your bot api token from the .env file, make sure to set it up:
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# --- YOU SHOULD CONFIGURE THIS PART --- #
# Here, you set the victims discord user_id, followed by the message you want to annoy them with.
# The user_id is fetched from the .env file, same as the DISCORD_TOKEN key. Make sure to set it up.
# Afterwards, you can adjust the following template, and add your annoyances.
user_replies = {
    int(os.getenv('USER_ID_1')): "Loser", 
    int(os.getenv('USER_ID_2')): "U Cutie",
    int(os.getenv('USER_ID_3')): "U Imbecile",
    int(os.getenv('USER_ID_4')): "Woah, a noob appears!",
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

    # Grabs sender's user ID and checks for a corresponding reply message.
    reply_message = user_replies.get(message.author.id)

    if reply_message:  # Check if a reply message exists for the user_id
        try:
            await message.reply({reply_message}) #Replies to the victim with annoyance :P
            print(f"Replied to {message.author.display_name} in {message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")


client.run(DISCORD_TOKEN)
