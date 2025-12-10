import aiosqlite
import json
import logging
import os
from typing import Optional, Dict, Any, List
from json import JSONDecodeError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnnoyanceDB:
    def __init__(self, db_name: str = 'annoy_o_matic.db'):
        self.db_name = db_name

    async def initialize(self):
        """Initializes the database connection and creates tables."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    user_id INTEGER PRIMARY KEY,
                    specific_reply TEXT,
                    specific_reaction TEXT,
                    annoy_methods TEXT DEFAULT 'message,reaction',
                    message_mode TEXT DEFAULT 'both'
                )
            ''')
            await db.commit()
            logger.info("Database initialized and table 'targets' ensured.")

    async def add_target(self, user_id: int) -> bool:
        """Adds a target user."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    "INSERT OR IGNORE INTO targets (user_id, specific_reply, specific_reaction) VALUES (?, ?, ?)",
                    (user_id, json.dumps([]), json.dumps([]))
                )
                await db.commit()
                # Check if row was actually inserted or if it existed
                # aiosqlite doesn't give rowcount for INSERT OR IGNORE easily in one go without logic, 
                # but for this logic, we return True if they are now in the DB.
                return True
        except Exception as e:
            logger.error(f"Error adding target {user_id}: {e}")
            return False

    async def remove_target(self, user_id: int) -> bool:
        """Removes a target user."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.execute("DELETE FROM targets WHERE user_id = ?", (user_id,))
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error removing target {user_id}: {e}")
            return False

    async def update_specific_reply(self, user_id: int, specific_replies: List[str]) -> bool:
        """Updates specific replies."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.execute(
                    "UPDATE targets SET specific_reply = ? WHERE user_id = ?",
                    (json.dumps(specific_replies), user_id)
                )
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating specific replies for {user_id}: {e}")
            return False

    async def update_specific_reaction(self, user_id: int, specific_reactions: List[str]) -> bool:
        """Updates specific reactions."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.execute(
                    "UPDATE targets SET specific_reaction = ? WHERE user_id = ?",
                    (json.dumps(specific_reactions), user_id)
                )
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating specific reactions for {user_id}: {e}")
            return False

    async def update_annoy_methods(self, user_id: int, methods: List[str]) -> bool:
        """Updates annoyance methods."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                methods_str = ','.join(methods)
                cursor = await db.execute(
                    "UPDATE targets SET annoy_methods = ? WHERE user_id = ?",
                    (methods_str, user_id)
                )
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating methods for {user_id}: {e}")
            return False

    async def update_message_mode(self, user_id: int, mode: str) -> bool:
        """Updates message mode."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.execute(
                    "UPDATE targets SET message_mode = ? WHERE user_id = ?",
                    (mode, user_id)
                )
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating mode for {user_id}: {e}")
            return False

    async def get_target_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetches settings for a user."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(
                    "SELECT user_id, specific_reply, specific_reaction, annoy_methods, message_mode FROM targets WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        methods_list = row[3].split(',') if row[3] else []
                        specific_replies = json.loads(row[1]) if row[1] else []
                        specific_reactions = json.loads(row[2]) if row[2] else []
                        return {
                            "user_id": row[0],
                            "specific_reply": specific_replies,
                            "specific_reaction": specific_reactions,
                            "annoy_methods": methods_list,
                            "message_mode": row[4]
                        }
            return None
        except Exception as e:
            logger.error(f"Error fetching settings for {user_id}: {e}")
            return None

    async def get_all_targets(self) -> Dict[int, Dict[str, Any]]:
        """Fetches all targets."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(
                    "SELECT user_id, specific_reply, specific_reaction, annoy_methods, message_mode FROM targets"
                ) as cursor:
                    rows = await cursor.fetchall()
                    all_targets = {}
                    for row in rows:
                        methods_list = row[3].split(',') if row[3] else []
                        specific_replies = json.loads(row[1]) if row[1] else []
                        specific_reactions = json.loads(row[2]) if row[2] else []
                        all_targets[row[0]] = {
                            "specific_reply": specific_replies,
                            "specific_reaction": specific_reactions,
                            "annoy_methods": methods_list,
                            "message_mode": row[4]
                        }
                    return all_targets
        except Exception as e:
            logger.error(f"Error fetching all targets: {e}")
            return {}
