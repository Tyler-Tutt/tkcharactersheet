import sqlite3
import json
from contextlib import closing

DATABASE_FILE = "dnd5e.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database. i.e. Creates a database Connection object"""
    connection = sqlite3.connect(DATABASE_FILE)
    
    # Allows access to columns by name
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    """
    Initializes the database and creates the necessary tables if they
    do not already exist.
    """
    # using closing() guarantees connection.close() is called when the block ends
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        
        # Create a 'users' table.
        # The 'preferences' column will store a JSON string.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                preferences TEXT
            )
        ''')

        # Store a JSON string of the entire sheet in characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                name TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        ''')
        
        connection.commit()

def save_character(character_name, character_data):
    """
    Saves a character's data to the database.
    Inserts a new record or replaces an existing one based on the character name.
    """
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        # Convert the Python dictionary to a JSON string for storage
        data_json = json.dumps(character_data)
        
        # Use INSERT OR REPLACE to handle both new and existing characters
        cursor.execute("INSERT OR REPLACE INTO characters (name, data) VALUES (?, ?)",
                       (character_name, data_json))
        
        connection.commit()
    print(f"Character '{character_name}' saved successfully.")

def get_character_list():
    """Fetches and returns a list of all saved character names."""
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM characters ORDER BY name DESC")
        # List comprehension to extract the name from each row tuple
        characters = [row['name'] for row in cursor.fetchall()]
        
    return characters

def load_character(character_name):
    """Fetches a specific character's data from the database."""
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT data FROM characters WHERE name = ?", (character_name,))
        row = cursor.fetchone()
        
    if row:
        # Parse the JSON string and return it as a Python dictionary
        return json.loads(row['data'])
    return None # Return None if no character is found

def get_races():
    """Fetches and returns a list of all race names from the database."""
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM races ORDER BY name ASC")
        # The result from fetchall is a list of Tuples per Row of Data returned, e.g., [('Dwarf',), ('Elf',)]
        # Use a list comprehension to extract the first item from each tuple.
        races = [row['name'] for row in cursor.fetchall()]
        
    return races

class UserPreferences:
    def __init__(self, username):
        self.username = username
        # Load or create the user on initialization. 
        # Notice we no longer save a permanent connection to self.connection!
        self.preferences = self._load_or_create_user()

    def _load_or_create_user(self):
        """
        Loads user preferences from the database. If the user doesn't exist,
        creates a new entry with default preferences.
        """
        with closing(get_db_connection()) as connection:
            cursor = connection.cursor()
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
                connection.commit()
                return default_prefs