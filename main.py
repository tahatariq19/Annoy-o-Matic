# main.py
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands # Import app_commands for Choices
from database import AnnoyanceDB

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
bot = commands.Bot(command_prefix="!", intents=intents)

# A global cache for all target user settings from the database
# Stores: {user_id: {"specific_reply": "...", "specific_reaction": "...", "annoy_methods": [], "message_mode": "..."}}
target_settings_cache = {}

@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
    global target_settings_cache
    target_settings_cache = db.get_all_targets() # Load all detailed targets on startup
    print(f"Loaded initial target settings from DB: {target_settings_cache}")

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

    # Get the target settings for the sender from cache
    user_settings = target_settings_cache.get(message.author.id)

    if user_settings:
        specific_reply = user_settings.get("specific_reply")
        specific_reaction = user_settings.get("specific_reaction")
        annoy_methods = user_settings.get("annoy_methods", ['message', 'reaction']) # Default to both
        message_mode = user_settings.get("message_mode", 'both') # Default to both

        # Filter available methods based on user settings and if a specific item exists
        available_methods = []
        if 'message' in annoy_methods and (specific_reply or message_mode != 'specific_only'): # Only message if there's a specific reply OR if random is allowed
            available_methods.append('message')
        if 'reaction' in annoy_methods and specific_reaction: # Only reaction if there's a specific reaction
             available_methods.append('reaction')
        elif 'reaction' in annoy_methods and not specific_reaction and specific_reaction is not None:
            # If specific_reaction is explicitly set to None, but reaction method is allowed, skip.
            # This handles cases where a user might remove a specific reaction but wants general reactions.
            # For simplicity, if specific_reaction is None, we assume no reaction annoyance for now.
            pass
        elif 'reaction' in annoy_methods and specific_reaction is None: # If specific reaction is none, but reaction is allowed, we can react with random emojis.
            available_methods.append('reaction')


        if not available_methods:
            print(f"No active annoyance methods for {message.author.display_name}")
            return # No methods to annoy with

        chosen_method = random.choice(available_methods)

        try:
            if chosen_method == 'message':
                reply_options = []
                if message_mode == 'specific_only' and specific_reply:
                    reply_options.append(specific_reply)
                elif message_mode == 'random_only':
                    reply_options.extend(random_messages)
                elif message_mode == 'both':
                    if specific_reply:
                        reply_options.append(specific_reply)
                    reply_options.extend(random_messages)

                if reply_options:
                    reply_message = random.choice(reply_options)
                    await message.channel.send(reply_message)
                    print(f"Replied to {message.author.display_name} in {message.channel.name} with message.")
                else:
                    print(f"No message options available for {message.author.display_name} with mode '{message_mode}'.")

            elif chosen_method == 'reaction':
                # Use specific reaction if available, otherwise a random one
                if specific_reaction:
                    await message.add_reaction(specific_reaction)
                    print(f"Reacted to {message.author.display_name} in {message.channel.name} with specific emoji.")
                else:
                    random_emoji = random.choice(emojis)
                    await message.add_reaction(random_emoji)
                    print(f"Reacted to {message.author.display_name} in {message.channel.name} with random emoji.")

        except discord.Forbidden:
            print(f"Lacked permissions to reply or react in {message.channel.name}")
        except Exception as e:
            print(f"An error occurred during annoyance: {e}")

    await bot.process_commands(message) # Important: process commands after on_message logic


# --- SLASH COMMANDS ---

# Command 1: Set a target
@bot.tree.command(name="settarget", description="Add a user to the annoyance list.")
@app_commands.describe(user="The user to add to the annoyance list.")
async def settarget(interaction: discord.Interaction, user: discord.Member):
    # Add permission checks here (e.g., administrator, specific role)
    # if not interaction.user.guild_permissions.administrator:
    #     await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
    #     return

    success = db.add_target(user.id)
    if success:
        # Load the default settings for the new user into cache
        target_settings_cache[user.id] = db.get_target_settings(user.id) # Re-fetch to get defaults
        await interaction.response.send_message(
            f"Successfully added {user.mention} to the annoyance list. "
            "Use `/setannoyancemessage`, `/setannoyancereaction`, `/setannoyancemethods`, "
            "and `/setmessagemode` to configure their annoyances."
        )
    elif db.get_target_settings(user.id): # Check if they already exist
         await interaction.response.send_message(
            f"{user.mention} is already an annoyance target. Use other commands to configure them.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"Failed to add {user.mention} as an annoyance target. Check bot logs for errors.",
            ephemeral=True
        )

# Command 2: Set specific annoyance message
@bot.tree.command(name="setannoyancemessage", description="Set a specific text message to annoy a user with.")
@app_commands.describe(
    user="The target user.",
    message="The specific message to annoy them with. Leave empty to clear."
)
async def setannoyancemessage(interaction: discord.Interaction, user: discord.Member, message: str = None):
    # Add permission checks
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target. Use `/settarget` first.", ephemeral=True)
        return

    success = db.update_specific_reply(user.id, message)
    if success:
        # Update cache
        target_settings_cache[user.id]['specific_reply'] = message
        if message:
            await interaction.response.send_message(f"Successfully set specific message for {user.mention}: '{message}'")
        else:
            await interaction.response.send_message(f"Successfully cleared specific message for {user.mention}.")
    else:
        await interaction.response.send_message(
            f"Failed to set specific message for {user.mention}. Check bot logs.", ephemeral=True
        )

