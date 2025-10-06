import tkinter as tk
from tkinter import ttk
from .pagebase import PageBase
from .components.character_sheet_components import CharacterHeaderFrame, AbilityScoreFrame
from models.character import Character

class CharacterSheet(PageBase):
    """TTRPG Character Sheet Module"""
    def __init__(self, master, app_controller, character_to_load=None):
        super().__init__(master, app_controller, "Character Sheet")
        self.character = Character(character_to_load)
        self.build_ui()

    def build_ui(self):
        # --- Style Configurations ---
        style = ttk.Style()
        style.configure('Background.TFrame', background="#AD1919", relief='solid', borderwidth=4) # Main container
        style.configure('Stats.TFrame', background="#580DAD") # Left side
        style.configure('Right.TFrame', background="#379611") # Right side
        style.configure('characterbackgroundframe.TFrame', background="#119682") # Top
        style.configure('abilityscore.TFrame', background="#116A96") # Ability Score Frames

        # --- Main Container Frame (3x3 Table) ---
        container = ttk.Frame(self, style="Background.TFrame", padding=10)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        container.columnconfigure(0, weight=1) # Left Column
        container.columnconfigure(1, weight=1) # Middle Column
        container.columnconfigure(2, weight=1) # Right Column
        container.rowconfigure(0, weight=0) # Character Background [Top] Row (Colspan=3)
        container.rowconfigure(1, weight=1) # Main content row should expand

        # --- Top Pane: Character Background ---
        # imported from character_sheet_components
        characterheaderframe = CharacterHeaderFrame(container, self.character.char_vars)
        characterheaderframe.grid(column=0, row=0, columnspan=3, sticky='ew', pady=(0, 10))

        # --- Stats Frame (Left Column) ---
        stats_frame = ttk.Frame(container, style="Stats.TFrame", padding=10)
        stats_frame.grid(column=0, row=1, sticky="nsew", padx=(0, 5))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        # --- Proficiency & Inspiration ---
        self.proficiency_bonus = tk.IntVar(value=0)
        self.inspiration = tk.BooleanVar()
        ttk.Entry(stats_frame, textvariable=self.character.proficiency_bonus).grid(column=0, row=0, sticky='ew', pady=2)
        ttk.Label(stats_frame, text="Proficiency Bonus").grid(column=1, row=0, sticky='ew')
        ttk.Checkbutton(stats_frame, text="Inspiration", variable=self.inspiration).grid(column=0, row=1, columnspan=2, sticky='ew', pady=2)

        # --- Ability Score Frames ---
        # Create an AbilityScoreFrame [Class] for each ability
        for i, ability in enumerate(self.character.abilities):
            score_frame = AbilityScoreFrame(
                stats_frame,
                ability_name=ability,
                skills_list=self.character.character_skills[ability],
                score_var=self.character.abilitiescore_vars[ability]['score'],
                modifier_var=self.character.abilitiescore_vars[ability]['modifier'],
                skill_vars_dict=self.character.abilitiescore_vars[ability]['skills']
            )
            score_frame.grid(column=0, row=i+2, sticky="ew", columnspan=2, pady=2)

            # Immediately calculate initial modifier values
            self.character.update_modifier(
                self.character.abilitiescore_vars[ability]['score'],
                self.character.abilitiescore_vars[ability]['modifier']
            )

        # --- Passive Perception ---
        # Placed after ability scores
        last_ability_row = len(self.character.abilities) + 1
        self.passive_perception = tk.IntVar(value=0)
        ttk.Entry(stats_frame, textvariable=self.passive_perception).grid(column=0, row=last_ability_row + 1, sticky='ew', pady=2)
        ttk.Label(stats_frame, text="Passive Perception").grid(column=1, row=last_ability_row + 1, sticky='ew')

        # Debug
        for statname, statdata in self.character.abilitiescore_vars.items():
            print(f"stat: {statname}, score: {statdata["score"].get()}, modifier: {statdata["modifier"].get()}")

        # --- Middle Column - Offense Defense Data ---
        middleframe = ttk.Frame(container)
        middleframe.grid(column=1, row=1, sticky='nsew')
        middleframe.columnconfigure(0, weight=1)

        # --- AC, Initiative, Speed ---
        ac_init_speed_frame = ttk.Frame(middleframe)
        ac_init_speed_frame.columnconfigure((0,1,2), weight=1)
        ac_init_speed_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Armor Class
        ttk.Entry(ac_init_speed_frame, textvariable=self.character.char_vars['armor_class'], justify='center').grid(row=0, column=0, sticky='ew')
        ttk.Label(ac_init_speed_frame, text="Armor Class", anchor='center').grid(row=1, column=0)

        # Initiative
        ttk.Entry(ac_init_speed_frame, textvariable=self.character.char_vars['initiative'], justify='center').grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(ac_init_speed_frame, text="Initiative", anchor='center').grid(row=1, column=1)

        # Speed
        ttk.Entry(ac_init_speed_frame, textvariable=self.character.char_vars['speed'], justify='center').grid(row=0, column=2, sticky='ew')
        ttk.Label(ac_init_speed_frame, text="Speed", anchor='center').grid(row=1, column=2)

        # Placeholder content
        # middle_label = ttk.Label(middleframe, text="Inventory / Notes")
        # middle_label.grid(column=0, row=0)

        # --- Right Side Frame ---
        rightsideframe = ttk.Frame(container, style="Right.TFrame", padding=10)
        rightsideframe.grid(column=2, row=1, sticky="nsew", padx=(5, 0))
        rightsideframe.columnconfigure(0, weight=1)
        
        # Placeholder content for the right side
        right_label = ttk.Label(rightsideframe, text="Inventory / Notes")
        right_label.grid(column=0, row=0)
        
    def save_character(self):
        """Public method to trigger the model's save functionality."""
        self.character.save()