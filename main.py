#Import libraries
import os
import discord
import random
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

# Loads your bot api token from the .env file, make sure to set it up:
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not set in the environment variables.")

# --- YOU SHOULD CONFIGURE THIS PART --- #
# Here, you set the victims discord user_id, followed by the message you want to annoy them with.
# The user_id is fetched from the .env file, same as the DISCORD_TOKEN key. Make sure to set it up.
# Afterwards, you can adjust the following template, and add your annoyances.
user_replies = {}
user_id_1 = os.getenv('USER_ID_1')
user_id_2 = os.getenv('USER_ID_2')

if user_id_1 is not None:
    user_replies[int(user_id_1)] = "Unfunny"
if user_id_2 is not None:
    user_replies[int(user_id_2)] = "Woah, a noob appears!"

# List of random messages to annoy the user with
random_messages = ["You dopehead", "Bad Boy", "Dingus"]

# List of emojis to react with
emojis = ["😂", "👍", "❤️", "🤔", "😁", "😆", "😅", "🤣", "😊", "😇", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"]


#Sets the intents for the bot, which are essentially permissions that the bot needs to function properly.
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot is logged in as {client.user}')

@client.event
async def on_message(message):
    # Grabs sender's user ID and checks for a corresponding reply message.
    user_specific_reply = user_replies.get(message.author.id)

    #Switch between annoying with message or reaction
    message_or_reaction = random.choice(['message', 'reaction'])

    if user_specific_reply: 
        try:
            if message_or_reaction == 'message':
                reply_message = random.choice(random_messages + [user_specific_reply])
                await message.channel.send(reply_message) #Annoys the victim with their specific or random messages
                print(f"Replied to {message.author.display_name} in {message.channel.name}")
            elif message_or_reaction == 'reaction':
                random_emoji = random.choice(emojis)
                await message.add_reaction(random_emoji) #Annoys the victim with a random emoji reaction LP
                print(f"Reacted to {message.author.display_name} in {message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

client.run(DISCORD_TOKEN)  #Runs the bot with the provided token