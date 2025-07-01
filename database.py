# database.py
import sqlite3
import json # Import json to handle lists of strings

class AnnoyanceDB:
    def __init__(self, db_name='annoy_o_matic.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()
        self._add_missing_columns() # New: Add this to handle schema changes

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def _create_table(self):
        """Creates the 'targets' table if it doesn't exist."""
        if not self.conn:
            print("Cannot create table: No database connection.")
            return
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    user_id INTEGER PRIMARY KEY,
                    specific_reply TEXT,          -- Stores JSON string of messages
                    specific_reaction TEXT,       -- Stores JSON string of emojis
                    annoy_methods TEXT DEFAULT 'message,reaction', -- Comma-separated: message,reaction
                    message_mode TEXT DEFAULT 'both' -- 'specific_only', 'random_only', 'both'
                )
            ''')
            self.conn.commit()
            print("Table 'targets' ensured.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def _add_missing_columns(self):
        """Adds new columns if they don't exist (for schema evolution)."""
        if not self.conn:
            return

        # Check for 'specific_reaction' (already added in previous version, keeping for context)
        try:
            self.cursor.execute("SELECT specific_reaction FROM targets LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE targets ADD COLUMN specific_reaction TEXT")
            self.conn.commit()
            print("Added 'specific_reaction' column.")

        # Check for 'annoy_methods' (already added)
        try:
            self.cursor.execute("SELECT annoy_methods FROM targets LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE targets ADD COLUMN annoy_methods TEXT DEFAULT 'message,reaction'")
            self.conn.commit()
            print("Added 'annoy_methods' column.")

        # Check for 'message_mode' (already added)
        try:
            self.cursor.execute("SELECT message_mode FROM targets LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE targets ADD COLUMN message_mode TEXT DEFAULT 'both'")
            self.conn.commit()
            print("Added 'message_mode' column.")


    def add_target(self, user_id: int):
        """Adds a target user without a specific reply/reaction (initial setup)."""
        if not self.conn:
            print("Cannot add target: No database connection.")
            return False
        try:
            # Insert only user_id, other columns will use their default values
            # Initialize specific_reply and specific_reaction as empty JSON lists
            self.cursor.execute(
                "INSERT OR IGNORE INTO targets (user_id, specific_reply, specific_reaction) VALUES (?, ?, ?)",
                (user_id, json.dumps([]), json.dumps([]))
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Added new target: {user_id}")
                return True
            else:
                print(f"Target {user_id} already exists.")
                return False # Already exists, but consider it successful if it's just about existence
        except sqlite3.Error as e:
            print(f"Error adding target: {e}")
            return False

    def remove_target(self, user_id: int):
        """Removes a target user from the database."""
        if not self.conn:
            print("Cannot remove target: No database connection.")
            return False
        try:
            self.cursor.execute("DELETE FROM targets WHERE user_id = ?", (user_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Removed target: {user_id}")
                return True
            else:
                print(f"Target {user_id} not found.")
                return False
        except sqlite3.Error as e:
            print(f"Error removing target: {e}")
            return False

    def update_specific_reply(self, user_id: int, specific_replies: list):
        """Updates the specific text replies for a target user."""
        if not self.conn:
            print("Cannot update specific reply: No database connection.")
            return False
        try:
            # Store list as JSON string
            self.cursor.execute(
                "UPDATE targets SET specific_reply = ? WHERE user_id = ?",
                (json.dumps(specific_replies), user_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating specific reply: {e}")
            return False

    def update_specific_reaction(self, user_id: int, specific_reactions: list):
        """Updates the specific emoji reactions for a target user."""
        if not self.conn:
            print("Cannot update specific reaction: No database connection.")
            return False
        try:
            # Store list as JSON string
            self.cursor.execute(
                "UPDATE targets SET specific_reaction = ? WHERE user_id = ?",
                (json.dumps(specific_reactions), user_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating specific reaction: {e}")
            return False

    def update_annoy_methods(self, user_id: int, methods: list):
        """Updates the annoyance methods for a target user."""
        if not self.conn:
            print("Cannot update annoy methods: No database connection.")
            return False
        try:
            # Store as comma-separated string
            methods_str = ','.join(methods)
            self.cursor.execute(
                "UPDATE targets SET annoy_methods = ? WHERE user_id = ?",
                (methods_str, user_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating annoy methods: {e}")
            return False

    def update_message_mode(self, user_id: int, mode: str):
        """Updates the message mode for a target user ('specific_only', 'random_only', 'both')."""
        if not self.conn:
            print("Cannot update message mode: No database connection.")
            return False
        try:
            self.cursor.execute(
                "UPDATE targets SET message_mode = ? WHERE user_id = ?",
                (mode, user_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating message mode: {e}")
            return False

    def get_target_settings(self, user_id: int):
        """Fetches all settings for a specific target user."""
        if not self.conn:
            print("Cannot get target settings: No database connection.")
            return None
        try:
            self.cursor.execute(
                "SELECT user_id, specific_reply, specific_reaction, annoy_methods, message_mode FROM targets WHERE user_id = ?",
                (user_id,)
            )
            row = self.cursor.fetchone()
            if row:
                # Convert annoy_methods string back to list
                methods_list = row[3].split(',') if row[3] else []
                
                # Load JSON strings back to Python lists
                specific_replies = json.loads(row[1]) if row[1] else []
                specific_reactions = json.loads(row[2]) if row[2] else []

                return {
                    "user_id": row[0],
                    "specific_reply": specific_replies, # Now a list
                    "specific_reaction": specific_reactions, # Now a list
                    "annoy_methods": methods_list,
                    "message_mode": row[4]
                }
            return None
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error fetching target settings: {e}")
            return None

    def get_all_targets(self):
        """Fetches all target users and their detailed settings."""
        if not self.conn:
            print("Cannot get all targets: No database connection.")
            return {}
        try:
            self.cursor.execute(
                "SELECT user_id, specific_reply, specific_reaction, annoy_methods, message_mode FROM targets"
            )
            rows = self.cursor.fetchall()
            all_targets_settings = {}
            for row in rows:
                methods_list = row[3].split(',') if row[3] else []
                
                # Load JSON strings back to Python lists
                specific_replies = json.loads(row[1]) if row[1] else []
                specific_reactions = json.loads(row[2]) if row[2] else []

                all_targets_settings[row[0]] = {
                    "specific_reply": specific_replies, # Now a list
                    "specific_reaction": specific_reactions, # Now a list
                    "annoy_methods": methods_list,
                    "message_mode": row[4]
                }
            return all_targets_settings
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error fetching all targets: {e}")
            return {}

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

# Example Usage (for testing the database.py directly)
if __name__ == "__main__":
    db = AnnoyanceDB(db_name='test_annoy_o_matic.db') # Use a separate test DB

    # Add a target
    db.add_target(123)
    db.add_target(456)

    # Set specific replies (now a list)
    db.update_specific_reply(123, ["Hello there, annoyance!", "Another message!", "You're still here?"])

    # Set specific reactions (now a list)
    db.update_specific_reaction(123, ["👋", "😂", "🙄"])

    # Set annoyance methods
    db.update_annoy_methods(123, ['message']) # Only messages
    db.update_annoy_methods(456, ['reaction', 'message']) # Both

    # Set message mode
    db.update_message_mode(123, 'specific_only')
    db.update_message_mode(456, 'random_only')

    # Get settings for user 123
    settings_123 = db.get_target_settings(123)
    print("\nSettings for user 123:", settings_123)

    # Get all targets
    all_targets = db.get_all_targets()
    print("\nAll targets:", all_targets)

    # Clear specific messages/reactions
    db.update_specific_reply(123, [])
    db.update_specific_reaction(123, [])
    settings_123_cleared = db.get_target_settings(123)
    print("\nSettings for user 123 after clearing:", settings_123_cleared)


    db.remove_target(123)
    db.remove_target(456)

    db.close()
