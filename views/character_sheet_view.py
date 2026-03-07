import flet as ft
from models.character_model import CharacterModel
from views.ability_score_container import AbilityScoreContainer

#TODO Layout Ability Score, AC/HP/Speed, and Features Column

class CharacterSheetView(ft.Container):
    # 1. Update __init__ to accept the handler functions
    def __init__(self, model: CharacterModel, on_score_change_handler, on_header_change_handler):
        super().__init__(expand=True)
        self.model = model
        
        # Save the handlers to the class instance so other methods can use them
        self.on_score_change = on_score_change_handler
        self.on_header_change = on_header_change_handler

        # --- Store references to controls that need to be updated ---
        # 2. Bind the header handler immediately by passing on_change=self.on_header_change
        self.charactername_field = ft.TextField(label="Character Name", value=self.model.charactername, data="charactername", on_change=self.on_header_change)
        self.class_field = ft.TextField(label="Class", value=self.model.characterclass, data="characterclass", on_change=self.on_header_change)
        self.level_field = ft.TextField(label="Level", value=str(self.model.level), data="level", on_change=self.on_header_change)
        self.background_field = ft.TextField(label="Background", value=self.model.background, data="background", on_change=self.on_header_change)
        self.player_name_field = ft.TextField(label="Player Name", value=self.model.player_name, data="player_name", on_change=self.on_header_change)
        self.race_field = ft.TextField(label="Race", value=self.model.race, data="race", on_change=self.on_header_change)
        self.alignment_field = ft.TextField(label="Alignment", value=self.model.alignment, data="alignment", on_change=self.on_header_change)
        self.experience_points_field = ft.TextField(label="Experience Points", value=str(self.model.experience_points), data="experience_points", on_change=self.on_header_change)

        # Ability Containers (will be populated in _create_ability_score_containers)
        self.ability_score_containers = []
        
        # Build the UI
        self.content = self.build_ui()

    def build_ui(self):
        self.header = self._create_header_container()
        self.second_row_container = self._create_second_row_container()
        return ft.Column(
            controls=[
                self.header,
                ft.Divider(height=20),
                self.second_row_container,
                ft.Row(
                    # wrap=True,
                    # spacing=10,
                    # run_spacing=10,
                    # controls=self.ability_cards
                )
            ]
        )

    def _create_header_container(self):
        """Builds and returns the top header Container"""
        # --- We already defined the fields in __init__, so we just use them here ---
        return ft.Container(
            padding=10,
            bgcolor=ft.Colors.RED_200,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # --- Name & Class Container ---
                    ft.Container(
                        expand=1,
                        bgcolor=ft.Colors.AMBER_900,
                        padding=5,
                        border_radius=5,
                        content=ft.Column(
                            controls=[
                                self.charactername_field,
                                self.class_field,
                            ]
                        ),
                    ),
                    
                    # --- Background Header Column ---
                    ft.Container(
                        expand=2,
                        bgcolor=ft.Colors.PURPLE,
                        padding=5,
                        border_radius=5,
                        content=ft.Column(
                            controls=[
                                # First Row of Background Header
                                ft.Row(
                                    controls=[
                                        self.level_field,
                                        self.background_field,
                                        self.player_name_field,
                                    ]
                                ),
                                # Second Row of Background Header
                                ft.Row(
                                    controls=[
                                        self.race_field,
                                        self.alignment_field,
                                        self.experience_points_field,
                                    ]
                                )
                            ]
                        ),
                    )
                ]
            )
        )

    def _create_second_row_container(self):
        "Builds and returns a container with a row which has 3 Columns"
        # --- Populate the self.ability_cards list ---
        self.ability_score_containers = self._create_ability_score_containers()
        return ft.Container(
            bgcolor=ft.Colors.LIGHT_BLUE,
            border=ft.border.all(2),
            padding=5,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[

                    # --- Ability Score Column ---
                    ft.Container(
                        expand=1,
                        padding=10,
                        bgcolor=ft.Colors.GREY,
                        content=ft.Column(
                            controls=[
                                *self.ability_score_containers  # Unpack the list of containers
                            ]
                        )
                    ),

                    # --- AC/HP/Speed Column ---
                    ft.Container(
                        expand=1,
                        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_200,
                        content=ft.Column(
                            controls=[
                                ft.Text("AC/HP/Speed")
                            ]
                        )
                    ),

                    # --- Features & Traits Column ---
                    ft.Container(
                        expand=1,
                        bgcolor=ft.Colors.GREY,
                        content=ft.Column(
                            controls=[
                                ft.Text("Features & Traits")
                            ]
                        )
                    )
                ]
            )
        )

    def _create_ability_score_containers(self):
        """Builds the ft.Container for each ability score using the AbilityScoreContainer component."""
        cards = []
        for ability_name in self.model.abilities_list:
            ability_data = self.model.ability_scores[ability_name]
            
            # Instantiate our clean new custom component
            card = AbilityScoreContainer(
                ability_name=ability_name,
                initial_score=ability_data["score"],
                skills_data=ability_data["skills"],
                on_score_change=self.on_score_change # Pass the controller's function down
            )
            cards.append(card)
        return cards