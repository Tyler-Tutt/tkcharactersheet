import flet as ft
from controllers.character_sheet_controller import CharacterSheetController
import database

# tells ft.App, "Take the function named main and use it as the blueprint for every new user session"
def main(page: ft.Page):
    # --- Page Setup ---
    page.title = "Flet Character Sheet pew pew"
    page.scroll = ft.ScrollMode.AUTO
    
    # --- Initialize Controller ---
    # The controller handles creating the model and the view
    app_controller = CharacterSheetController(page)

    # --- AppBar ---
    page.appbar = ft.AppBar(
        title=ft.Text("Flet Character Sheet"),
        actions=[
            ft.IconButton(
                icon=ft.Icons.EDIT_OFF, # Start in view mode
                on_click=app_controller.toggle_edit_mode, 
                tooltip="Switch to Edit Mode"
            ),
            ft.IconButton(
                ft.Icons.SAVE, 
                on_click=app_controller.save_character, 
                tooltip="Save Character"
            ),
            ft.IconButton(
                ft.Icons.FOLDER_OPEN, 
                on_click=app_controller.open_load_modal, 
                tooltip="Load Character"
            ),
        ]
    )

    # --- Add View to Page ---
    page.add(app_controller.get_view())
    page.update()

if __name__ == "__main__":
    database.init_db()
    ft.run(main)