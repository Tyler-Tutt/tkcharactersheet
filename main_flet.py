import flet as ft
from models.character_model import CharacterModel
import database

def main(page: ft.Page):
    # --- 1. Page and Model Setup ---
    page.title = "Flet Character Sheet"
    page.scroll = ft.ScrollMode.ADAPTIVE # Make the whole page scrollable

    # Instantiate the data model
    model = CharacterModel()

    # --- 2. UI Component Functions (We will build these next) ---
    # header = create_character_header(model)
    # ability_scores = create_all_ability_scores(model)

    # --- 3. Page Layout ---
    page.add(
        ft.Text("Character Sheet UI will go here!", size=30)
        # We will add our real components here later
    )

if __name__ == "__main__":
    database.init_db()
    ft.app(target=main)