# database.py
import aiosqlite
import json
import logging
from typing import Optional, Dict, Any, List
from json import JSONDecodeError

# Configure logging for the database module
logger = logging.getLogger(__name__)

class AnnoyanceDB:
    def __init__(self, db_name: str = 'annoy_o_matic.db'):
        self.db_name = db_name
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Establishes an asynchronous connection to the SQLite database."""
        try:
            self.conn = await aiosqlite.connect(self.db_name)
            # Enable row factory for easier column access if needed, though we use indices mostly
            self.conn.row_factory = aiosqlite.Row 
            logger.info(f"Connected to database: {self.db_name}")
            await self._create_table()
            await self._add_missing_columns()
        except aiosqlite.Error as e:
            logger.error(f"Error connecting to database: {e}")
            self.conn = None

    async def _create_table(self):
        """Creates the 'targets' table if it doesn't exist."""
        if not self.conn:
            logger.warning("Cannot create table: No database connection.")
            return
        try:
            await self.conn.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    user_id INTEGER PRIMARY KEY,
                    specific_reply TEXT,          -- Stores JSON string of messages
                    specific_reaction TEXT,       -- Stores JSON string of emojis
                    annoy_methods TEXT DEFAULT 'message,reaction', -- Comma-separated: message,reaction
                    message_mode TEXT DEFAULT 'both' -- 'specific_only', 'random_only', 'both'
                )
            ''')
            await self.conn.commit()
            logger.info("Table 'targets' ensured.")
        except aiosqlite.Error as e:
            logger.error(f"Error creating table: {e}")

    async def _add_missing_columns(self):
        """Adds new columns if they don't exist (for schema evolution)."""
        if not self.conn:
            return

        async def add_column_if_missing(column_name, column_def):
            try:
                await self.conn.execute(f"SELECT {column_name} FROM targets LIMIT 1")
            except aiosqlite.OperationalError:
                await self.conn.execute(f"ALTER TABLE targets ADD COLUMN {column_name} {column_def}")
                await self.conn.commit()
                logger.info(f"Added '{column_name}' column.")

        await add_column_if_missing("specific_reaction", "TEXT")
        await add_column_if_missing("annoy_methods", "TEXT DEFAULT 'message,reaction'")
        await add_column_if_missing("message_mode", "TEXT DEFAULT 'both'")

    async def add_target(self, user_id: int) -> bool:
        """Adds a target user without a specific reply/reaction (initial setup)."""
        if not self.conn:
            logger.error("Cannot add target: No database connection.")
            return False
        try:
            cursor = await self.conn.execute(
                "INSERT OR IGNORE INTO targets (user_id, specific_reply, specific_reaction) VALUES (?, ?, ?)",
                (user_id, json.dumps([]), json.dumps([]))
            )
            await self.conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Added new target: {user_id}")
                return True
            else:
                logger.info(f"Target {user_id} already exists.")
                return False
        except aiosqlite.Error as e:
            logger.error(f"Error adding target: {e}")
            return False

    async def remove_target(self, user_id: int) -> bool:
        """Removes a target user from the database."""
        if not self.conn:
            logger.error("Cannot remove target: No database connection.")
            return False
        try:
            cursor = await self.conn.execute("DELETE FROM targets WHERE user_id = ?", (user_id,))
            await self.conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Removed target: {user_id}")
                return True
            else:
                logger.info(f"Target {user_id} not found.")
                return False
        except aiosqlite.Error as e:
            logger.error(f"Error removing target: {e}")
            return False

    async def update_specific_reply(self, user_id: int, specific_replies: List[str]) -> bool:
        """Updates the specific text replies for a target user."""
        if not self.conn:
            logger.error("Cannot update specific reply: No database connection.")
            return False
        try:
            cursor = await self.conn.execute(
                "UPDATE targets SET specific_reply = ? WHERE user_id = ?",
                (json.dumps(specific_replies), user_id)
            )
            await self.conn.commit()
            return cursor.rowcount > 0
        except aiosqlite.Error as e:
            logger.error(f"Error updating specific reply: {e}")
            return False

    async def update_specific_reaction(self, user_id: int, specific_reactions: List[str]) -> bool:
        """Updates the specific emoji reactions for a target user."""
        if not self.conn:
            logger.error("Cannot update specific reaction: No database connection.")
            return False
        try:
            cursor = await self.conn.execute(
                "UPDATE targets SET specific_reaction = ? WHERE user_id = ?",
                (json.dumps(specific_reactions), user_id)
            )
            await self.conn.commit()
            return cursor.rowcount > 0
        except aiosqlite.Error as e:
            logger.error(f"Error updating specific reaction: {e}")
            return False

    async def update_annoy_methods(self, user_id: int, methods: List[str]) -> bool:
        """Updates the annoyance methods for a target user."""
        if not self.conn:
            logger.error("Cannot update annoy methods: No database connection.")
            return False
        try:
            methods_str = ','.join(methods)
            cursor = await self.conn.execute(
                "UPDATE targets SET annoy_methods = ? WHERE user_id = ?",
                (methods_str, user_id)
            )
            await self.conn.commit()
            return cursor.rowcount > 0
        except aiosqlite.Error as e:
            logger.error(f"Error updating annoy methods: {e}")
            return False

    async def update_message_mode(self, user_id: int, mode: str) -> bool:
        """Updates the message mode for a target user."""
        if not self.conn:
            logger.error("Cannot update message mode: No database connection.")
            return False
        try:
            cursor = await self.conn.execute(
                "UPDATE targets SET message_mode = ? WHERE user_id = ?",
                (mode, user_id)
            )
            await self.conn.commit()
            return cursor.rowcount > 0
        except aiosqlite.Error as e:
            logger.error(f"Error updating message mode: {e}")
            return False

    async def get_target_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetches all settings for a specific target user."""
        if not self.conn:
            logger.error("Cannot get target settings: No database connection.")
            return None
        try:
            async with self.conn.execute(
                "SELECT user_id, specific_reply, specific_reaction, annoy_methods, message_mode FROM targets WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    # row is an aiosqlite.Row object, access by index or name
                    methods_list = row['annoy_methods'].split(',') if row['annoy_methods'] else []
                    specific_replies = json.loads(row['specific_reply']) if row['specific_reply'] else []
                    specific_reactions = json.loads(row['specific_reaction']) if row['specific_reaction'] else []
                    return {
                        "user_id": row['user_id'],
                        "specific_reply": specific_replies,
                        "specific_reaction": specific_reactions,
                        "annoy_methods": methods_list,
                        "message_mode": row['message_mode']
                    }
                return None
        except (aiosqlite.Error, JSONDecodeError) as e:
            logger.error(f"Error fetching target settings: {e}")
            return None

    async def get_all_targets(self) -> Dict[int, Dict[str, Any]]:
        """Fetches all target users and their detailed settings."""
        if not self.conn:
            logger.error("Cannot get all targets: No database connection.")
            return {}
        try:
            async with self.conn.execute(
                "SELECT user_id, specific_reply, specific_reaction, annoy_methods, message_mode FROM targets"
            ) as cursor:
                rows = await cursor.fetchall()
                all_targets_settings: Dict[int, Dict[str, Any]] = {}
                for row in rows:
                    methods_list = row['annoy_methods'].split(',') if row['annoy_methods'] else []
                    specific_replies = json.loads(row['specific_reply']) if row['specific_reply'] else []
                    specific_reactions = json.loads(row['specific_reaction']) if row['specific_reaction'] else []
                    all_targets_settings[row['user_id']] = {
                        "specific_reply": specific_replies,
                        "specific_reaction": specific_reactions,
                        "annoy_methods": methods_list,
                        "message_mode": row['message_mode']
                    }
                return all_targets_settings
        except (aiosqlite.Error, JSONDecodeError) as e:
            logger.error(f"Error fetching all targets: {e}")
            return {}

    async def close(self):
        """Closes the database connection."""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed.")
