import discord
from discord.ext import commands
from discord import app_commands
import random
import re
import csv
from io import StringIO
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Annoyance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # We access the database instance from the bot object
        self.db = bot.db
        self.target_settings_cache = {}
        # Default annoyance data
        self.random_messages = ["You dopehead", "Bad Boy", "Dingus", "Still here?", "Annoyed yet?"]
        self.emojis = ["😂", "👍", "❤️", "🤔", "😁", "😆", "😅", "🤣", "😊", "😇", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"]

    async def cog_load(self):
        """Called when the cog is loaded."""
        logger.info("Annoyance Cog loaded.")
        self.target_settings_cache = await self.db.get_all_targets()
        logger.info(f"Loaded {len(self.target_settings_cache)} targets from DB.")

    def parse_emojis(self, text: str):
        """Parses emojis from text."""
        emojis_found = []
        emoji_pattern = re.compile(r'<a?:[a-zA-Z0-9_]+:[0-9]+>|\p{Emoji}', re.UNICODE)
        parts = [part.strip() for part in text.split(',')]
        for part in parts:
            found = emoji_pattern.findall(part)
            emojis_found.extend(found)
        return emojis_found

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Check if author is a target
        user_settings = self.target_settings_cache.get(message.author.id)
        if not user_settings:
            return

        # --- Annoyance Logic ---
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
            if specific_reactions or self.emojis:
                available_methods.append('reaction')

        if not available_methods:
            return

        chosen_method = random.choice(available_methods)

        try:
            if chosen_method == 'message':
                reply_options = []
                if message_mode == 'specific_only':
                    reply_options.extend(specific_replies)
                elif message_mode == 'random_only':
                    reply_options.extend(self.random_messages)
                elif message_mode == 'both':
                    reply_options.extend(specific_replies)
                    reply_options.extend(self.random_messages)

                if reply_options:
                    await message.reply(random.choice(reply_options))
                    logger.info(f"Annoyed {message.author} with message.")

            elif chosen_method == 'reaction':
                if specific_reactions:
                    emoji = random.choice(specific_reactions)
                else:
                    emoji = random.choice(self.emojis)
                await message.add_reaction(emoji)
                logger.info(f"Annoyed {message.author} with reaction.")

        except discord.Forbidden:
            logger.warning(f"Missing permissions to annoy {message.author} in {message.channel}.")
        except Exception as e:
            logger.error(f"Error annoying {message.author}: {e}")

    # --- Slash Commands ---

    @app_commands.command(name="settarget", description="Add a user to the annoyance list.")
    @app_commands.describe(user="The user to add.")
    async def settarget(self, interaction: discord.Interaction, user: discord.Member):
        if user.id in self.target_settings_cache:
            await interaction.response.send_message(f"{user.mention} is already a target.", ephemeral=True)
            return

        success = await self.db.add_target(user.id)
        if success:
            # Update cache
            new_settings = await self.db.get_target_settings(user.id)
            if new_settings:
                self.target_settings_cache[user.id] = new_settings
                await interaction.response.send_message(f"Added {user.mention} to annoyance list.")
            else:
                await interaction.response.send_message(f"Error fetching new settings for {user.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Failed to add {user.mention}. Check logs.", ephemeral=True)

    @app_commands.command(name="removetarget", description="Stop annoying a user.")
    async def removetarget(self, interaction: discord.Interaction, user: discord.Member):
        success = await self.db.remove_target(user.id)
        if success:
            if user.id in self.target_settings_cache:
                del self.target_settings_cache[user.id]
            await interaction.response.send_message(f"Removed {user.mention} from annoyance list.")
        else:
            await interaction.response.send_message(f"{user.mention} is not in the list.", ephemeral=True)

    @app_commands.command(name="setannoyancemessage", description="Set custom messages.")
    async def setannoyancemessage(self, interaction: discord.Interaction, user: discord.Member, messages: str):
        if user.id not in self.target_settings_cache:
            await interaction.response.send_message(f"{user.mention} is not a target.", ephemeral=True)
            return

        msg_list = [m.strip() for m in messages.split(';') if m.strip()]
        success = await self.db.update_specific_reply(user.id, msg_list)
        if success:
            self.target_settings_cache[user.id]['specific_reply'] = msg_list
            await interaction.response.send_message(f"Updated messages for {user.mention}.")
        else:
            await interaction.response.send_message("Failed to update messages.", ephemeral=True)

    @app_commands.command(name="setannoyancereaction", description="Set custom reactions.")
    async def setannoyancereaction(self, interaction: discord.Interaction, user: discord.Member, emojis_input: str):
        if user.id not in self.target_settings_cache:
            await interaction.response.send_message(f"{user.mention} is not a target.", ephemeral=True)
            return

        emoji_list = self.parse_emojis(emojis_input)
        if not emoji_list:
            await interaction.response.send_message("No valid emojis found.", ephemeral=True)
            return

        success = await self.db.update_specific_reaction(user.id, emoji_list)
        if success:
            self.target_settings_cache[user.id]['specific_reaction'] = emoji_list
            await interaction.response.send_message(f"Updated reactions for {user.mention}.")
        else:
            await interaction.response.send_message("Failed to update reactions.", ephemeral=True)

    @app_commands.command(name="listtargets", description="List all targets.")
    async def listtargets(self, interaction: discord.Interaction):
        targets = await self.db.get_all_targets()
        if not targets:
            await interaction.response.send_message("No targets.", ephemeral=True)
            return
        
        msg = "**Annoyance Targets:**\n"
        for uid, data in targets.items():
            msg += f"<@{uid}>: {data['message_mode']} mode\n"
        
        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Annoyance(bot))
