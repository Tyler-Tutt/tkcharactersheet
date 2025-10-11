import database

class CharacterModel():
    def __init__(self, character_to_load=None):
        """Initializes data model with standard Python types."""
        # --- Character Attributes ---
        self.charactername = "Character Name"
        self.characterclass = "Character Class"
        self.level = 1
        self.background = "Background"
        self.player_name = "Player Name"
        self.race = "Race"
        self.alignment = "Alignment"
        self.experience_points = 0
        self.armor_class = 10
        self.initiative = 0
        self.speed = 30
        self.max_hp = 10
        self.current_hp = 10
        self.temp_hp = 0

        # --- Ability & Skill Data ---
        self.abilities_list = [
            "Strength", "Dexterity", "Constitution",
            "Intelligence", "Wisdom", "Charisma"
        ]
        self.skills_map = {
            "Strength": ["Saving Throw", "Athletics"],
            "Dexterity": ["Saving Throw", "Acrobatics", "Sleight of Hand", "Stealth"],
            "Constitution": ["Saving Throw"],
            "Intelligence": ["Saving Throw", "Arcana", "History", "Investigation", "Nature", "Religion"],
            "Wisdom": ["Saving Throw", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
            "Charisma": ["Saving Throw", "Deception", "Intimidation", "Performance", "Persuasion"]
        }

        self.scores = {}
        for ability in self.abilities_list:
            self.scores[ability] = {
                "score": 10,
                "skills": {
                    skill: {"proficient": False}
                    for skill in self.skills_map[ability]
                }
            }
        
        if character_to_load:
            self.load(character_to_load)

    def get_modifier_for(self, ability_name):
        """Calculates and returns the modifier string for a given ability."""
        score = self.scores.get(ability_name, {}).get("score", 10)
        modifier = (score - 10) // 2
        return f"+{modifier}" if modifier >= 0 else str(modifier)

    def get_proficiency_bonus(self):
        """Calculates and returns Proficiency Bonus based on character level."""
        level = self.level
        if 1 <= level <= 4:
            return 2
        elif 5 <= level <= 8:
            return 3
        elif 9 <= level <= 12:
            return 4
        elif 13 <= level <= 16:
            return 5
        elif 17 <= level <= 20:
            return 6
        return 0
    
    def load(self, character_name):
        """Fetches data from DB and populates the model's attributes."""
        data = database.load_character(character_name)
        if not data:
            print(f"Load Error: Could not find data for {character_name}.")
            return False # Return a status

        # Directly assign attributes
        self.charactername = data.get('charactername', "Unknown")
        self.characterclass = data.get('class', "Class")
        self.level = data.get('level', 1)
        self.background = data.get('background', "Background")
        self.player_name = data.get('player_name', "Player Name")
        self.race = data.get('race', "Race")
        self.alignment = data.get('alignment', "Alignment")
        self.experience_points = data.get('experience_points', 0)
        self.armor_class = data.get('armor_class', 10)
        self.initiative = data.get('initiative', 0)
        self.speed = data.get('speed', 30)
        self.max_hp = data.get('max_hp', 10)
        self.current_hp = data.get('current_hp', 10)
        self.temp_hp = data.get('temp_hp', 0)
        
        # Load nested ability data
        if 'abilities' in data:
            self.scores = data['abilities']
        return True

    def to_dict(self):
        """Gathers all model data into a Python dictionary for saving."""
        return {
            'charactername': self.charactername,
            'characterclass': self.characterclass,
            'level': self.level,
            'background': self.background,
            'playername': self.player_name,
            'race': self.race,
            'alignment': self.alignment,
            'experience_points': self.experience_points,
            'armor_class': self.armor_class,
            'initiative': self.initiative,
            'speed': self.speed,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'temp_hp': self.temp_hp,
            'abilities': self.scores
        }

    def save(self):
        """Saves the character's data to the database."""
        if not self.character_name or self.character_name == "Character Name":
            print("Save Error: Please enter a character name before saving.")
            return False # Return a status

        character_data = self.to_dict()
        database.save_character(self.character_name, character_data)
        print(f"Success: Character '{self.character_name}' was saved.")
        return True