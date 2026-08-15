import flet as ft
from models import CharacterModel, InventoryItem
from views.character_sheet_view import CharacterSheetView
from views.load_character_modal import LoadCharacterModal
import database
from events import PubSubTopic, UIAction

class CharacterSheetController:
    '''
    The central orchestrator that manages the flow of data between the character model and the user interface. 
    It translates user interactions into model updates and ensures the view reflects the most current state.
    '''
    def __init__(self, page: ft.Page):
        '''
        Initializes the Controller by linking the Flet page, instantiating the data model, and creating the main character sheet view. 
        Also sets the initial application state, starting the user in a non-editable viewing mode.
        '''
        self.page = page
        self.model = CharacterModel()
        self.is_edit_mode = False
        
        # --- Dispatch Dictionary ---
        # Map the incoming action strings to the private-methods that handle them.
        self._action_handlers = {
            UIAction.UPDATE_HEADER: self._handle_update_header,
            UIAction.TOGGLE_PROFICIENCY: self._handle_toggle_proficiency,
            UIAction.UPDATE_ABILITY: self._handle_update_ability,
            UIAction.ADD_ITEM: self._handle_add_item,
            UIAction.TOGGLE_ATTUNEMENT: self._handle_toggle_attunement
        }
        
        self.view = CharacterSheetView(model=self.model)

        # Whenever a message comes across the UI_ACTION "frequency", 
        # trigger the 'handle_subscribe_topic_ui_action' function
        self.page.pubsub.subscribe_topic(
            PubSubTopic.UI_ACTION, 
            self.handle_subscribe_topic_ui_action
        )

    def toggle_edit_mode(self, e):
        '''
        Switches the application between read-only and editable state by updating the is_edit_mode flag. 
        Dynamically modifies UI elements like icons and tooltips while providing visual feedback to the user via a SnackBar.
        '''
        self.is_edit_mode = not self.is_edit_mode

        # Broadcast the edit mode change globally
        self.page.pubsub.send_all_on_topic(PubSubTopic.EDIT_MODE_CHANGED, self.is_edit_mode)
        
        e.control.icon = ft.Icons.EDIT if self.is_edit_mode else ft.Icons.EDIT_OFF
        e.control.tooltip = "Switch to View Mode" if self.is_edit_mode else "Switch to Edit Mode"
        e.control.update()

        self.page.appbar.bgcolor = ft.Colors.AMBER_300 if self.is_edit_mode else None
        self.page.appbar.update()
        
        mode_text = "Edit Mode" if self.is_edit_mode else "Viewing Mode"
        self.page.show_dialog(ft.SnackBar(ft.Text(mode_text), duration=1500))

    def get_view(self):
        '''
        Getter method that returns the top-level CharacterSheetView component managed by the controller. 
        '''
        return self.view

    # --- Central Routing Engine (Radio Tower) ---
    def handle_subscribe_topic_ui_action(self, topic: str, message: dict):
        """Listens for actions broadcasted by UI components, routes them, and triggers a UI refresh."""
        # Flet passes two things:
        # topic = "ui_action" 
        # message = {"action": UIAction.UPDATE_HEADER, "attr": "charactername", "value": "Thorin"}
        action = message.get("action") # extracts UIAction.UPDATE_HEADER
        
        # Looks up the matching method in the Dispatch Dictionary based on string returned in action
        handler_method = self._action_handlers.get(action)
        
        if handler_method:
            # If the method exists, execute it and pass the message payload
            handler_method(message) # Forwards the payload to _handle_update_header
            
            # After a successful update, tell the entire app that the model has changed
            self.page.pubsub.send_all_on_topic(PubSubTopic.MODEL_UPDATED, "update")
        else:
            # Gracefully handle typos or unimplemented actions
            print(f"Warning: Unrecognized UI action '{action}'")

    # --- 3. The Isolated Action Handlers ---
    
    def _handle_update_header(self, message: dict):
        attr_name = message["attr"]
        new_value = message["value"]
        old_value = getattr(self.model, attr_name, None)
        
        if attr_name in ['level', 'experience_points', 'speed', 'max_hp', 'current_hp', 'temp_hp']:
            try:
                new_value = int(new_value)
            except (ValueError, TypeError):
                new_value = old_value 
        
        if attr_name == 'speed':
            self.model.base_speed = new_value
        else:
            setattr(self.model, attr_name, new_value)

    def _handle_toggle_proficiency(self, message: dict):
        ability_name = message["ability"]
        skill_name = message["skill"]
        self.model.ability_scores_list[ability_name].skills[skill_name].base_proficiency = message["is_proficient"]

    def _handle_update_ability(self, message: dict):
        ability_name = message["ability"]
        if ability_name in self.model.ability_scores_list:
            self.model.ability_scores_list[ability_name].base_score = message["score"]

    def _handle_add_item(self, message: dict):
        item_name = message["item_name"]
        item_data = database.fetch_item(item_name)
        
        if item_data:
            new_item = InventoryItem(
                name=item_data.get("name", item_name),
                category=item_data.get("category", "Gear"),
                rarity=item_data.get("rarity", "Common"),
                requires_attunement=item_data.get("requires_attunement", False),
                description=item_data.get("description", ""),
                short_description=item_data.get("short_description", ""), 
                modifiers=item_data.get("modifiers", [])
            )
            self.model.inventory.append(new_item)
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Added {item_name} to inventory!")))
        else:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Item {item_name} not found in database."), bgcolor=ft.Colors.ERROR))

    def _handle_toggle_attunement(self, message: dict):
        item_index = message["index"]
        self.model.inventory[item_index].is_active = message["is_active"]
        self.model.update_active_modifiers()

    # --- External Save/Load ---
    def save_character(self, e):
        if not self.model.charactername or self.model.charactername == "Character Name":
            self.page.show_dialog(ft.SnackBar(ft.Text("Save failed. Check character name."), bgcolor=ft.Colors.ERROR))
            return

        character_data = self.model.convert_to_dictionary()
        database.save_character(self.model.charactername, character_data)
        self.page.show(ft.SnackBar(ft.Text(f"Saved {self.model.charactername}!"), bgcolor=ft.Colors.GREEN_700))

    def open_load_modal(self, e):
        '''
        Retrieves the list of saved characters from the database and presents them in a selection dialog. 
        '''
        character_list = database.fetch_character_list()

        def handle_load(char_to_load):
            char_data = database.fetch_character(char_to_load)
            if char_data and self.model.load_from_dictionary(char_data):
                self.page.pubsub.send_all_on_topic(PubSubTopic.MODEL_UPDATED, "load")
                self.page.close(modal) 
                self.page.show_dialog(ft.SnackBar(ft.Text(f"Loaded {char_to_load}!"))) 
            else:
                self.page.show_dialog(ft.SnackBar(ft.Text(f"Failed to load {char_to_load}.")))

        def handle_cancel():
            self.page.close_dialog(modal)

        modal = LoadCharacterModal(character_list=character_list, on_load_confirm=handle_load, on_cancel=handle_cancel)
        self.page.show_dialog(modal)