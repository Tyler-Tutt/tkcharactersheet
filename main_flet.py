import flet as ft
from models.character_model import CharacterModel
import database

def main(page: ft.Page):
    # --- 1. Page and Model Setup ---
    page.title = "Flet Character Sheet"
    page.scroll = ft.ScrollMode.ADAPTIVE # Make the whole page scrollable
    model = CharacterModel() # Instantiate the data model

    # --- 2. Build UI Components ---
    header = create_character_header(model)
    
    # Create a list of all ability score cards
    ability_cards = []
    for ability_name in model.abilities_list:
        ability_cards.append(create_ability_score_card(model, ability_name))

    # --- 3. Page Layout ---
    page.add(
        # The top header section
        header,
        ft.Divider(height=20),
        # A row for the main content areas
        ft.Row(
            # Use a Wrap control to let cards flow to the next line if space is tight
            controls=[ft.Wrap(spacing=10, run_spacing=10, controls=ability_cards)],
            # In a later step, you'd add the middle and right columns here
        )
    )

def create_character_header(model: CharacterModel):
    """Builds and returns the top header UI as an ft.Container."""
    return ft.Container(
        padding=10,
        # border=ft.border.all(2, ft.colors.OUTLINE),
        border_radius=8,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # Left side: Character Name and Class
                ft.Column(
                    controls=[
                        ft.TextField(label="Character Name", value=model.charactername, width=250),
                        ft.TextField(label="Class & Level", value=model.characterclass, width=250),
                    ]
                ),
                # Right side: Background, Player Name, etc.
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.TextField(label="Background", value=model.background, expand=True),
                                ft.TextField(label="Player Name", value=model.player_name, expand=True),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.TextField(label="Race", value=model.race, expand=True),
                                ft.TextField(label="Alignment", value=model.alignment, expand=True),
                                ft.TextField(label="Experience Points", value=model.experience_points, expand=True),
                            ]
                        )
                    ]
                )
            ]
        )
    )

def create_ability_score_card(model: CharacterModel, ability_name: str):
    """Builds the UI for a single ability score."""
    # Create a list of Flet controls for the skills
    skills_controls = []
    ability_data = model.scores[ability_name]
    skills_map = model.skills_map[ability_name]

    for skill in skills_map:
        skills_controls.append(
            ft.Row(
                controls=[
                    ft.Checkbox(label=skill, value=ability_data["skills"][skill]["proficient"]),
                    # In a later step, you'd add the skill modifier here
                ]
            )
        )

    return ft.Container(
        width=250,
        padding=10,
        # border=ft.border.all(2, ft.colors.OUTLINE),
        border_radius=8,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(ability_name.upper(), size=16, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    value=ability_data["score"],
                    text_align=ft.TextAlign.CENTER,
                    width=100,
                    # In a later step, the on_change event here will update the model
                ),
                ft.Text(model.get_modifier_for(ability_name), size=20),
                ft.Divider(),
                # Add all the skill Checkboxes we created above
                *skills_controls 
            ]
        )
    )
if __name__ == "__main__":
    database.init_db()
    ft.app(target=main)

