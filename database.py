import sqlite3
import json

# TODO Figure out how to save/load a character's sheet/data

DATABASE_FILE = "dnd5e.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    
    # Allows access to columns by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database and creates the necessary tables if they
    do not already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create a 'users' table.
    # The 'preferences' column will store a JSON string.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            preferences TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_races():
    """Fetches and returns a list of all race names from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM races ORDER BY name ASC")
    # The result from fetchall is a list of tuples, e.g., [('Dwarf',), ('Elf',)]
    # We use a list comprehension to extract the first item from each tuple.
    races = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return races

class UserPreferences:
    def __init__(self, username):
        self.username = username
        self.conn = get_db_connection()
        # Load or create the user on initialization
        self.preferences = self._load_or_create_user()

    def _load_or_create_user(self):
        """
        Loads user preferences from the database. If the user doesn't exist,
        creates a new entry with default preferences.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT preferences FROM users WHERE username = ?", (self.username,))
        row = cursor.fetchone()
        
        if row and row['preferences']:
            # User exists, load their preferences
            # The preferences are stored as a JSON string, so we parse it
            return json.loads(row['preferences'])
        else:
            # User does not exist or has no prefs, create them with empty preferences
            default_prefs = {}
            # Convert the dictionary to a JSON string for storage
            prefs_json = json.dumps(default_prefs)
            if row: # User exists but prefs are NULL
                 cursor.execute("UPDATE users SET preferences = ? WHERE username = ?", (prefs_json, self.username))
            else: # User does not exist
                 cursor.execute("INSERT INTO users (username, preferences) VALUES (?, ?)",
                               (self.username, prefs_json))
            self.conn.commit()
            return default_prefs