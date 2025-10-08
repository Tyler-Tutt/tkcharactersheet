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
        container.columnconfigure((0,1,2), weight=1) # All Columns
        container.rowconfigure(0, weight=0) # Character Background [Top] Row (Colspan=3)
        container.rowconfigure(1, weight=1) # Main content row should expand
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Top Pane: Character Background ---
        # imported from character_sheet_components
        characterheaderframe = CharacterHeaderFrame(container, self.character.char_vars)
        characterheaderframe.grid(column=0, row=0, columnspan=3, sticky='ew', pady=(0, 10))

        # --- Left Column - Offense Defense Data ---
        leftframe = ttk.Frame(container, style="Right.TFrame")
        leftframe.columnconfigure(0, weight=1)
        leftframe.grid(column=0, row=1, sticky='nsew')

        # --- AC, Initiative, Speed Frame ---
        ac_init_speed_frame2 = ttk.Frame(leftframe)
        ac_init_speed_frame2.columnconfigure((0,1,2), weight=1)
        ac_init_speed_frame2.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Armor Class
        ttk.Entry(ac_init_speed_frame2, textvariable=self.character.char_vars['armor_class'], justify='center').grid(row=0, column=0, sticky='ew')
        ttk.Label(ac_init_speed_frame2, text="Armor Class", anchor='center').grid(row=1, column=0)

        # Initiative
        ttk.Entry(ac_init_speed_frame2, textvariable=self.character.char_vars['initiative'], justify='center').grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(ac_init_speed_frame2, text="Initiative", anchor='center').grid(row=1, column=1)

        # Speed
        ttk.Entry(ac_init_speed_frame2, textvariable=self.character.char_vars['speed'], justify='center').grid(row=0, column=2, sticky='ew')
        ttk.Label(ac_init_speed_frame2, text="Speed", anchor='center').grid(row=1, column=2)

        # # --- Left Column - Ability Scores ---
        # stats_frame = ttk.Frame(container, style="Stats.TFrame", padding=10)
        # stats_frame.columnconfigure((0,1,2), weight=1)
        # stats_frame.grid(column=0, row=1, sticky="nsew", padx=(0, 5))

        # # --- Proficiency & Inspiration Frame ---
        # proficiency_inspiration_frame = ttk.Frame(stats_frame)
        # proficiency_inspiration_frame.columnconfigure(0, weight=1)
        # proficiency_inspiration_frame.grid(column=0, row=0, sticky='nsew')

        # # --- Proficiency & Inspiration ---
        # self.proficiency_bonus = tk.IntVar(value=0)
        # self.inspiration = tk.BooleanVar()
        # ttk.Entry(proficiency_inspiration_frame, textvariable=self.character.proficiency_bonus).grid(column=0, row=0, sticky='ew', pady=2)
        # ttk.Label(proficiency_inspiration_frame, text="Proficiency Bonus").grid(column=1, row=0, sticky='ew')
        # ttk.Checkbutton(proficiency_inspiration_frame, text="Inspiration", variable=self.inspiration).grid(column=0, row=1, columnspan=2, sticky='ew', pady=2)

        # # --- Ability Score Frames ---
        # # Create an AbilityScoreFrame [Class] for each ability
        # for i, ability in enumerate(self.character.abilities):
        #     score_frame = AbilityScoreFrame(
        #         proficiency_inspiration_frame,
        #         ability_name=ability,
        #         skills_list=self.character.character_skills[ability],
        #         score_var=self.character.abilitiescore_vars[ability]['score'],
        #         modifier_var=self.character.abilitiescore_vars[ability]['modifier'],
        #         skill_vars_dict=self.character.abilitiescore_vars[ability]['skills']
        #     )
        #     score_frame.grid(column=0, row=i+2, sticky="ew", columnspan=2, pady=2)

        #     # Immediately calculate initial modifier values
        #     self.character.update_modifier(
        #         self.character.abilitiescore_vars[ability]['score'],
        #         self.character.abilitiescore_vars[ability]['modifier']
        #     )

        # # --- Passive Perception ---
        # last_ability_row = len(self.character.abilities) + 1
        # self.passive_perception = tk.IntVar(value=0)
        # ttk.Entry(proficiency_inspiration_frame, textvariable=self.passive_perception).grid(column=0, row=last_ability_row + 1, sticky='ew', pady=2)
        # ttk.Label(proficiency_inspiration_frame, text="Passive Perception").grid(column=1, row=last_ability_row + 1, sticky='ew')

        # Debug
        for statname, statdata in self.character.abilitiescore_vars.items():
            print(f"stat: {statname}, score: {statdata["score"].get()}, modifier: {statdata["modifier"].get()}")

        # --- Middle Column - Offense Defense Data ---
        middleframe = ttk.Frame(container)
        middleframe.columnconfigure(0, weight=1)
        middleframe.grid(column=1, row=1, sticky='nsew', padx=(5, 5))

        # --- AC, Initiative, Speed Frame ---
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

        # --- Right Side Frame ---
        rightsideframe = ttk.Frame(container, style="Right.TFrame")
        rightsideframe.columnconfigure(0, weight=1)
        rightsideframe.grid(column=2, row=1, sticky="nsew")

        #TODO Implement Text Area w/ Hover Text from Database?
        # --- Features & Traits ---
        features_traits_frame = ttk.Frame(rightsideframe)
        features_traits_frame.columnconfigure((0,1,2), weight=1)
        features_traits_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Armor Class
        ttk.Entry(features_traits_frame, textvariable=self.character.char_vars['armor_class'], justify='center').grid(row=0, column=0, sticky='ew')
        ttk.Label(features_traits_frame, text="Armor Class", anchor='center').grid(row=1, column=0)

        # Initiative
        ttk.Entry(features_traits_frame, textvariable=self.character.char_vars['initiative'], justify='center').grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(features_traits_frame, text="Initiative", anchor='center').grid(row=1, column=1)

        # Speed
        ttk.Entry(features_traits_frame, textvariable=self.character.char_vars['speed'], justify='center').grid(row=0, column=2, sticky='ew')
        ttk.Label(features_traits_frame, text="Speed", anchor='center').grid(row=1, column=2)
        
        # # Placeholder content for the right side
        # right_label = ttk.Label(rightsideframe, text="Inventory / Notes")
        # right_label.grid(column=0, row=0)
        
    def save_character(self):
        """Public method to trigger the model's save functionality."""
        self.character.save()