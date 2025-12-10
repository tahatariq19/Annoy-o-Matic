import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from database import AnnoyanceDB

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment.")

class AnnoyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = AnnoyanceDB()

    async def setup_hook(self):
        # Initialize DB
        await self.db.initialize()
        # Load Cogs
        await self.load_extension('cogs.annoyance')
        # Sync Commands
        await self.tree.sync()
        logger.info("Commands synced.")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

if __name__ == '__main__':
    bot = AnnoyBot()
    bot.run(DISCORD_TOKEN)
