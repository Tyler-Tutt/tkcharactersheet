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
            print(f"Debug: i: {i} | stat_name: {stat_name}")

            # Store the variables in our dictionary using the stat name as the key
            self.stat_vars[stat_name] = {"score": score_var, "modifier": modifier_var}
            print(f"Debug: score: {self.stat_vars[stat_name]['score'].get()} || modifier: {self.stat_vars[stat_name]['modifier'].get()}")

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

        for statname, statdata in self.stat_vars.items():
            print(f"stat: {statname}, score: {statdata["score"].get()}, modifier: {statdata["modifier"].get()}")

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