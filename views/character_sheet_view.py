import flet as ft
from models.character_model import CharacterModel

class CharacterSheetView(ft.Container):
    def __init__(self, model: CharacterModel):
        super().__init__(expand=True)
        self.model = model
        self.content = self.build()

    def build(self):
        self.header = self._create_character_header()
        self.ability_cards = self._create_ability_cards()
        return ft.Column(
            controls=[
                self.header,
                ft.Divider(height=20),
                ft.Row(
                    # wrap=True,
                    # spacing=10,
                    # run_spacing=10,
                    controls=self.ability_cards
                )
            ]
        )

    def _create_character_header(self):
        """Builds and returns the top header UI as an ft.Container."""
        return ft.Container(
            padding=10,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # --- Left Column wrapped in its own Container ---
                    ft.Container(
                        expand=1,
                        bgcolor=ft.Colors.AMBER_900,
                        padding=5,
                        border_radius=5,
                        content=ft.Column(
                            controls=[
                                ft.TextField(label="Character Name", value=self.model.charactername),
                                ft.TextField(label="Class & Level", value=self.model.characterclass),
                            ]
                        ),
                    ),
                    
                    # --- Right Column wrapped in its own Container ---
                    ft.Container(
                        expand=2,
                        bgcolor=ft.Colors.PURPLE,
                        padding=5,
                        border_radius=5,
                        content=ft.Column(
                            controls=[
                                # First Row in the Right Column
                                ft.Row(
                                    controls=[
                                        ft.TextField(label="Background", value=self.model.background, expand=1),
                                        ft.TextField(label="Player Name", value=self.model.player_name, expand=1),
                                    ]
                                ),
                                # Second Row in the Right Column
                                ft.Row(
                                    controls=[
                                        ft.TextField(label="Race", value=self.model.race, expand=1),
                                        ft.TextField(label="Alignment", value=self.model.alignment, expand=1),
                                        ft.TextField(label="Experience Points", value=self.model.experience_points, expand=1),
                                    ]
                                )
                            ]
                        ),
                    )
                ]
            )
        )

    def _create_ability_cards(self):
        """Creates the UI for all ability scores."""
        cards = []
        for ability_name in self.model.abilities_list:
            card = self._create_ability_score_card(ability_name)
            cards.append(card)
        return cards

    def _create_ability_score_card(self, ability_name: str):
        """Builds the UI for a single ability score."""
        ability_data = self.model.scores[ability_name]
        skills_map = self.model.skills_map[ability_name]

        score_field = ft.TextField(
            value=str(ability_data["score"]),
            text_align=ft.TextAlign.CENTER,
            width=100,
            data=ability_name  # The controller will use this
        )

        modifier_text = ft.Text(self.model.get_modifier_for(ability_name), size=20)

        skills_controls = []
        for skill in skills_map:
            skills_controls.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(label=skill, value=ability_data["skills"][skill]["proficient"]),
                    ]
                )
            )

        return ft.Container(
            # width=250,
            padding=10,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(ability_name.upper(), size=16, weight=ft.FontWeight.BOLD),
                    score_field,
                    modifier_text,
                    ft.Divider(),
                    *skills_controls
                ]
            ),
            # Store references to controls that need to be updated by the controller
            data={"score_field": score_field, "modifier_text": modifier_text}
        )