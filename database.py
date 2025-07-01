# database.py
import sqlite3

class AnnoyanceDB:
    def __init__(self, db_name='annoy_o_matic.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()

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
                    specific_reply TEXT
                )
            ''')
            self.conn.commit()
            print("Table 'targets' ensured.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_target(self, user_id: int, specific_reply: str):
        """Adds or updates a target user with a specific reply."""
        if not self.conn:
            print("Cannot add target: No database connection.")
            return False
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO targets (user_id, specific_reply) VALUES (?, ?)",
                (user_id, specific_reply)
            )
            self.conn.commit()
            print(f"Added/updated target: {user_id}")
            return True
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

    def get_all_targets(self):
        """Fetches all target users and their specific replies."""
        if not self.conn:
            print("Cannot get targets: No database connection.")
            return {}
        try:
            self.cursor.execute("SELECT user_id, specific_reply FROM targets")
            rows = self.cursor.fetchall()
            return {user_id: specific_reply for user_id, specific_reply in rows}
        except sqlite3.Error as e:
            print(f"Error fetching targets: {e}")
            return {}

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

# Example Usage (for testing the database.py directly)
if __name__ == "__main__":
    db = AnnoyanceDB()

    # Add some targets
    db.add_target(123456789012345678, "You are my favorite target!")
    db.add_target(987654321098765432, "Get annoyed!")
    db.add_target(123456789012345678, "Updated message for favorite target.") # Update existing

    # Get all targets
    current_targets = db.get_all_targets()
    print("Current targets:", current_targets)

    # Remove a target
    db.remove_target(987654321098765432)

    # Get all targets again
    current_targets = db.get_all_targets()
    print("Current targets after removal:", current_targets)

    db.close()
