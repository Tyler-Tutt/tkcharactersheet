import flet as ft

class LoadCharacterDialog(ft.AlertDialog):
    def __init__(self, character_list: list, on_load_confirm, on_cancel):
        # Initialize the parent AlertDialog
        super().__init__(
            modal=True,
            title=ft.Text("Load Character"),
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Save the callback functions
        self.on_load_confirm = on_load_confirm
        self.on_cancel = on_cancel

        # --- Define UI Controls ---
        self.character_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in character_list],
            value=character_list[0] if character_list else None,
            expand=True
        )

        self.content = ft.Container(
            content=self.character_dropdown,
            width=300
        )

        self.actions = [
            ft.TextButton("Load", on_click=self._handle_load),
            ft.TextButton("Cancel", on_click=self._handle_cancel),
        ]

    def _handle_load(self, e):
        """Internal handler to grab the dropdown value and pass it to the controller."""
        selected_character = self.character_dropdown.value
        if selected_character:
            # Trigger the function passed from main_flet.py
            self.on_load_confirm(selected_character)

    def _handle_cancel(self, e):
        """Internal handler for the cancel button."""
        self.on_cancel()