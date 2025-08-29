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
        # Using more subtle colors for better readability
        style = ttk.Style()
        style.configure('Background.TFrame', background="#AD1919") # Main container
        style.configure('Stats.TFrame', background="#580DAD") # Left side
        style.configure('Right.TFrame', background="#379611") # Right side

        # --- Main Container Frame ---
        container = ttk.Frame(self, style="Background.TFrame", padding=10)
        container.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)

        container.columnconfigure(0, weight=1) # Left side column
        container.columnconfigure(1, weight=3) # Right side column (takes up more space)
        container.rowconfigure(0, weight=1)

        # --- Left Side: Stats Container ---
        statscontainer = ttk.Frame(container, style="Stats.TFrame", padding=10)
        statscontainer.grid(column=0, row=0, sticky="new", padx=(0, 5))
        
        # Configure the grid inside the stats container to create the table
        statscontainer.columnconfigure(0, weight=1) # Label column
        statscontainer.columnconfigure(1, weight=1) # Point column
        statscontainer.columnconfigure(2, weight=1) # Modifier column

        # --- Create the Stats Table ---
        self.stat_vars = {}
        character_stats = [
            "Strength", "Dexterity", "Constitution",
            "Intelligence", "Wisdom", "Charisma"
        ]

        # 'enumerate' gives us both the index (for the row) and the stat name
        for i, stat_name in enumerate(character_stats):
            # Create the variables for this stat
            score_var = tk.IntVar(value=10)
            modifier_var = tk.StringVar(value="+0")

            # Store the variables in our dictionary using the stat name as the key
            self.stat_vars[stat_name] = {"score": score_var, "modifier": modifier_var}

            # Set up the trace using a lambda that passes these specific variables
            # We use default arguments in the lambda (s=score_var) to "capture" the
            # current variable in the loop correctly. This is a standard trick.
            score_var.trace_add(
                "write",
                lambda *args, s=score_var, m=modifier_var: self.update_modifier(s, m)
            )

            # Create and grid the widgets using the loop index 'i' for the row
            ttk.Label(statscontainer, text=stat_name).grid(column=0, row=i, sticky="w", pady=2)
            ttk.Entry(statscontainer, textvariable=score_var, width=5).grid(column=1, row=i, pady=2)
            ttk.Label(statscontainer, textvariable=modifier_var).grid(column=2, row=i, pady=2)

            # Immediately calculate the initial modifier
            self.update_modifier(score_var, modifier_var)

        # # --- Setup Stat Variables ---
        # self.strengthScore = tk.IntVar(value=10)
        # self.strengthModifier = tk.StringVar(value="+0")
        # self.strengthScore.trace_add("write", lambda *args: self.update_modifier(self.strengthScore, self.strengthModifier))
        # self.dexterityScore = tk.IntVar(value=10)
        # self.dexterityModifier = tk.StringVar(value="+0")
        # self.dexterityScore.trace_add("write", lambda *args: self.update_modifier(self.dexterityScore, self.dexterityModifier))

        # # --- Create Stat Widgets ---
        # strengthLabel = ttk.Label(statscontainer, text="Strength").grid(column=0, row=0)
        # strengthScore = ttk.Entry(statscontainer, textvariable=self.strengthScore).grid(column=1, row=0)
        # strengthMod = ttk.Label(statscontainer, textvariable=self.strengthModifier).grid(column=2, row=0)
        # dexterityLabel = ttk.Label(statscontainer, text="Dexterity").grid(column=0, row=1)
        # dexterityScore = ttk.Entry(statscontainer, textvariable=self.dexterityScore).grid(column=1, row=1)
        # dexterityMod = ttk.Label(statscontainer, textvariable=self.dexterityModifier).grid(column=2, row=1)
        
        # --- Right Side Container ---
        rightsidecontainer = ttk.Frame(container, style="Right.TFrame", padding=10)
        rightsidecontainer.grid(column=1, row=0, sticky="nsew", padx=(5, 0))
        
        # Example content for the right side
        right_label = ttk.Label(rightsidecontainer, text="Inventory / Notes")
        right_label.pack()

    def update_modifier(self, stat_score, modifier_score):
        """
        Calculates a modifier based on the score from 'score_variable'
        and updates the text of 'modifier_variable'.
        """
        try:
            score = stat_score.get()
            modifier = (score - 10) // 2
            
            if modifier >= 0:
                result = f"+{modifier}"
            else:
                result = str(modifier)
                
            modifier_score.set(result)

        except tk.TclError:
            # This handles the case where the entry box is empty
            modifier_score.set("...")