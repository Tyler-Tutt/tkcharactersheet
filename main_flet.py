import flet as ft
from models.character_model import CharacterModel
from views.character_sheet_view import CharacterSheetView
import database

#TODO Fix Saving & Loading functionality
#TODO Add Keybinds https://flet.dev/docs/cookbook/keyboard-shortcuts

def main(page: ft.Page):
    # --- Page and Model Setup ---
    page.title = "Flet Character Sheet"
    page.scroll = ft.ScrollMode.ADAPTIVE
    # page.window.maximized = True

    model = CharacterModel()

    # --- Build UI View ---
    view = CharacterSheetView(model)

    # --- Controller Logic / Event Handlers ---
    def on_score_change(e: ft.ControlEvent):
        """Handles changes to any ability score TextField."""
        ability_name = e.control.data
        try:
            new_score = int(e.control.value)
            model.scores[ability_name]["score"] = new_score
        except (ValueError, TypeError):
            model.scores[ability_name]["score"] = 10 # Revert to default

        # Update the UI
        new_modifier = model.get_modifier_for(ability_name)
        for card in view.ability_cards:
            # Access the ability name Text-control directly from data
            card_ability_name_text = card.data["ability_name_text"]
            card_ability_name = card_ability_name_text.value

            if card_ability_name.lower() == ability_name.lower():
                # Access the modifier Text-control directly from data
                modifier_text_control = card.data["modifier_text"]
                modifier_text_control.value = new_modifier
                break
        page.update()

    def save_character(e):
        """Saves the current character data."""
        # Get charactername from the header's TextField directly
        model.charactername = view.charactername.value
        #TODO continue to update the rest of the model's fields here
        
        if model.save():
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {model.charactername}!"), open=True)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Save failed. Check character name."), open=True)
        page.update()

    def open_load_dialog(e):
        """Opens a dialog to load a character."""
        character_list = database.get_character_list()

        def load_and_close(e):
            char_to_load = character_dropdown.value
            # Inside load_and_close
            if char_to_load:
                model.load(char_to_load)
                # Create the new view with the loaded model data
                new_view = CharacterSheetView(model) 

                # --- More Robust Way (Alternative) ---
                # Find the existing view and update its content 
                # (Requires finding the view if not always at index 0)
                for i, ctrl in enumerate(page.controls):
                    if isinstance(ctrl, CharacterSheetView):
                        page.controls[i] = new_view # Replace the old instance
                        break 
                else: # If not found (shouldn't happen here)
                    page.add(new_view) # Add if somehow missing

                # # --- Current Way (Works but is fragile) ---
                # if page.controls and isinstance(page.controls[0], CharacterSheetView):
                #     page.controls[0] = new_view # Assumes the view is the first control
                # else:
                #     print("Error: Could not find CharacterSheetView to replace.")
                #     # Handle error appropriately, maybe just add the new view
                #     page.add(new_view)

                # You MUST reconnect handlers to the controls WITHIN the new_view
                connect_event_handlers(new_view) 
                page.dialog.open = False
                page.update()

        character_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in character_list],
            value=character_list[0] if character_list else None
        )

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Load Character"),
            content=character_dropdown,
            actions=[
                ft.TextButton("Load", on_click=load_and_close),
                ft.TextButton("Cancel", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    def connect_event_handlers(view_instance: CharacterSheetView):
        """Connects event handlers to the controls in the view."""
        for card in view_instance.ability_cards:
            score_field = card.data["score_field"]
            score_field.on_change = on_score_change

    # --- 4. Page Setup and Final Layout ---
    page.appbar = ft.AppBar(
        title=ft.Text("Flet Character Sheet"),
        actions=[
            ft.IconButton(ft.Icons.SAVE, on_click=save_character, tooltip="Save Character"),
            ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=open_load_dialog, tooltip="Load Character"),
        ]
    )

    # Add the view to the page and connect handlers
    page.add(view)
    connect_event_handlers(view)
    page.update()

if __name__ == "__main__":
    database.init_db()
    ft.app(target=main)