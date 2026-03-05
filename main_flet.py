import flet as ft
from models.character_model import CharacterModel
from views.character_sheet_view import CharacterSheetView
import database

def main(page: ft.Page):
    # --- Page and Model Setup ---
    page.title = "Flet Character Sheet"
    page.scroll = ft.ScrollMode.AUTO
    # page.window.maximized = True

    model = CharacterModel()

    # --- 1. Define Controller Logic / Event Handlers FIRST ---
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
            model.ability_scores[ability_name]["score"] = new_score
        except (ValueError, TypeError):
            new_score = 10 # Default
            model.ability_scores[ability_name]["score"] = new_score
            e.control.value = str(new_score) # Fix the UI

        # Update the UI
        new_modifier = model.calc_ability_modifier(ability_name)
        for card in view.ability_score_containers:
            # Access the ability name Text-control directly from data
            card_ability_name_text = card.data["ability_name_text"]
            card_ability_name = card_ability_name_text.value

            if card_ability_name.lower() == ability_name.lower():
                # Access the modifier Text-control directly from data
                modifier_text_control = card.data["modifier_text"]
                modifier_text_control.value = new_modifier
                break
        page.update()

    # --- 2. Build UI View SECOND (pass handlers as arguments) ---
    view = CharacterSheetView(model, on_score_change, on_header_change)

    # --- 3. Other Application Logic ---
    def save_character(e):
        """Saves the current character data."""
        if model.save_character():
            page.open(
                ft.SnackBar(
                    ft.Text(f"Saved {model.charactername}!"), 
                    bgcolor=ft.Colors.GREEN_700
                )
            )
        else:
            page.open(
                ft.SnackBar(
                    ft.Text("Save failed. Check character name."), 
                    bgcolor=ft.Colors.ERROR
                )
            )

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
        for card in view_controls.ability_score_containers:
            ability_name_text = card.data["ability_name_text"].value.capitalize()
            if ability_name_text in model_data.ability_scores:
                # Get data from the (now loaded) model
                ability_data = model_data.ability_scores[ability_name_text]
                modifier_str = model_data.calc_ability_modifier(ability_name_text)

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
                if model.load_character(char_to_load):
                    
                    # 2. Update the existing view from the model
                    update_view_from_model(model, view)
                    
                    # Modern Flet: Close the dialog
                    page.close(dialog) 
                    
                    # Modern Flet: Open the SnackBar
                    page.open(ft.SnackBar(ft.Text(f"Loaded {char_to_load}!"))) 
                else:
                    page.open(ft.SnackBar(ft.Text(f"Failed to load {char_to_load}.")))
            else:
                page.close(dialog)

        character_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in character_list],
            value=character_list[0] if character_list else None,
            expand=True
        )

        # Define the dialog as a local variable rather than assigning to page.dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Load Character"),
            content=ft.Container(
                content=character_dropdown,
                width=300
            ),
            actions=[
                ft.TextButton("Load", on_click=load_and_close),
                # Use page.close() for the cancel button as well
                ft.TextButton("Cancel", on_click=lambda e: page.close(dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Modern Flet: Open the dialog directly (handles updates and overlays automatically)
        page.open(dialog)

    # Note: connect_event_handlers() has been entirely deleted!

    # --- 4. Page Setup and Final Layout ---
    page.appbar = ft.AppBar(
        title=ft.Text("Flet Character Sheet"),
        actions=[
            ft.IconButton(ft.Icons.SAVE, on_click=save_character, tooltip="Save Character"),
            ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=open_load_dialog, tooltip="Load Character"),
        ]
    )

    # Add the view to the page. 
    # Because you will bind the events inside the View class, Flet handles them immediately.
    page.add(view)
    page.update()

if __name__ == "__main__":
    database.init_db()
    ft.app(target=main)