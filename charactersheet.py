import tkinter as tk
from tkinter import ttk
from pagebase import PageBase

class CharacterSheet(PageBase):
    """TTRPG Character Sheet Module"""
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, "Character Sheet")

    def build_ui(self):
        # --- Main Layout Configuration ---
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Style Configuration ---
        style = ttk.Style()
        style.configure('Background.TFrame', background="#AD1919", relief='solid', borderwidth=4) # Main container
        style.configure('Stats.TFrame', background="#580DAD") # Left side
        style.configure('Right.TFrame', background="#379611") # Right side
        style.configure('characterbackgroundframe.TFrame', background="#119682") # Right side
        style.configure('statframe.TFrame', background="#116A96") # Stat Frames

        # --- Main Container Frame (3x3 Table) ---
        container = ttk.Frame(self, style="Background.TFrame", padding=10)
        container.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)

        container.columnconfigure(0, weight=1) # Left Column
        container.columnconfigure(1, weight=1) # Middle Column
        container.columnconfigure(2, weight=1) # Right Column
        container.rowconfigure(0, weight=0) # Character Background Frame Row
        container.rowconfigure(1, weight=0) 
        container.rowconfigure(2, weight=0)

        # --- Top Pane: Character Background ---
        charbackgroundframe = ttk.Frame(container, style="characterbackgroundframe.TFrame", padding=5)
        charbackgroundframe.grid(column=0, row=0, columnspan=4, sticky='ew', pady=(0, 10))

        charbackgroundframe.columnconfigure(0, weight=1) # Character Name Column
        charbackgroundframe.columnconfigure(1, weight=2) # Character Background Column
        charbackgroundframe.rowconfigure(0, weight=1)

        # 1x1 Table for Character Name
        characternameframe = ttk.Frame(charbackgroundframe)
        characternameframe.grid(column=0, row=0, sticky='ew')
        characternameframe.columnconfigure(0, weight=1)
        characternameframe.rowconfigure(0, weight=1)
        self.charactername = tk.StringVar(value="Character Name")
        ttk.Entry(characternameframe, textvariable=self.charactername).grid(column=0, row=0, sticky='ew')

        # 2x3 Table for Background Info Entries
        backgroundinfoframe = ttk.Frame(charbackgroundframe)
        backgroundinfoframe.grid(column=1, row=0, sticky='ew', columnspan=3) # Spans Right 3 Columns
        backgroundinfoframe.columnconfigure(0, weight=1)
        backgroundinfoframe.columnconfigure(1, weight=1)
        backgroundinfoframe.columnconfigure(2, weight=1)
        backgroundinfoframe.rowconfigure(0, weight=1)
        backgroundinfoframe.rowconfigure(1, weight=1)

        # Define background fields in a more structured way
        background_fields = {
            'class_level': "Class & Level",
            'background': "Background",
            'player_name': "Player Name",
            'race': "Race",
            'alignment': "Alignment",
            'experience_points': "Experience Points"
        }

        self.class_level = tk.StringVar(value="Class & Level")
        self.background = tk.StringVar(value="Background")
        self.player_name = tk.StringVar(value="Player Name")
        self.race = tk.StringVar(value="Race")
        self.alignment = tk.StringVar(value="Alignment")
        self.experience_points = tk.StringVar(value="Experience Points")

        ttk.Entry(backgroundinfoframe, textvariable=self.class_level).grid(column=0, row=0, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=self.background).grid(column=1, row=0, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=self.player_name).grid(column=2, row=0, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=self.race).grid(column=0, row=1, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=self.alignment).grid(column=1, row=1, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=self.experience_points).grid(column=2, row=1, sticky='ew')

        # --- Stats Frame ---
        statsframe = ttk.Frame(container, style="Stats.TFrame", padding=10)
        statsframe.grid(column=0, row=1, sticky="nsew", padx=(0, 5))
        
        # 9x2 Table for Stats
        statsframe.columnconfigure(0, weight=1)
        statsframe.columnconfigure(1, weight=1)
        statsframe.rowconfigure(0, weight=1)
        statsframe.rowconfigure(1, weight=1)
        statsframe.rowconfigure(2, weight=1)
        statsframe.rowconfigure(3, weight=1)
        statsframe.rowconfigure(4, weight=1)
        statsframe.rowconfigure(5, weight=1)
        statsframe.rowconfigure(6, weight=1)
        statsframe.rowconfigure(7, weight=1)
        statsframe.rowconfigure(8, weight=1)

        # --- Proficieny & Inspiration ---

        self.proficieny_bonus = tk.IntVar(value=0)
        self.inspiration = tk.BooleanVar()
        ttk.Entry(statsframe, textvariable=self.proficieny_bonus).grid(column=0, row=0, sticky='ew', pady=2)
        ttk.Label(statsframe, text="Proficiency Bonus").grid(column=1, row=0, sticky='ew')
        ttk.Checkbutton(statsframe, text="Inspiration", variable=self.inspiration).grid(column=0, row=1, columnspan=2, sticky='ew', pady=2)

        # --- Create Stats Table ---
        character_stats = [
            "Strength", "Dexterity", "Constitution",
            "Intelligence", "Wisdom", "Charisma"
        ]

        # --- Create Skills Dictionary ---
        character_skills = {
            "Strength": ["Athletics"],
            "Dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"], 
            "Constitution": [],
            "Intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"],
            "Wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
            "Charisma": ["Deception", "Intimidation", "Performance", "Persuasion"]
        }

        # --- Create empty Dictionaries that will hold stat Scores & Modifiers ---
        self.stat_vars = {}
        self.stat_frames = {}

        # 'enumerate' gives us both the index (for the row) and the stat name
        for i, stat_name in enumerate(character_stats):
            # Create the variables for this stat
            score_var = tk.IntVar(value=10)
            modifier_var = tk.StringVar(value="+0")

            # Store the variables in our dictionary using the stat name as the key
            self.stat_vars[stat_name] = {"score": score_var, "modifier": modifier_var}
            # print(f"Debug: score: {self.stat_vars[stat_name]['score'].get()} || modifier: {self.stat_vars[stat_name]['modifier'].get()}")

            # Set up the trace using a lambda that passes these specific variables
            # We use default arguments in the lambda (s=score_var) to "capture" the
            # current variable in the loop correctly. This is a standard trick.
            score_var.trace_add(
                "write",
                lambda *args, s=score_var, m=modifier_var: self.update_modifier(s, m)
            )

            # --- Create 6x4 Table Child Frames for each Stat ---
            frame_key = f"{stat_name}_frame"
            new_frame = ttk.Frame(statsframe, style='statframe.TFrame')
            new_frame.grid(column=0, row=i+2, sticky="ew", columnspan=3, pady=2)
            new_frame.columnconfigure(0, weight=2)
            new_frame.columnconfigure(1, weight=1)
            new_frame.columnconfigure(2, weight=1)
            new_frame.columnconfigure(3, weight=2)
            new_frame.rowconfigure(0, weight=1)
            new_frame.rowconfigure(1, weight=1)
            new_frame.rowconfigure(2, weight=1)
            new_frame.rowconfigure(3, weight=1)
            new_frame.rowconfigure(4, weight=1)
            new_frame.rowconfigure(5, weight=1)
            # Adds current Stat in Loop to stat_frames dictionary
            self.stat_frames[frame_key] = new_frame

            # Stat Label, Score, and Modifier Score
            ttk.Label(self.stat_frames[frame_key], text=stat_name).grid(column=0, row=0, sticky="nsew", pady=2)
            ttk.Entry(self.stat_frames[frame_key], textvariable=score_var, width=5).grid(column=0, row=1, sticky="w", pady=2)
            ttk.Label(self.stat_frames[frame_key], textvariable=modifier_var).grid(column=0, row=2, sticky="w", pady=2)

            # Proficiency Checkbox, Skill Score, Skill Name
            ttk.Checkbutton(self.stat_frames[frame_key]).grid(column=1, row=0)
            ttk.Entry(self.stat_frames[frame_key]).grid(column=2, row=0)
            ttk.Label(self.stat_frames[frame_key], text="Saving Throw").grid(column=3, row=0)
            ttk.Label(self.stat_frames[frame_key], text="Saving Throw").grid(column=3, row=1)
            ttk.Label(self.stat_frames[frame_key], text="Saving Throw").grid(column=3, row=2)
            ttk.Label(self.stat_frames[frame_key], text="Saving Throw").grid(column=3, row=3)

            # Immediately calculate initial modifier values
            self.update_modifier(score_var, modifier_var)

        for statname, statdata in self.stat_vars.items():
            print(f"stat: {statname}, score: {statdata["score"].get()}, modifier: {statdata["modifier"].get()}")

        self.passive_perception = tk.IntVar(value=0)
        ttk.Entry(statsframe, textvariable=self.passive_perception).grid(column=0, row=8, sticky='ew', pady=2)
        ttk.Label(statsframe, text="Passive Perception").grid(column=1, row=8, sticky='ew')

        # --- Right Side Frame ---
        rightsideframe = ttk.Frame(container, style="Right.TFrame", padding=10)
        rightsideframe.grid(column=1, row=1, columnspan=3, sticky="nsew", padx=(5, 0))
        
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
            print(f"{result}")

        except tk.TclError:
            # This handles the case where the entry box is empty
            modifier_score.set("...")