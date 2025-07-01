# main.py
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands # Import commands extension
from database import AnnoyanceDB # Import your database class

# Loads environment variables from .env file
load_dotenv()

# Loads your bot api token from the .env file, make sure to set it up:
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not set in the environment variables.")

# --- INITIALIZE DATABASE ---
db = AnnoyanceDB()
# --- YOU SHOULD CONFIGURE THIS PART --- #

# List of random messages to annoy the user with
random_messages = ["You dopehead", "Bad Boy", "Dingus"]

# List of emojis to react with
emojis = ["😂", "👍", "❤️", "🤔", "😁", "😆", "😅", "🤣", "😊", "😇", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"]


#Sets the intents for the bot, which are essentially permissions that the bot needs to function properly.
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True # Required for fetching members in commands (good practice for user mentions)

# Change from discord.Client to commands.Bot
# commands.Bot supports slash commands directly
bot = commands.Bot(command_prefix="!", intents=intents) # You can keep "!" as a prefix for old commands if you add any

# A global cache for user replies from the database to avoid excessive DB calls
user_replies_cache = {}

@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
    global user_replies_cache
    user_replies_cache = db.get_all_targets() # Load targets on startup
    print(f"Loaded initial targets from DB: {user_replies_cache}")
    
    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    # Grabs sender's user ID and checks for a corresponding reply message from cache.
    # We use .get() which returns None if the key is not found, preventing KeyError.
    user_specific_reply = user_replies_cache.get(message.author.id)

    #Switch between annoying with message or reaction
    message_or_reaction = random.choice(['message', 'reaction'])

    if user_specific_reply:
        try:
            if message_or_reaction == 'message':
                # Combines specific reply with random messages
                reply_message = random.choice(random_messages + [user_specific_reply])
                await message.channel.send(reply_message) #Annoys the victim with their specific or random messages
                print(f"Replied to {message.author.display_name} in {message.channel.name}")
            elif message_or_reaction == 'reaction':
                random_emoji = random.choice(emojis)
                await message.add_reaction(random_emoji) #Annoys the victim with a random emoji reaction LP
                print(f"Reacted to {message.author.display_name} in {message.channel.name}")
        except discord.Forbidden:
            print(f"Lacked permissions to reply or react in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    await bot.process_commands(message) # Important: process commands after on_message logic


# --- SLASH COMMANDS ---

# Command to set a user as a target
@bot.tree.command(name="settarget", description="Set a user to be annoyed.")
@discord.app_commands.describe(
    user="The user to annoy.",
    annoyance_message="The specific message to sometimes annoy them with."
)
async def settarget(interaction: discord.Interaction, user: discord.Member, annoyance_message: str):
    # Check if the command invoker has permissions (e.g., is an admin)
    # For now, let's allow anyone, but you should add permission checks later!
    # Example: if not interaction.user.guild_permissions.administrator:
    #             await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
    #             return

    success = db.add_target(user.id, annoyance_message)
    if success:
        # Update the local cache
        user_replies_cache[user.id] = annoyance_message
        await interaction.response.send_message(
            f"Successfully set {user.mention} as an annoyance target with message: '{annoyance_message}'"
        )
    else:
        await interaction.response.send_message(
            f"Failed to set {user.mention} as an annoyance target. Check bot logs for errors.",
            ephemeral=True
        )

# Command to remove a user from targets
@bot.tree.command(name="removetarget", description="Stop annoying a user.")
@discord.app_commands.describe(
    user="The user to stop annoying."
)
async def removetarget(interaction: discord.Interaction, user: discord.Member):
    # Add permission checks here too!
    success = db.remove_target(user.id)
    if success:
        # Remove from local cache
        if user.id in user_replies_cache:
            del user_replies_cache[user.id]
        await interaction.response.send_message(f"Successfully removed {user.mention} from annoyance targets.")
    else:
        await interaction.response.send_message(
            f"{user.mention} was not found in the annoyance targets.",
            ephemeral=True
        )

# Command to list current targets (optional but useful for debugging/checking)
@bot.tree.command(name="listtargets", description="List all users currently being annoyed.")
async def listtargets(interaction: discord.Interaction):
    targets = db.get_all_targets()
    if not targets:
        await interaction.response.send_message("No users are currently being annoyed.", ephemeral=True)
        return

    target_list_str = "Currently annoying the following users:\n"
    for user_id, message in targets.items():
        try:
            # Try to fetch the user by ID to get their name
            user = await bot.fetch_user(user_id)
            target_list_str += f"- **{user.display_name}** (`{user.id}`): \"{message}\"\n"
        except discord.NotFound:
            target_list_str += f"- Unknown User (`{user_id}`): \"{message}\" (User not found or left guild)\n"
        except Exception as e:
            target_list_str += f"- Error fetching user (`{user_id}`): {e}\n"

    await interaction.response.send_message(target_list_str, ephemeral=True)


bot.run(DISCORD_TOKEN) #Runs the bot with the provided token
