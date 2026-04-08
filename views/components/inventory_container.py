import flet as ft
from models import CharacterModel
from events import PubSubTopic, UIAction

class InventoryContainer(ft.Container):
    def __init__(self, model: CharacterModel):
        super().__init__(
            padding=10,
            bgcolor=ft.Colors.GREY_800,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8
        )
        self.model = model
        self.item_list_column = ft.Column()
        
        self.add_test_item_btn = ft.ElevatedButton(
            text="Loot 'Cloak of Protection'", 
            on_click=self._add_test_item
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Inventory & Attunement", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                self.add_test_item_btn,
                ft.Divider(),
                self.item_list_column
            ]
        )
        self.update_inventory_ui()

        # Initialize the component in View Mode
        self.set_edit_mode(is_edit=False)

    # --- Pub/Sub Subscriptions ---
    def did_mount(self):
        self.page.pubsub.subscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_inventory_ui)
        self.page.pubsub.subscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_inventory_ui)
        self.page.pubsub.unsubscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    # --- Action Publishers ---
    def _add_test_item(self, e):
        e.page.pubsub.send_all_on_topic(PubSubTopic.UI_ACTION, {"action": "add_item", "item_name": "Cloak of Protection"})

    def _on_attunement_change(self, e):
        e.page.pubsub.send_all_on_topic(PubSubTopic.UI_ACTION, {
            "action": UIAction.TOGGLE_ATTUNEMENT,
            "index": e.control.data,
            "is_active": e.control.value
        })

    # --- Data Updaters ---
    def update_inventory_ui(self, topic=None, message=None):
        self.item_list_column.controls.clear()
        
        for index, item in enumerate(self.model.inventory):
            item_row = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(item.name, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, expand=True),
                    ft.Text(item.short_description, color=ft.Colors.GREY_400, size=12, expand=True),
                    ft.Checkbox(
                        label="Attuned", 
                        value=item.is_active, 
                        data=index,
                        on_change=self._on_attunement_change
                    )
                ]
            )
            self.item_list_column.controls.append(item_row)
            
        # THE FIX: Check if the component is mounted before updating
        if self.page:
            self.update()
            
    def set_edit_mode(self, topic=None, is_edit: bool = False):
        self.add_test_item_btn.visible = is_edit
        
        # THE FIX: Apply the safety check here too
        if self.page:
            self.update()