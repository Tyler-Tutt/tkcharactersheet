import sqlite3
import json

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

    def get_page_preferences(self, page_name, default_prefs=None):
        """Gets the entire preference dictionary for a specific page."""
        if default_prefs is None:
            default_prefs = {}
        # Get the sub-dictionary for the page, or return the default if not found.
        return self.preferences.get(page_name, default_prefs)

    def get_preference(self, page_name, key, default=None):
        """Gets a specific preference value from within a page's preferences."""
        # Get the page's preference dictionary first
        page_prefs = self.preferences.get(page_name, {})
        # Then get the specific key from that dictionary
        return page_prefs.get(key, default)

    def set_preference(self, page_name, key, value):
        """Sets a specific preference value and saves it to the database."""
        if page_name not in self.preferences:
            self.preferences[page_name] = {}
        self.preferences[page_name][key] = value
        
        # Save the entire updated preferences dictionary back to the DB
        prefs_json = json.dumps(self.preferences)
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET preferences = ? WHERE username = ?",
                       (prefs_json, self.username))
        self.conn.commit()

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