# Command 3: Set specific annoyance reaction
@bot.tree.command(name="setannoyancereaction", description="Set a specific emoji reaction to annoy a user with.")
@app_commands.describe(
    user="The target user.",
    emoji="The specific emoji to react with. Leave empty to clear. (e.g., 😂)"
)
async def setannoyancereaction(interaction: discord.Interaction, user: discord.Member, emoji: str = None):
    # Add permission checks
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target. Use `/settarget` first.", ephemeral=True)
        return

    # Basic emoji validation (can be more robust)
    if emoji and not (len(emoji) == 1 and emoji in emojis) and not discord.utils.get(interaction.guild.emojis, name=emoji.strip(':')):
        await interaction.response.send_message("Please provide a single valid emoji.", ephemeral=True)
        return

    success = db.update_specific_reaction(user.id, emoji)
    if success:
        # Update cache
        target_settings_cache[user.id]['specific_reaction'] = emoji
        if emoji:
            await interaction.response.send_message(f"Successfully set specific reaction for {user.mention}: {emoji}")
        else:
            await interaction.response.send_message(f"Successfully cleared specific reaction for {user.mention}.")
    else:
        await interaction.response.send_message(
            f"Failed to set specific reaction for {user.mention}. Check bot logs.", ephemeral=True
        )


# Command 4: Configure annoyance methods (message, reaction, both)
@bot.tree.command(name="setannoyancemethods", description="Configure which annoyance methods to use for a user.")
@app_commands.describe(
    user="The target user.",
    messages="Whether to use text messages to annoy them.",
    reactions="Whether to use emoji reactions to annoy them."
)
async def setannoyancemethods(
    interaction: discord.Interaction,
    user: discord.Member,
    messages: bool,
    reactions: bool
):
    # Add permission checks
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target. Use `/settarget` first.", ephemeral=True)
        return

    methods_to_use = []
    if messages:
        methods_to_use.append('message')
    if reactions:
        methods_to_use.append('reaction')

    if not methods_to_use:
        await interaction.response.send_message("You must enable at least one annoyance method (messages or reactions).", ephemeral=True)
        return

    success = db.update_annoy_methods(user.id, methods_to_use)
    if success:
        # Update cache
        target_settings_cache[user.id]['annoy_methods'] = methods_to_use
        await interaction.response.send_message(
            f"Successfully set annoyance methods for {user.mention}: {', '.join(methods_to_use)}"
        )
    else:
        await interaction.response.send_message(
            f"Failed to update annoyance methods for {user.mention}. Check bot logs.", ephemeral=True
        )


# Command 5: Toggle message mode (specific, random, both)
@bot.tree.command(name="setmessagemode", description="Configure how text messages are chosen for a user.")
@app_commands.describe(
    user="The target user.",
    mode="Choose how messages are selected."
)
@app_commands.choices(mode=[
    app_commands.Choice(name="Specific Message Only", value="specific_only"),
    app_commands.Choice(name="Random Messages Only", value="random_only"),
    app_commands.Choice(name="Both Specific and Random", value="both"),
])
async def setmessagemode(interaction: discord.Interaction, user: discord.Member, mode: app_commands.Choice[str]):
    # Add permission checks
    if user.id not in target_settings_cache:
        await interaction.response.send_message(f"{user.mention} is not an annoyance target. Use `/settarget` first.", ephemeral=True)
        return

    success = db.update_message_mode(user.id, mode.value)
    if success:
        # Update cache
        target_settings_cache[user.id]['message_mode'] = mode.value
        await interaction.response.send_message(
            f"Successfully set message mode for {user.mention} to '{mode.name}'."
        )
    else:
        await interaction.response.send_message(
            f"Failed to update message mode for {user.mention}. Check bot logs.", ephemeral=True
        )

# Command to remove a user from targets (unchanged from previous version, just re-included)
@bot.tree.command(name="removetarget", description="Stop annoying a user.")
@app_commands.describe(user="The user to stop annoying.")
async def removetarget(interaction: discord.Interaction, user: discord.Member):
    # Add permission checks here too!
    success = db.remove_target(user.id)
    if success:
        # Remove from local cache
        if user.id in target_settings_cache:
            del target_settings_cache[user.id]
        await interaction.response.send_message(f"Successfully removed {user.mention} from annoyance targets.")
    else:
        await interaction.response.send_message(
            f"{user.mention} was not found in the annoyance targets.",
            ephemeral=True
        )

# Command to list current targets (updated to show more details)
@bot.tree.command(name="listtargets", description="List all users currently being annoyed and their settings.")
async def listtargets(interaction: discord.Interaction):
    targets_data = db.get_all_targets() # Get full data from DB
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

        target_list_str += (
            f"\n- **{user_name}** (`{user_id}`)\n"
            f"  - Specific Message: {settings['specific_reply'] or 'None'}\n"
            f"  - Specific Reaction: {settings['specific_reaction'] or 'None'}\n"
            f"  - Annoy Methods: {', '.join(settings['annoy_methods']) or 'None'}\n"
            f"  - Message Mode: {settings['message_mode']}\n"
        )
    # Ensure message doesn't exceed Discord's character limit (2000)
    if len(target_list_str) > 2000:
        target_list_str = target_list_str[:1900] + "\n... (truncated)"
    await interaction.response.send_message(target_list_str, ephemeral=True)


bot.run(DISCORD_TOKEN)
