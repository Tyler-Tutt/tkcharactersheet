import tkinter as tk
from tkinter import ttk, messagebox
from pagebase import PageBase
from character_sheet_components import CharacterHeaderFrame, AbilityScoreFrame
import database

class CharacterSheet(PageBase):
    """TTRPG Character Sheet Module"""
    def __init__(self, master, app_controller):
        self._define_character_data()
        super().__init__(master, app_controller, "Character Sheet")
        # Note: build_ui() is called by the super().__init__

    def _define_character_data(self):
        """Initializes all the data models (tk.Vars) for the character sheet."""
        # --- Character Header Data ---
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
        # DEBUG Loop through the dictionary's items
        for key, tk_variable in self.char_vars.items():
            # Use .get() to access the string value inside the tk.StringVar
            value = tk_variable.get()
            print(f"Key: {key} | Value: '{value}'")

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
            # Dictionary Item inside a Dictionary
            self.abilitiescore_vars[ability] = {
                "score": score_var,
                "modifier": modifier_var,
                "skills": {
                    skill: {"proficient": tk.BooleanVar(value=False)}
                    for skill in self.character_skills[ability]
                }
            }
            # Set up the trace to auto-update the modifier when the score changes
            score_var.trace_add(
                "write",
                lambda *args, s=score_var, m=modifier_var: self.update_modifier(s, m)
            )

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

    def save_character(self):
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

    def build_ui(self):
        # --- Style Configurations ---
        style = ttk.Style()
        style.configure('Background.TFrame', background="#AD1919", relief='solid', borderwidth=4) # Main container
        style.configure('Stats.TFrame', background="#580DAD") # Left side
        style.configure('Right.TFrame', background="#379611") # Right side
        style.configure('characterbackgroundframe.TFrame', background="#119682") # Right side
        style.configure('abilityscore.TFrame', background="#116A96") # Ability Score Frames

        # --- Main Container Frame (3x3 Table) ---
        container = ttk.Frame(self, style="Background.TFrame", padding=10)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        container.columnconfigure(0, weight=1) # Left Column
        container.columnconfigure(1, weight=1) # Middle Column
        container.columnconfigure(2, weight=1) # Right Column
        container.rowconfigure(0, weight=0) # Character Background Frame Row
        container.rowconfigure(1, weight=1) # Main content row should expand

        # --- Top Pane: Character Background ---
        # imported from character_sheet_components
        characterheaderframe = CharacterHeaderFrame(container, self.char_vars)
        characterheaderframe.grid(column=0, row=0, columnspan=3, sticky='ew', pady=(0, 10))

        # --- Stats Frame (Left Column) ---
        stats_frame = ttk.Frame(container, style="Stats.TFrame", padding=10)
        stats_frame.grid(column=0, row=1, sticky="nsew", padx=(0, 5))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        # --- Proficiency & Inspiration ---
        self.proficieny_bonus = tk.IntVar(value=0)
        self.inspiration = tk.BooleanVar()
        ttk.Entry(stats_frame, textvariable=self.proficieny_bonus).grid(column=0, row=0, sticky='ew', pady=2)
        ttk.Label(stats_frame, text="Proficiency Bonus").grid(column=1, row=0, sticky='ew')
        ttk.Checkbutton(stats_frame, text="Inspiration", variable=self.inspiration).grid(column=0, row=1, columnspan=2, sticky='ew', pady=2)

        # --- Ability Score Frames ---
        # Create an AbilityScoreFrame for each ability
        for i, ability in enumerate(self.abilities):
            score_frame = AbilityScoreFrame(
                stats_frame,
                ability_name=ability,
                skills_list=self.character_skills[ability],
                score_var=self.abilitiescore_vars[ability]['score'],
                modifier_var=self.abilitiescore_vars[ability]['modifier'],
                skill_vars_dict=self.abilitiescore_vars[ability]['skills']
            )
            score_frame.grid(column=0, row=i+2, sticky="ew", columnspan=2, pady=2)

            # Immediately calculate initial modifier values
            self.update_modifier(
                self.abilitiescore_vars[ability]['score'],
                self.abilitiescore_vars[ability]['modifier']
            )

        # --- Passive Perception ---
        # Placed after ability scores
        last_ability_row = len(self.abilities) + 1
        self.passive_perception = tk.IntVar(value=0)
        ttk.Entry(stats_frame, textvariable=self.passive_perception).grid(column=0, row=last_ability_row + 1, sticky='ew', pady=2)
        ttk.Label(stats_frame, text="Passive Perception").grid(column=1, row=last_ability_row + 1, sticky='ew')

        # Debug
        for statname, statdata in self.abilitiescore_vars.items():
            print(f"stat: {statname}, score: {statdata["score"].get()}, modifier: {statdata["modifier"].get()}")

        # --- Right Side Frame ---
        rightsideframe = ttk.Frame(container, style="Right.TFrame", padding=10)
        rightsideframe.grid(column=1, row=1, columnspan=2, sticky="nsew", padx=(5, 0))
        
        # Example content for the right side
        right_label = ttk.Label(rightsideframe, text="Inventory / Notes")
        right_label.pack()

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
    def update_proficiency_bonus(self):
        """Updates the proficiency bonus based on character level."""
        try:
            level = int(self.char_vars['level'].get().split()[1])  # Assumes format "Class Level"
            if level >= 17:
                self.proficieny_bonus.set(6)
            elif level >= 13:
                self.proficieny_bonus.set(5)
            elif level >= 9:
                self.proficieny_bonus.set(4)
            elif level >= 5:
                self.proficieny_bonus.set(3)
            else:
                self.proficieny_bonus.set(2)
        except (IndexError, ValueError):
            self.proficieny_bonus.set(0)  # Default if parsing fails