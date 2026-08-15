import flet as ft
from models import CharacterModel
from events import PubSubTopic, UIAction

class CharacterHeaderContainer(ft.Container):
    def __init__(self, model: CharacterModel):
        super().__init__(
            padding=10,
            bgcolor=ft.Colors.CYAN_700,
            border=ft.Border.all(2, ft.Colors.OUTLINE),
            border_radius=8
        )
        self.model = model

        self.charactername_field = ft.TextField(label="Character Name", value=model.charactername, data="charactername", on_change=self._on_header_change)
        self.class_field = ft.TextField(label="Class", value=model.characterclass, data="characterclass", on_change=self._on_header_change)
        self.level_field = ft.TextField(label="Level", value=str(model.level), data="level", on_change=self._on_header_change, col={"sm": 12, "md": 4})
        self.background_field = ft.TextField(label="Background", value=model.background, data="background", on_change=self._on_header_change, col={"sm": 12, "md": 4})
        self.player_name_field = ft.TextField(label="Player Name", value=model.player_name, data="player_name", on_change=self._on_header_change, col={"sm": 12, "md": 4})
        self.race_field = ft.TextField(label="Race", value=model.race, data="race", on_change=self._on_header_change, col={"sm": 12, "md": 4})
        self.alignment_field = ft.TextField(label="Alignment", value=model.alignment, data="alignment", on_change=self._on_header_change, col={"sm": 12, "md": 4})
        self.experience_points_field = ft.TextField(label="Experience Points", value=str(model.experience_points), data="experience_points", on_change=self._on_header_change, col={"sm": 12, "md": 4})

        self.content = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(col={"sm": 12, "md": 4}, controls=[self.charactername_field, self.class_field]),
                ft.Column(col={"sm": 12, "md": 8}, controls=[
                        ft.ResponsiveRow(controls=[self.level_field, self.background_field, self.player_name_field]),
                        ft.ResponsiveRow(controls=[self.race_field, self.alignment_field, self.experience_points_field])
                ])
            ]
        )

        # Initialize the component in View Mode
        self.set_edit_mode(is_edit=False)

    # --- Pub/Sub Subscriptions ---
    def did_mount(self):
        self.page.pubsub.subscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_header_data)
        self.page.pubsub.subscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_header_data)
        self.page.pubsub.unsubscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    # --- Action Publishers ---
    def _on_header_change(self, e):
        '''
        Action to take on changing a header field's value
        Tell's the Flet PubSub 'Frequency' of 'UI_ACTION' to trigger
        '''
        e.page.pubsub.send_all_on_topic(PubSubTopic.UI_ACTION, {
            "action": UIAction.UPDATE_HEADER ,
            "attr": e.control.data,
            "value": e.control.value
        })

    # --- Data Updaters ---
    def update_header_data(self, topic=None, message=None):
        self.charactername_field.value = self.model.charactername
        self.class_field.value = self.model.characterclass
        
        if self.level_field.read_only:
             self.level_field.value = str(self.model.level)
             self.experience_points_field.value = str(self.model.experience_points)
             
        self.background_field.value = self.model.background
        self.player_name_field.value = self.model.player_name
        self.race_field.value = self.model.race
        self.alignment_field.value = self.model.alignment

        # SAFETY CHECK
        if self.page:
            self.update()

    def set_edit_mode(self, topic=None, is_edit: bool = False):
        read_only_state = not is_edit 
        self.charactername_field.read_only = read_only_state
        self.class_field.read_only = read_only_state
        self.level_field.read_only = read_only_state
        self.background_field.read_only = read_only_state
        self.player_name_field.read_only = read_only_state
        self.race_field.read_only = read_only_state
        self.alignment_field.read_only = read_only_state
        self.experience_points_field.read_only = read_only_state
        try:
            self.update()
        except RuntimeError:
            pass