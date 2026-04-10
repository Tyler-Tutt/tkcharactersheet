import sqlite3
import json
from contextlib import closing

DATABASE_FILE = "dnd5e.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database. i.e. Creates a database Connection object"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Allows access to columns by name 
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    """
    Initializes the database schema (Strictly DDL (CREATE TABLES)) if they do not already exist.
    """
    # closing() guarantees connection.close() is called when the block ends
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        
        # Create 'users' table.
        # 'preferences' column stores a JSON string.
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

        # 1. Build Hybrid Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                rarity TEXT NOT NULL,
                requires_attunement BOOLEAN,
                data TEXT NOT NULL
            )
        ''')
        
        connection.commit()

def fetch_item(item_name):
    """Fetches an item and merges its SQL columns and JSON data into one dictionary."""
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        # Fetch EVERYTHING (*) instead of just 'data'
        cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
        row = cursor.fetchone()
        
    if row:
        # Convert the SQLite Row to a standard Python dictionary
        item_dictionaried = dict(row)
        # Pop the JSON string out from the 'data' field and parse it
        data_dict = json.loads(item_dictionaried.pop('data'))
        # Merge the parsed JSON back into the main dictionary
        item_dictionaried.update(data_dict)
        # SQLite stores booleans as 1 or 0, so we cast it back to a Python bool
        item_dictionaried['requires_attunement'] = bool(item_dictionaried['requires_attunement'])
        return item_dictionaried
    return None

def save_character(character_name: str, character_data: dict):
    """Saves character data using modern UPSERT syntax."""
    data_json = json.dumps(character_data)
    
    with closing(get_db_connection()) as conn:
        with conn: # Context manager automatically handles commit/rollback
            conn.execute("""
                INSERT INTO characters (name, data) 
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET data = excluded.data;
            """, (character_name, data_json))
    print(f"Character '{character_name}' saved successfully.")

def fetch_character_list():
    """
    Fetches and returns a list of all saved character names.
    """
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM characters ORDER BY name DESC")
        # List comprehension to extract the name from each row tuple
        characters = [row['name'] for row in cursor.fetchall()]
        
    return characters

def fetch_character(character_name):
    """
    Fetches a specific character's data from the database and returns it as a Python Dictionary
    """
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT data FROM characters WHERE name = ?", (character_name,))
        row = cursor.fetchone()

    if row:
        # Parse the JSON string and return it as a Python dictionary
        return json.loads(row['data'])
    return None # Return None if no character is found

def fetch_races():
    """
    Fetches and returns a list of all race names from the database.
    """
    with closing(get_db_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM races ORDER BY name ASC")
        # The result from fetchall is a list of Tuples per Row of Data returned, e.g., [('Dwarf',), ('Elf',)]
        # Use a list comprehension to extract the first item from each tuple.
        races = [row['name'] for row in cursor.fetchall()]
        
    return races

#TODO Dead Code?
class UserPreferences:
    """
    Creates a User Record
    """
    def __init__(self, username):
        self.username = username
        # Load or create the user on initialization. 
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