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
    
    # --- Controller Logic / Event Handlers ---
    def on_score_change(e: ft.ControlEvent):
        """
        This function is called whenever any ability score TextField changes.
        """
        # 1. Get which ability changed from the control's data
        ability_name = e.control.data
        
        # 2. Update the Model
        try:
            new_score = int(e.control.value)
            model.scores[ability_name]["score"] = new_score
        except (ValueError, TypeError):
            # Handle cases where the input is not a valid number
            model.scores[ability_name]["score"] = 10 # or some default

        # 3. Update the UI
        # Recalculate the modifier from the model
        new_modifier = model.get_modifier_for(ability_name)
        
        # Find the modifier_text control that needs updating.
        # We look through all our built cards to find the right one.
        for card in ability_cards:
            # The card's content is a Column, and its first child is the name
            card_ability_name_control = card.content.controls[0]
            if card_ability_name_control.value.lower() == ability_name.lower():
                # We stored the modifier text control in the card's data
                modifier_text_control = card.data["modifier_text"]
                modifier_text_control.value = new_modifier
                break # Stop searching once found
                
        # 4. Tell Flet to redraw the page
        page.update()

    # --- Build UI Components (pass the handler to the constructor) ---
    ability_cards = []
    for ability_name in model.abilities_list:
        card = create_ability_score_card(model, ability_name, on_score_change)
        ability_cards.append(card)

    # --- 3. Page Layout ---
    page.add(
        # The top header section
        header,
        ft.Divider(height=20),
        # A row for the main content areas
        ft.Row(
            # Use a Wrap control to let cards flow to the next line if space is tight
            controls=[
                ft.Row(
                    wrap=True, 
                    spacing=10, 
                    run_spacing=10, 
                    controls=ability_cards
                )
            ],
            # In a later step, you'd add the middle and right columns here
        )
    )

    def save_character(e):
        # First, update the model with the latest data from UI fields
        model.character_name = header.content.controls[0].controls[0].value
        # ... update ALL other model fields from their respective UI controls ...
        
        # Then, call the model's save method
        if model.save():
            page.snack_bar = ft.SnackBar(ft.Text(f"Saved {model.character_name}!"), open=True)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Save failed. Check name."), open=True)
        page.update()

    def open_load_dialog(e):
        character_list = database.get_character_list()
        
        def load_and_close(e):
            # The character name is stored in the dropdown's value
            char_to_load = character_dropdown.value
            if char_to_load:
                model.load(char_to_load)
                # This is a key part: you must now rebuild the UI
                # or manually update every single control on the page
                # with the new model data.
                # For simplicity, we can do a full page refresh.
                page.clean() # Remove all controls
                build_page_layout() # A new function to rebuild the UI
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

    # --- Page Setup ---
    # Add an AppBar to the page for global actions
    page.appbar = ft.AppBar(
        title=ft.Text("Flet Character Sheet"),
        actions=[
            ft.IconButton(ft.Icons.SAVE, on_click=save_character, tooltip="Save Character"),
            ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=open_load_dialog, tooltip="Load Character"),
        ]
    )

    # --- UI Building and Layout ---
    # Refactor the UI building into its own function for clarity and reusability
    def build_page_layout():
        # This is the same code you had before for creating header, cards, etc.
        # It's now inside a function so we can call it again after loading.
        global header, ability_cards # Make controls accessible to handlers
        header = create_character_header(model)
        ability_cards = []
        for ability_name in model.abilities_list:
            card = create_ability_score_card(model, ability_name, on_score_change)
            ability_cards.append(card)
        
        page.add(
            header,
            ft.Divider(height=20),
            ft.Row(controls=[ft.Row(wrap=True, controls=ability_cards)])
        )

    # Initial build of the page
    build_page_layout()
    page.update() # Make sure the initial layout is drawn

def create_character_header(model: CharacterModel):
    """Builds and returns the top header UI as an ft.Container."""
    return ft.Container(
        padding=10,
        border=ft.border.all(2, ft.Colors.OUTLINE),
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

def create_ability_score_card(model: CharacterModel, ability_name: str, on_score_change):
    """Builds the UI for a single ability score."""
    
    # Get references to the specific data for this ability
    ability_data = model.scores[ability_name]
    skills_map = model.skills_map[ability_name]
    
    # --- Create Controls with References ---
    # We need to access these controls later to update them
    score_field = ft.TextField(
        value=str(ability_data["score"]), # TextFields always use strings
        text_align=ft.TextAlign.CENTER,
        width=100,
        # Assign the handler function passed into this component
        on_change=on_score_change,
        # Store the ability name in the control's data attribute
        # so the handler knows which ability changed.
        data=ability_name 
    )

    modifier_text = ft.Text(model.get_modifier_for(ability_name), size=20)
    
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
        border=ft.border.all(2, ft.Colors.OUTLINE),
        border_radius=8,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(ability_name.upper(), size=16, weight=ft.FontWeight.BOLD),
                score_field, # Use the control we just created
                modifier_text, # Use the control we just created
                ft.Divider(),
                *skills_controls 
            ]
        ),
        # Store the controls we might need to update in this component's data attribute
        data={"score_field": score_field, "modifier_text": modifier_text}
    )

if __name__ == "__main__":
    database.init_db()
    ft.app(target=main)

