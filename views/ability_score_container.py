import flet as ft

class AbilityScoreContainer(ft.Container):
    def __init__(self, ability_name: str, initial_score: int, skills_data: dict, on_score_change):
        super().__init__(
            padding=10,
            bgcolor=ft.Colors.LIGHT_GREEN,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8
        )
        self.ability_name = ability_name
        self.on_score_change = on_score_change  # Callback to notify the controller
        
        # --- Internal UI Elements ---
        self.ability_name_text = ft.Text(ability_name.upper(), size=16, weight=ft.FontWeight.BOLD)
        self.modifier_text = ft.Text(self._calc_modifier_str(initial_score), size=20)
        self.score_field = ft.TextField(
            value=str(initial_score),
            text_align=ft.TextAlign.CENTER,
            width=100,
            on_change=self._internal_score_change
        )
        
        # --- Build Skills UI ---
        self.skills_controls = []
        for skill_name, skill_info in skills_data.items():
            self.skills_controls.append(
                ft.Row(
                    controls=[
                        # Note: You'll eventually want to add an on_change handler here for the checkbox too!
                        ft.Checkbox(value=skill_info["proficient"]),
                        ft.TextField(width=50),
                        ft.Text(skill_name, selectable=True)
                    ]
                )
            )
            
        # --- Layout ---
        self.content = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.ability_name_text, self.modifier_text, self.score_field]
                ),
                ft.Column(controls=self.skills_controls)
            ]
        )

    def _calc_modifier_str(self, score: int) -> str:
        """Helper to calculate the + or - modifier string."""
        modifier = (score - 10) // 2
        return f"+{modifier}" if modifier >= 0 else str(modifier)

    def _internal_score_change(self, e: ft.ControlEvent):
        """Handles the text field change internally, updates its own UI, then notifies the controller."""
        raw_value = e.control.value
        try:
            # Handle empty strings gracefully
            new_score = int(raw_value) if raw_value != "" else 0
        except ValueError:
            new_score = 10
            self.score_field.value = str(new_score)

        # 1. Update this specific component's UI instantly
        self.modifier_text.value = self._calc_modifier_str(new_score)
        self.update() # ONLY updates this card! Very fast.
        
        # 2. Tell the main controller the data changed so it can update the Model
        if self.on_score_change:
            self.on_score_change(self.ability_name, new_score)

    def update_card_data(self, new_score: int, new_skills_data: dict):
        """Called by the main controller when loading a character from the database."""
        self.score_field.value = str(new_score)
        self.modifier_text.value = self._calc_modifier_str(new_score)
        
        # TODO: Update the skill checkboxes here based on new_skills_data
        
        self.update()