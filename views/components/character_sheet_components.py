import tkinter as tk
from tkinter import ttk
from database import get_races

# TODO Split 'components' modules into UI Frames per 'primary blocks' of the character sheet

class CharacterHeaderFrame(ttk.Frame):
    """A component for the top character information header."""
    def __init__(self, master, char_vars, **kwargs):
        super().__init__(master, style="characterbackgroundframe.TFrame", padding=5, **kwargs)
        self._build_widgets(char_vars)

    def _build_widgets(self, char_vars):
        # Configure columns & rows of this CharacterHeaderFrame
        self.columnconfigure(0, weight=1) # Name Column
        self.columnconfigure(1, weight=2) # Background Info Column
        self.rowconfigure(0, weight=1)

        # 1x1 Table for Character Name
        characternameframe = ttk.Frame(self)
        characternameframe.grid(column=0, row=0, sticky='ew')
        characternameframe.columnconfigure(0, weight=1)
        characternameframe.rowconfigure(0, weight=1)
        characternameframe.rowconfigure(1, weight=1)
        ttk.Entry(characternameframe, textvariable=char_vars['charactername']).grid(column=0, row=0, sticky='ew')
        ttk.Entry(characternameframe, textvariable=char_vars['characterclass']).grid(column=0, row=1, sticky='ew')

        # 2x3 Table for Background Info Entries
        backgroundinfoframe = ttk.Frame(self)
        backgroundinfoframe.grid(column=1, row=0, sticky='ew')
        backgroundinfoframe.columnconfigure(0, weight=1)
        backgroundinfoframe.columnconfigure(1, weight=1)
        backgroundinfoframe.columnconfigure(2, weight=1)
        backgroundinfoframe.rowconfigure(0, weight=1)
        backgroundinfoframe.rowconfigure(1, weight=1)

        race_options = get_races()

        ttk.Spinbox(backgroundinfoframe, from_=1, to=20, textvariable=char_vars['level']).grid(column=0, row=0, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=char_vars['background']).grid(column=1, row=0, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=char_vars['player_name']).grid(column=2, row=0, sticky='ew')
        ttk.Combobox(backgroundinfoframe, textvariable=char_vars['race'], values=race_options, state="readonly").grid(column=0, row=1, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=char_vars['alignment']).grid(column=1, row=1, sticky='ew')
        ttk.Entry(backgroundinfoframe, textvariable=char_vars['experience_points']).grid(column=2, row=1, sticky='ew')

class AbilityScoreFrame(ttk.Frame):
    """A component for a single ability score block (e.g., Strength)."""
    def __init__(self, master, ability_name, skills_list, score_var, modifier_var, skill_vars_dict, **kwargs):
        super().__init__(master, style='abilityscore.TFrame', **kwargs)
        self._build_widgets(ability_name, skills_list, score_var, modifier_var, skill_vars_dict)

    def _build_widgets(self, ability_name, skills_list, score_var, modifier_var, skill_vars_dict):
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=2)

        # Stat Label, Score, and Modifier Score
        ttk.Label(self, text=ability_name).grid(column=0, row=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=score_var, width=5).grid(column=0, row=1, sticky="w", pady=2)
        ttk.Label(self, textvariable=modifier_var).grid(column=0, row=2, sticky="w", pady=2)

        # Proficiency Checkboxes, Skill Scores, Skill Names
        for j, skill in enumerate(skills_list):
            prof_var = skill_vars_dict[skill]["proficient"]
            ttk.Checkbutton(self, variable=prof_var).grid(column=1, row=j, pady=2)
            ttk.Entry(self).grid(column=2, row=j, pady=2)
            ttk.Label(self, text=skill).grid(column=3, row=j, pady=2)