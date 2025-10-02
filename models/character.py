import tkinter as tk
import database
from tkinter import messagebox

class Character:
    """The data model for a character."""
    def __init__(self, character_to_load=None):
        self._define_character_data()
        if character_to_load:
            self.load(character_to_load)

    def _define_character_data(self, character_to_load=None):
        """Initializes all the data models (tk.Vars) for the character sheet."""
        # --- Character Variables ---
        self.char_vars = {
            'charactername': tk.StringVar(value="Character Name"),
            'characterclass': tk.StringVar(value="Character Class"),
            'level': tk.IntVar(value=1),
            'background': tk.StringVar(value="Background"),
            'player_name': tk.StringVar(value="Player Name"),
            'race': tk.StringVar(value="Race"),
            'alignment': tk.StringVar(value="Alignment"),
            'experience_points': tk.StringVar(value="Experience Points")
        }

        self.proficiency_bonus = tk.IntVar(value=2) # Start with +2 for level 1

        # --- Ability & Skill Data ---
        # List
        self.abilities = [
            "Strength", "Dexterity", "Constitution",
            "Intelligence", "Wisdom", "Charisma"
        ]
        # Dictionary
        self.character_skills = {
            "Strength": ["Saving Throw", "Athletics"],
            "Dexterity": ["Saving Throw", "Acrobatics", "Sleight of Hand", "Stealth"],
            "Constitution": ["Saving Throw"],
            "Intelligence": ["Saving Throw", "Arcana", "History", "Investigation", "Nature", "Religion"],
            "Wisdom": ["Saving Throw", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
            "Charisma": ["Saving Throw", "Deception", "Intimidation", "Performance", "Persuasion"]
        }


        self.abilitiescore_vars = {}
        for ability in self.abilities:
            score_var = tk.IntVar(value=10)
            modifier_var = tk.StringVar(value="+0")
            self.abilitiescore_vars[ability] = {
                "score": score_var,
                "modifier": modifier_var,
                # Dictionary Comprehension
                "skills": {
                    skill: {"proficient": tk.BooleanVar(value=False)}
                    for skill in self.character_skills[ability]
                }
            }
            # Set up trace to auto-update modifier when score changes
            score_var.trace_add(
                "write",
                lambda *args, s=score_var, m=modifier_var: self.update_modifier(s, m)
            )

        # Whenever the 'level' changes, call the update function.
        self.char_vars['level'].trace_add(
            "write",
            self.update_proficiency_bonus)
        
        if character_to_load:
            self.load(character_to_load)

    def load(self, character_name):
        """Fetches data from DB and populates the tk.Vars."""
        print(f"Loading data for {character_name}...")
        data = database.load_character(character_name)
        if not data:
            messagebox.showerror("Load Error", f"Could not find data for {character_name}.")
            return

        # Populate header data
        for key, value in data.items():
            if key in self.char_vars:
                self.char_vars[key].set(value)

        # Populate ability scores and skills
        if 'abilities' in data:
            for ability, ability_data in data['abilities'].items():
                if ability in self.abilitiescore_vars:
                    self.abilitiescore_vars[ability]['score'].set(ability_data['score'])
                    for skill, skill_data in ability_data['skills'].items():
                        if skill in self.abilitiescore_vars[ability]['skills']:
                            self.abilitiescore_vars[ability]['skills'][skill]['proficient'].set(skill_data['proficient'])
        
        # After loading, immediately update all modifiers
        for ability in self.abilities:
            self.update_modifier(
                self.abilitiescore_vars[ability]['score'],
                self.abilitiescore_vars[ability]['modifier']
            )
        self.update_proficiency_bonus()


    def save(self):
        """Gathers the data and saves it to the database."""
        # Get the character's name to use as the primary key
        char_name = self.char_vars['charactername'].get()
        if not char_name or char_name == "Character Name":
            messagebox.showerror("Save Error", "Please enter a character name before saving.")
            return

        # Gather all data from the sheet
        character_data = self._get_data_as_dict()
        
        # Call the database function to save the data
        database.save_character(char_name, character_data)
        
        # Show a confirmation message
        messagebox.showinfo("Success", f"Character '{char_name}' was saved successfully!")

    def _get_data_as_dict(self):
        """Gathers all character data from the tk.Vars into a Python dictionary."""
        data = {}
        # Get header data
        for key, var in self.char_vars.items():
            data[key] = var.get()

        # Get ability scores and skills data
        data['abilities'] = {}
        for ability, ability_data in self.abilitiescore_vars.items():
            data['abilities'][ability] = {
                'score': ability_data['score'].get(),
                'skills': {
                    skill: {'proficient': prof_data['proficient'].get()}
                    for skill, prof_data in ability_data['skills'].items()
                }
            }
        return data

    def update_modifier(self, stat_score, modifier_score):
        """
        Calculates a modifier based on the score from 'stat_score'
        and updates the text of 'modifier_score'.
        """
        try:
            score = stat_score.get()
            modifier = (score - 10) // 2
            
            if modifier >= 0:
                result = f"+{modifier}"
            else:
                result = str(modifier)
                
            modifier_score.set(result)
            # print(f"{result}")

        except tk.TclError:
            # Handles the case where the entry box is empty
            modifier_score.set("...")

    # TODO Update calculation based upon table in db? (What data/formulas to have in DB vs code?)
    def update_proficiency_bonus(self, *args):
        """Updates the proficiency bonus based on character level."""
        try:
            level = self.char_vars['level'].get()
            if level >= 17:
                self.proficiency_bonus.set(6)
            elif level >= 13:
                self.proficiency_bonus.set(5)
            elif level >= 9:
                self.proficiency_bonus.set(4)
            elif level >= 5:
                self.proficiency_bonus.set(3)
            else:
                self.proficiency_bonus.set(2)
        except (IndexError, ValueError):
            self.proficiency_bonus.set(0)  # Default if parsing fails