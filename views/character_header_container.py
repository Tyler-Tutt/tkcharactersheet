import flet as ft

class CharacterHeaderContainer(ft.Container):
    def __init__(self, model, on_header_change):
        # Initialize the parent Container with the styling from your old _create_header
        super().__init__(
            padding=10,
            bgcolor=ft.Colors.RED_200,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8
        )
        
        self.on_header_change = on_header_change

        # --- 1. Define the UI Controls ---
        self.charactername_field = ft.TextField(label="Character Name", value=model.charactername, data="charactername", on_change=self.on_header_change)
        self.class_field = ft.TextField(label="Class", value=model.characterclass, data="characterclass", on_change=self.on_header_change)
        self.level_field = ft.TextField(label="Level", value=str(model.level), data="level", on_change=self.on_header_change)
        self.background_field = ft.TextField(label="Background", value=model.background, data="background", on_change=self.on_header_change)
        self.player_name_field = ft.TextField(label="Player Name", value=model.player_name, data="player_name", on_change=self.on_header_change)
        self.race_field = ft.TextField(label="Race", value=model.race, data="race", on_change=self.on_header_change)
        self.alignment_field = ft.TextField(label="Alignment", value=model.alignment, data="alignment", on_change=self.on_header_change)
        self.experience_points_field = ft.TextField(label="Experience Points", value=str(model.experience_points), data="experience_points", on_change=self.on_header_change)

        # --- 2. Build the Layout ---
        self.content = ft.Row(
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
                            ft.Row(
                                controls=[
                                    self.level_field,
                                    self.background_field,
                                    self.player_name_field,
                                ]
                            ),
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

    def update_header_data(self, model):
        """Called by the main controller when loading a character."""
        self.charactername_field.value = model.charactername
        self.class_field.value = model.characterclass
        self.level_field.value = str(model.level)
        self.background_field.value = model.background
        self.player_name_field.value = model.player_name
        self.race_field.value = model.race
        self.alignment_field.value = model.alignment
        self.experience_points_field.value = str(model.experience_points)
        
        # Tell Flet to redraw ONLY this header card!
        self.update()