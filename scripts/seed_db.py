#TODO Figure out how/why this seed script doesn't seed to the same .db that is initialied

import json
import database # Works natively now!
import os

# Use the simple 'os' module to reliably find the json file relative to where the command is run.
JSON_PATH = os.path.join("data", "items.json")

def seed_database():
    print("Seeding reference data from JSON...")
    
    # 1. Ensure tables exist before trying to seed them
    database.init_db()
    
    # 2. Load JSON data
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {JSON_PATH}")
        return

    # 3. Seed using modern UPSERT
    with database.closing(database.get_db_connection()) as conn:
        with conn: # Context manager handles commit/rollback safely
            for item in items:
                # Extract columns for fast SQL querying, leave everything else in JSON blob
                name = item.pop("name")
                category = item.pop("category", "Gear")
                rarity = item.pop("rarity", "Common")
                requires_attunement = item.pop("requires_attunement", False)
                
                conn.execute("""
                    INSERT INTO items (name, category, rarity, requires_attunement, data)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET 
                        category=excluded.category,
                        rarity=excluded.rarity,
                        requires_attunement=excluded.requires_attunement,
                        data=excluded.data;
                """, (name, category, rarity, requires_attunement, json.dumps(item)))

    print(f"Successfully seeded/updated {len(items)} items in the database!")

if __name__ == "__main__":
    seed_database()