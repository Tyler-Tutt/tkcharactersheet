import flet as ft
from models import CharacterModel
from events import PubSubTopic

class AcInitiativeSpeed(ft.Container):
    def __init__(self, model: CharacterModel):
        super().__init__(
            padding=10,
            bgcolor=ft.Colors.RED_200,
            border=ft.Border.all(2, ft.Colors.OUTLINE),
            border_radius=8
        )
        self.model = model

        self.armor_class = ft.TextField(label="Armor Class", value=str(model.armor_class), read_only=True, col={"sm": 12, "md": 4})
        initiative_string = f"+{model.initiative}" if model.initiative >= 0 else str(model.initiative)
        self.initiative = ft.TextField(label="Initiative", value=initiative_string, read_only=True, col={"sm": 12, "md": 4})
        self.speed = ft.TextField(label="Speed", value=str(model.base_speed), data="speed", on_change=self._on_speed_change, col={"sm": 12, "md": 4})

        self.content = ft.ResponsiveRow(controls=[self.armor_class, self.initiative, self.speed])

        # Initialize the component in View Mode
        self.set_edit_mode(is_edit=False)

    # --- Pub/Sub Subscriptions ---
    def did_mount(self):
        self.page.pubsub.subscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_stats_data)
        self.page.pubsub.subscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_stats_data)
        self.page.pubsub.unsubscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    # --- Action Publishers ---
    def _on_speed_change(self, e):
        e.page.pubsub.send_all_on_topic(PubSubTopic.UI_ACTION, {
            "action": "update_header", 
            "attr": "speed", 
            "value": e.control.value
        })

    # --- Data Updaters ---
    def update_stats_data(self, topic=None, message=None):
        self.armor_class.value = str(self.model.armor_class)
        self.initiative.value = f"+{self.model.initiative}" if self.model.initiative >= 0 else str(self.model.initiative)
        # Update speed only if not in edit mode so we don't overwrite user typing
        if self.speed.read_only:
            self.speed.value = str(self.model.final_speed)
        if self.page:
            self.update()

    def set_edit_mode(self, topic=None, is_edit: bool = False):
        self.speed.read_only = not is_edit
        self.speed.value = str(self.model.base_speed) if is_edit else str(self.model.final_speed)
        try:
            self.update()
        except RuntimeError:
            pass