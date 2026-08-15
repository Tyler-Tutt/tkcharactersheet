import flet as ft
from models import CharacterModel
from views.components import AbilityScoreContainer, CharacterHeaderContainer, AcInitiativeSpeed, InventoryContainer
from events import PubSubTopic

class CharacterSheetView(ft.Container):
    def __init__(self, model: CharacterModel):
        super().__init__(expand=True)
        self.model = model
        self.ability_score_containers = []
        self.content = self.build_ui()

    # --- Flet Lifecycle Methods for Pub/Sub ---
    def did_mount(self):
        self.page.pubsub.subscribe_topic(PubSubTopic.MODEL_UPDATED, self.handle_model_update)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(PubSubTopic.MODEL_UPDATED, self.handle_model_update)

    def handle_model_update(self, topic, message):
        """Updates components living strictly in this root view."""
        self.proficiency_bonus_field.value = self.model.format_modifier(self.model.proficiency_bonus)
        self.proficiency_bonus_field.update()

    def build_ui(self):
        self.header = CharacterHeaderContainer(self.model)
        self.achpspeed = AcInitiativeSpeed(self.model)
        self.proficiency_bonus_field = ft.TextField(
            label="Proficiency Bonus",
            value=self.model.format_modifier(self.model.proficiency_bonus),
            read_only=True,
            text_align=ft.TextAlign.CENTER,
        )
        self.inventory_container = InventoryContainer(self.model)
        self.second_row_container = self._create_row_2()
        
        return ft.Column(
            controls=[
                self.header,
                ft.Divider(height=20),
                self.second_row_container,
            ]
        )

    def _create_row_2(self):
        self.ability_score_containers = self._create_ability_score_containers()
        return ft.Container(
            bgcolor=ft.Colors.LIGHT_BLUE,
            border=ft.Border.all(2),
            padding=5,
            content=ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        col={"sm": 12, "md": 4},
                        controls=[self.proficiency_bonus_field, *self.ability_score_containers]
                    ),
                    ft.Column(
                        col={"sm": 12, "md": 4},
                        controls=[self.achpspeed]),
                    ft.Column(
                        col={"sm": 12, "md": 4},
                        controls=[ft.Text("Features & Traits"), self.inventory_container]
                    )
                ]
            )
        )

    def _create_ability_score_containers(self):
        containers = []
        for ability_name in self.model.ability_list:
            container = AbilityScoreContainer(model=self.model, ability_name=ability_name)
            containers.append(container)
        return containers