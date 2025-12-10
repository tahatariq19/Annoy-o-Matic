# main.py
import os
import discord
import random
import regex as re
import csv
import logging
import asyncio
from io import StringIO
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from database import AnnoyanceDB

# --- LOGGING CONFIGURATION --- #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Loads environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not set in the environment variables.")

TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')

# --- INITIALIZE DATABASE --- #
# Initialize the class, but connect() must be called in an async context
db = AnnoyanceDB()

# List of random messages to annoy the user with
random_messages = ["You dopehead", "Bad Boy", "Dingus", "Still here?", "Annoyed yet?"]

# List of emojis to react with
emojis = ["😂", "👍", "❤️", "🤔", "😁", "😆", "😅", "🤣", "😊", "😇", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"]

# Sets the intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

target_settings_cache = {}

@bot.event
async def on_ready():
    logger.info(f'Bot is logged in as {bot.user}')
    
    # Connect to the database asynchronously
    await db.connect()
    
    global target_settings_cache
    target_settings_cache = await db.get_all_targets()
    logger.info(f"Loaded initial target settings from DB: {len(target_settings_cache)} targets.")

    try:
        if TEST_GUILD_ID:
            guild = discord.Object(id=int(TEST_GUILD_ID))
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"Synced {len(synced)} guild command(s) to guild {TEST_GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} global command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check cache first (fast)
    user_settings = target_settings_cache.get(message.author.id)

    if user_settings:
        specific_replies = user_settings.get("specific_reply", [])
        specific_reactions = user_settings.get("specific_reaction", [])
        annoy_methods = user_settings.get("annoy_methods", ['message', 'reaction'])
        message_mode = user_settings.get("message_mode", 'both')

        available_methods = []
        if 'message' in annoy_methods:
            if (message_mode == 'specific_only' and specific_replies) or \
               (message_mode == 'random_only') or \
               (message_mode == 'both'):
                available_methods.append('message')

        if 'reaction' in annoy_methods:
            if specific_reactions or emojis:
                available_methods.append('reaction')

        if not available_methods:
            logger.debug(f"No active annoyance methods for {message.author.display_name}")
            return

        chosen_method = random.choice(available_methods)

        try:
            if chosen_method == 'message':
                reply_options = []
                if message_mode == 'specific_only':
                    if specific_replies:
                        reply_options.extend(specific_replies)
                elif message_mode == 'random_only':
                    reply_options.extend(random_messages)
                elif message_mode == 'both':
                    if specific_replies:
                        reply_options.extend(specific_replies)
                    reply_options.extend(random_messages)

                if reply_options:
                    reply_message = random.choice(reply_options)
                    await message.reply(reply_message)
                    logger.info(f"Replied to {message.author.display_name} in {message.channel}")
                else:
                    logger.warning(f"No message options available for {message.author.display_name}")

            elif chosen_method == 'reaction':
                if specific_reactions:
                    chosen_emoji = random.choice(specific_reactions)
                    await message.add_reaction(chosen_emoji)
                    logger.info(f"Reacted to {message.author.display_name} in {message.channel} with specific emoji.")
                else:
                    random_emoji = random.choice(emojis)
                    await message.add_reaction(random_emoji)
                    logger.info(f"Reacted to {message.author.display_name} in {message.channel} with random emoji.")

        except discord.Forbidden:
            logger.warning(f"Lacked permissions to reply or react in {message.channel}")
        except Exception as e:
            logger.error(f"An error occurred during annoyance: {e}")

    await bot.process_commands(message)


# Define MY_GUILD for guild-specific commands if TEST_GUILD_ID is set
if TEST_GUILD_ID:
    MY_GUILD = discord.Object(id=int(TEST_GUILD_ID))
else:
    MY_GUILD = None 

# Utility function to parse emojis
def parse_emojis(text: str):
    emojis = []
    emoji_pattern = re.compile(r'<a?:[a-zA-Z0-9_]+:[0-9]+>|\p{Emoji}', re.UNICODE)
    parts = [part.strip() for part in text.split(',')]
    for part in parts:
        found_emojis = emoji_pattern.findall(part)
        emojis.extend(found_emojis)
    return emojis


# --- SLASH COMMANDS --- #

@bot.tree.command(name="settarget", description="Add a user to the annoyance list.", guild=MY_GUILD if MY_GUILD else None)
@app_commands.describe(user="The user to add to the annoyance list.")
async def settarget(interaction: discord.Interaction, user: discord.Member):
    if user.id in target_settings_cache:
        await interaction.response.send_message(
            f"{user.mention} is already an annoyance target. Use other commands to configure them.",
            ephemeral=True
        )
        return

    # Call async DB method
    is_newly_added = await db.add_target(user.id)
    if is_newly_added:
        settings = await db.get_target_settings(user.id)
        if settings:
            target_settings_cache[user.id] = settings
            await interaction.response.send_message(
                f"Successfully added {user.mention} to the annoyance list."
            )
        else:
            await interaction.response.send_message(
                f"Failed to add {user.mention}. Could not retrieve settings.",
                ephemeral=True
            )
    else:
        # Fallback if already in DB but not cache
        settings = await db.get_target_settings(user.id)
        if settings:
            target_settings_cache[user.id] = settings
            await interaction.response.send_message(f"{user.mention} is already an annoyance target.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Failed to add {user.mention}.", ephemeral=True)

@bot.tree.command(name="setannoyancemessage", description="Set specific annoyance messages for a user.")
@app_commands.describe(user="The target user.", messages="Semicolon-separated or quoted messages.")
async def setannoyancemessage(interaction: discord.Interaction, user: discord.Member, messages: str = ""):
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target.", ephemeral=True)
        return

    message_list = []
    if messages:
        try:
            reader = csv.reader(StringIO(messages), delimiter=';', skipinitialspace=True)
            message_list = [m.strip() for m in next(reader) if m.strip()]
        except Exception:
            message_list = [m.strip() for m in messages.split(';') if m.strip()]

    # Async update
    success = await db.update_specific_reply(user.id, message_list)
    if success:
        target_settings_cache[user.id]['specific_reply'] = message_list
        if message_list:
            formatted_list = "\n".join(f"- '{m}'" for m in message_list)
            await interaction.response.send_message(f"Successfully set specific messages for {user.mention}:\n>>> {formatted_list}")
        else:
            await interaction.response.send_message(f"Successfully cleared specific messages for {user.mention}.")
    else:
        await interaction.response.send_message("Failed to set specific messages.", ephemeral=True)

@bot.tree.command(name="setannoyancereaction", description="Set one or more specific emoji reactions.")
@app_commands.describe(user="The target user.", emojis_input="Comma-separated list of emojis.")
async def setannoyancereaction(interaction: discord.Interaction, user: discord.Member, emojis_input: str = ""):
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target.", ephemeral=True)
        return

    emoji_list = []
    if emojis_input:
        parsed_emojis = parse_emojis(emojis_input)
        if not parsed_emojis:
            await interaction.response.send_message("No valid emojis found.", ephemeral=True)
            return
        emoji_list = parsed_emojis

    # Async update
    success = await db.update_specific_reaction(user.id, emoji_list)
    if success:
        target_settings_cache[user.id]['specific_reaction'] = emoji_list
        if emoji_list:
            await interaction.response.send_message(f"Successfully set specific reactions for {user.mention}:\n>>> {', '.join(emoji_list)}")
        else:
            await interaction.response.send_message(f"Successfully cleared specific reactions for {user.mention}.")
    else:
        await interaction.response.send_message("Failed to set specific reactions.", ephemeral=True)

@bot.tree.command(name="setannoyancemethods", description="Configure annoyance methods.", guild=MY_GUILD if MY_GUILD else None)
async def setannoyancemethods(interaction: discord.Interaction, user: discord.Member, messages: bool, reactions: bool):
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target.", ephemeral=True)
        return

    methods_to_use = []
    if messages: methods_to_use.append('message')
    if reactions: methods_to_use.append('reaction')

    if not methods_to_use:
        await interaction.response.send_message("You must enable at least one annoyance method.", ephemeral=True)
        return

    # Async update
    success = await db.update_annoy_methods(user.id, methods_to_use)
    if success:
        target_settings_cache[user.id]['annoy_methods'] = methods_to_use
        await interaction.response.send_message(f"Successfully set annoyance methods for {user.mention}: {', '.join(methods_to_use)}")
    else:
        await interaction.response.send_message("Failed to update annoyance methods.", ephemeral=True)

@bot.tree.command(name="setmessagemode", description="Configure how text messages are chosen.", guild=MY_GUILD if MY_GUILD else None)
@app_commands.choices(mode=[
    app_commands.Choice(name="Specific Message(s) Only", value="specific_only"),
    app_commands.Choice(name="Random Messages Only", value="random_only"),
    app_commands.Choice(name="Both Specific and Random", value="both"),
])
async def setmessagemode(interaction: discord.Interaction, user: discord.Member, mode: app_commands.Choice[str]):
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target.", ephemeral=True)
        return

    # Async update
    success = await db.update_message_mode(user.id, mode.value)
    if success:
        target_settings_cache[user.id]['message_mode'] = mode.value
        await interaction.response.send_message(f"Successfully set message mode for {user.mention} to '{mode.name}'.")
    else:
        await interaction.response.send_message("Failed to update message mode.", ephemeral=True)

@bot.tree.command(name="removetarget", description="Stop annoying a user.", guild=MY_GUILD if MY_GUILD else None)
async def removetarget(interaction: discord.Interaction, user: discord.Member):
    # Async remove
    success = await db.remove_target(user.id)
    if success:
        if user.id in target_settings_cache:
            del target_settings_cache[user.id]
        await interaction.response.send_message(f"Successfully removed {user.mention} from annoyance targets.")
    else:
        await interaction.response.send_message(f"{user.mention} was not found in the annoyance targets.", ephemeral=True)

@bot.tree.command(name="listtargets", description="List all users currently being annoyed.", guild=MY_GUILD if MY_GUILD else None)
async def listtargets(interaction: discord.Interaction):
    # Async get all
    targets_data = await db.get_all_targets()
    if not targets_data:
        await interaction.response.send_message("No users are currently being annoyed.", ephemeral=True)
        return

    target_list_str = "Currently annoying the following users:\n"
    for user_id, settings in targets_data.items():
        try:
            user = await bot.fetch_user(user_id)
            user_name = user.display_name
        except discord.NotFound:
            user_name = f"Unknown User ({user_id})"

        specific_replies_str = ", ".join(f"'{m}'" for m in settings['specific_reply']) if settings['specific_reply'] else 'None'
        specific_reactions_str = ", ".join(settings['specific_reaction']) if settings['specific_reaction'] else 'None'

        target_list_str += (
            f"\n- **{user_name}** (`{user_id}`)\n"
            f"  - Specific Messages: {specific_replies_str}\n"
            f"  - Specific Reactions: {specific_reactions_str}\n"
            f"  - Annoy Methods: {', '.join(settings['annoy_methods']) or 'None'}\n"
            f"  - Message Mode: {settings['message_mode']}\n"
        )
    if len(target_list_str) > 2000:
        target_list_str = target_list_str[:1900] + "\n... (truncated)"
    await interaction.response.send_message(target_list_str, ephemeral=True)

@bot.event
async def on_shutdown():
    await db.close()

if __name__ == '__main__':
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start Discord bot: {e}")
