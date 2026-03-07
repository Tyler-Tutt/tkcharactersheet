import flet as ft
from models.character_model import CharacterModel
from views.ability_score_container import AbilityScoreContainer
from views.character_header_container import CharacterHeaderContainer

#TODO Layout Ability Score, AC/HP/Speed, and Features Column

class CharacterSheetView(ft.Container):
    # 1. Update __init__ to accept the handler functions
    def __init__(self, model: CharacterModel, on_score_change_handler, on_header_change_handler):
        super().__init__(expand=True)
        self.model = model
        
        # Save the handlers to the class instance so other methods can use them
        self.on_score_change = on_score_change_handler
        self.on_header_change = on_header_change_handler

        # Ability Containers (will be populated in _create_ability_score_containers)
        self.ability_score_containers = []
        
        # Build the UI
        self.content = self.build_ui()

    def build_ui(self):
        '''
        Instantiate UI components
        '''
        self.header = CharacterHeaderContainer(self.model, self.on_header_change)
        self.second_row_container = self._create_second_row_container()
        
        return ft.Column(
            controls=[
                self.header,
                ft.Divider(height=20),
                self.second_row_container,
            ]
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
        containers = []
        for ability_name in self.model.abilities_list:
            ability_data = self.model.ability_scores[ability_name]
            
            # Instantiate our clean new custom component
            card = AbilityScoreContainer(
                ability_name=ability_name,
                initial_score=ability_data["score"],
                skills_data=ability_data["skills"],
                on_score_change=self.on_score_change # Pass the controller's function down
            )
            containers.append(card)
        return containers