import flet as ft
from models import CharacterModel
from models.enums import StatType
from events import PubSubTopic

class AbilityScoreContainer(ft.Container):
    def __init__(self, model: CharacterModel, ability_name: StatType):
        super().__init__(
            padding=10,
            bgcolor=ft.Colors.LIGHT_GREEN,
            border=ft.Border.all(2, ft.Colors.OUTLINE),
            border_radius=8
        )
        self.model = model
        self.ability_name = ability_name
        self.skill_modifier_fields = {}
        self.skill_checkboxes = [] 
        
        # Format the Enum cleanly for the UI display (e.g., "strength" -> "Strength")
        display_name = ability_name.value.replace("_", " ").title()
        
        initial_score = self.model.ability_scores_list[ability_name].base_score
        self.ability_name_text = ft.Text(display_name.upper(), size=16, weight=ft.FontWeight.BOLD)
        self.modifier_text = ft.Text(self.model.format_modifier((initial_score - 10) // 2), size=20)
        self.score_field = ft.TextField(
            value=str(initial_score),
            text_align=ft.TextAlign.CENTER,
            width=100,
            on_change=self._on_score_change
        )
        
        self.skills_controls = []
        skills_data = self.model.ability_scores_list[ability_name].skills
        
        for skill_name, skill_info in skills_data.items():
            mod_val = self.model.get_skill_modifier(self.ability_name, skill_name)
            mod_field = ft.TextField(
                value=self.model.format_modifier(mod_val), 
                read_only=True, width=60, text_align=ft.TextAlign.CENTER, col={"sm": 3, "md": 3}
            )
            self.skill_modifier_fields[skill_name] = mod_field
            
            prof_checkbox = ft.Checkbox(
                value=skill_info.base_proficiency, 
                data={"ability": self.ability_name, "skill": skill_name},
                on_change=self._on_proficiency_change,
                col={"sm": 2, "md": 2}
            )
            self.skill_checkboxes.append(prof_checkbox) 
            
            # Format the skill Enum cleanly for the UI display
            skill_display = skill_name.value.replace("_", " ").title()
            
            self.skills_controls.append(
                ft.ResponsiveRow(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[prof_checkbox, mod_field, ft.Text(skill_display, selectable=True, col={"sm": 7, "md": 7})]
                )
            )
            
        self.content = ft.ResponsiveRow(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Column(
                    col={"sm": 12, "md": 4},
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.ability_name_text, self.modifier_text, self.score_field]
                ),
                ft.Column(col={"sm": 12, "md": 8}, controls=self.skills_controls),
            ]
        )

        self.set_edit_mode(is_edit=False)

    # --- Pub/Sub Subscriptions ---
    def did_mount(self):
        self.page.pubsub.subscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_card_data)
        self.page.pubsub.subscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(PubSubTopic.MODEL_UPDATED, self.update_card_data)
        self.page.pubsub.unsubscribe_topic(PubSubTopic.EDIT_MODE_CHANGED, self.set_edit_mode)

    # --- Action Publishers ---
    def _on_score_change(self, e: ft.ControlEvent):
        raw_value = e.control.value
        try:
            new_score = int(raw_value) if raw_value != "" else 0
        except ValueError:
            new_score = 10
            self.score_field.value = str(new_score)
            self.score_field.update()

        e.page.pubsub.send_all_on_topic(PubSubTopic.UI_ACTION, {
            "action": "update_ability",
            "ability": self.ability_name,
            "score": new_score
        })

    def _on_proficiency_change(self, e: ft.ControlEvent):
        e.page.pubsub.send_all_on_topic("ui_action", {
            "action": "toggle_proficiency",
            "ability": e.control.data["ability"],
            "skill": e.control.data["skill"],
            "is_proficient": e.control.value
        })

    # --- Data Updaters ---
    def update_card_data(self, topic=None, message=None):
        is_edit = not self.score_field.read_only
        score = self.model.ability_scores_list[self.ability_name].base_score if is_edit else self.model.get_final_ability_score(self.ability_name)
            
        self.score_field.value = str(score)
        self.modifier_text.value = self.model.format_modifier((score - 10) // 2)
        
        for skill_name, mod_field in self.skill_modifier_fields.items():
            mod_field.value = self.model.format_modifier(self.model.get_skill_modifier(self.ability_name, skill_name))
            
        for checkbox in self.skill_checkboxes:
            skill_name = checkbox.data["skill"]
            checkbox.value = self.model.ability_scores_list[self.ability_name].skills[skill_name].base_proficiency if is_edit else self.model.is_skill_proficient(self.ability_name, skill_name)
        
        if self.page:
            self.update()

    def set_edit_mode(self, topic=None, is_edit: bool = False):
        self.score_field.read_only = not is_edit
        self.score_field.value = str(self.model.ability_scores_list[self.ability_name].base_score) if is_edit else str(self.model.get_final_ability_score(self.ability_name))

        for checkbox in self.skill_checkboxes:
            checkbox.disabled = not is_edit
            skill_name = checkbox.data["skill"]
            checkbox.value = self.model.ability_scores_list[self.ability_name].skills[skill_name].base_proficiency if is_edit else self.model.is_skill_proficient(self.ability_name, skill_name)

        try:
            self.update()
        except RuntimeError:
            pass