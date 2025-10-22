import flet as ft
from models.character_model import CharacterModel
from views.character_sheet_view import CharacterSheetView
import database

def main(page: ft.Page):
    # --- Page and Model Setup ---
    page.title = "Flet Character Sheet"
    page.scroll = ft.ScrollMode.ADAPTIVE
    # page.window.maximized = True

    model = CharacterModel()

    # --- Build UI View (created ONCE) ---
    view = CharacterSheetView(model)

    # --- Controller Logic / Event Handlers ---

    def on_header_change(e: ft.ControlEvent):
        """
        A generic handler for all header TextFields.
        Updates the corresponding attribute in the model.
        """
        attr_name = e.control.data  # e.g., "charactername", "level", "race"
        new_value = e.control.value

        # --- Good Practice: Validate and convert type ---
        # Get the old value from the model as a default
        old_value = getattr(model, attr_name, None)
        
        # Try to convert to int for numeric fields
        if attr_name in ['level', 'experience_points', 'armor_class', 'initiative', 'speed', 'max_hp', 'current_hp', 'temp_hp']:
            try:
                new_value = int(new_value)
            except (ValueError, TypeError):
                new_value = old_value # Revert to old value if invalid input
                e.control.value = str(old_value) # Fix the UI
        
        # Update the model attribute
        setattr(model, attr_name, new_value)
        # No page.update() needed, as the TextField already shows the new value.

    def on_score_change(e: ft.ControlEvent):
        """Handles changes to any ability score TextField."""
        ability_name = e.control.data
        try:
            new_score = int(e.control.value)
            model.scores[ability_name]["score"] = new_score
        except (ValueError, TypeError):
            new_score = 10 # Default
            model.scores[ability_name]["score"] = new_score
            e.control.value = str(new_score) # Fix the UI

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
        # --- MUCH SIMPLER! ---
        # The model is already up-to-date thanks to the on_change handlers.
        if model.save():
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {model.charactername}!"), open=True)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Save failed. Check character name."), open=True)
        page.update()

    def update_view_from_model(model_data: CharacterModel, view_controls: CharacterSheetView):
        """
        Updates all controls in the view to match the model's data.
        This is the core of the state management for loading.
        """
        # 1. Update Header Fields
        view_controls.charactername_field.value = model_data.charactername
        view_controls.class_field.value = model_data.characterclass
        view_controls.level_field.value = str(model_data.level)
        view_controls.background_field.value = model_data.background
        view_controls.player_name_field.value = model_data.player_name
        view_controls.race_field.value = model_data.race
        view_controls.alignment_field.value = model_data.alignment
        view_controls.experience_points_field.value = str(model_data.experience_points)

        # 2. Update Ability Scores and Modifiers
        for card in view_controls.ability_cards:
            ability_name_text = card.data["ability_name_text"].value.capitalize()
            if ability_name_text in model_data.scores:
                # Get data from the (now loaded) model
                ability_data = model_data.scores[ability_name_text]
                modifier_str = model_data.get_modifier_for(ability_name_text)

                # Get the view controls from the card's data dict
                score_field = card.data["score_field"]
                modifier_text = card.data["modifier_text"]

                # Set the view control values
                score_field.value = str(ability_data["score"])
                modifier_text.value = modifier_str
        
        # 3. TODO: Update other UI elements as you add them
        # (e.g., skill proficiencies, HP, etc.)
        print(f"View updated from model for {model_data.charactername}")


    def open_load_dialog(e):
        """Opens a dialog to load a character."""
        character_list = database.get_character_list()

        def load_and_close(e):
            char_to_load = character_dropdown.value
            if char_to_load:
                # 1. Load data into the existing model
                if model.load(char_to_load):
                    
                    # --- THIS IS THE KEY CHANGE ---
                    # 2. Update the existing view from the model
                    #    (No more rebuilding!)
                    update_view_from_model(model, view)
                    # --- END OF KEY CHANGE ---
                    
                    page.dialog.open = False
                    page.snack_bar = ft.SnackBar(ft.Text(f"Loaded {char_to_load}!"), open=True)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Failed to load {char_to_load}."), open=True)
                
                page.update() # Update to close dialog and show snackbar
            else:
                page.dialog.open = False
                page.update()


        character_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in character_list],
            value=character_list[0] if character_list else None,
            expand=True
        )

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Load Character"),
            content=ft.Container(
                content=character_dropdown,
                width=300
            ),
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
        # 1. Connect Ability Score handlers
        for card in view_instance.ability_cards:
            score_field = card.data["score_field"]
            score_field.on_change = on_score_change

        # 2. Connect Header handlers
        view_instance.charactername_field.on_change = on_header_change
        view_instance.class_field.on_change = on_header_change
        view_instance.level_field.on_change = on_header_change
        view_instance.background_field.on_change = on_header_change
        view_instance.player_name_field.on_change = on_header_change
        view_instance.race_field.on_change = on_header_change
        view_instance.alignment_field.on_change = on_header_change
        view_instance.experience_points_field.on_change = on_header_change

    # --- 4. Page Setup and Final Layout ---
    page.appbar = ft.AppBar(
        title=ft.Text("Flet Character Sheet"),
        actions=[
            ft.IconButton(ft.Icons.SAVE, on_click=save_character, tooltip="Save Character"),
            ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=open_load_dialog, tooltip="Load Character"),
        ]
    )

    # Add the view to the page and connect handlers (all done once at start)
    page.add(view)
    connect_event_handlers(view)
    page.update()

if __name__ == "__main__":
    database.init_db()
    ft.app(target=main)
