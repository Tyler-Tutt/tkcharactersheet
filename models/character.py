from dataclasses import dataclass, field, asdict
from typing import Dict, List
import rules_5e as rules
from .items import InventoryItem
from .stats import Ability, Skill
from .enums import StatType, ArithmeticType
from .effectmodifiers import EffectModifier

@dataclass
class CharacterModel:
    """ "The Model": Represents current data and score-logic of a Character"""
    # --- Core Attributes ---
    charactername: str = "Character Name"
    characterclass: str = "Character Class"
    level: int = 1
    background: str = "Background"
    player_name: str = "Player Name"
    race: str = "Race"
    alignment: str = "Alignment"
    experience_points: int = 0
    base_speed: int = rules.DEFAULT_SPEED
    base_max_hp: int = rules.DEFAULT_MAX_HP
    current_hp: int = rules.DEFAULT_MAX_HP
    temp_hp: int = 0

    # --- Modifier List ---
    active_modifiers: List[EffectModifier] = field(default_factory=list)
    
    # --- Inventory ---
    inventory: List[InventoryItem] = field(default_factory=list)

    # --- Ability & Skill Data ---
    ability_list: list = field(default_factory=lambda: rules.ABILITIES.copy())
    ability_scores_list: Dict[str, Ability] = field(default_factory=dict)

    def __post_init__(self):
        """Initializes the nested Ability & Skill dictionaries if not provided."""
        if not self.ability_scores_list:
            for ability, skills in rules.SKILLS.items():
                ability_skills = {skill_name: Skill() for skill_name in skills}
                self.ability_scores_list[ability] = Ability(
                    base_score=rules.BASE_ABILITY_SCORE, 
                    skills=ability_skills
                )

    # --- THE MODIFIER ENGINE ---
    def update_active_modifiers(self):
        """Rebuilds the active modifiers list based on equipped items, active spells, etc."""
        self.active_modifiers.clear()
        
        # Pulls modifiers from Inventory Items
        self.active_modifiers.extend([
            mod for item in self.inventory 
            if item.is_active for mod in item.modifiers
        ])
        
        # Future additions go here!
        # self.active_modifiers.extend(self.get_spell_modifiers())
        # self.active_modifiers.extend(self.get_feat_modifiers())

    def calculate_stat(self, target_stat: StatType, base_value: int | float) -> int:
        """
        Universal Stat Calculation Engine. 
        Order of Operations: Base -> Override -> Bonus -> Multiplier
        """
        # 1. Filter for the target_stat
        relevant_mods = [mod for mod in self.active_modifiers if mod.target == target_stat]
        final_value = float(base_value)
        # 2. Process Overrides (e.g., Setting a stat to a specific number)
        overrides = [mod.value for mod in relevant_mods if mod.arithmetic_type == ArithmeticType.OVERRIDE]
        if overrides:
            final_value = max(overrides) # Standard D&D rule: take the highest override
        # 3. Process Bonuses (Additive/Subtractive)
        bonuses = [mod.value for mod in relevant_mods if mod.arithmetic_type == ArithmeticType.BONUS]
        final_value += sum(bonuses)
        # 4. Process Multipliers (e.g., double speed)
        multipliers = [mod.value for mod in relevant_mods if mod.arithmetic_type == ArithmeticType.MULTIPLIER]
        for mult in multipliers:
            final_value *= mult

        # Return as an integer (D&D generally rounds down)
        return int(final_value)

    # --- DERIVED PROPERTIES (Using the Engine) ---
    @property
    def proficiency_bonus(self) -> int:
        return rules.PROFICIENCY_BASE + ((self.level - 1) // rules.PROFICIENCY_LEVEL_DIVISOR)
        
    @property
    def final_speed(self) -> int:
        return self.calculate_stat(StatType.SPEED, self.base_speed)

    def get_final_ability_score(self, ability_name: StatType) -> int:
        base = self.ability_scores_list.get(ability_name).base_score if ability_name in self.ability_scores_list else rules.BASE_ABILITY_SCORE
        return self.calculate_stat(ability_name, base)

    @property
    def initiative(self) -> int:
        """Derived from FINAL Dexterity + any Initiative specific modifiers."""
        final_dex = self.get_final_ability_score("Dexterity")
        dex_mod = (final_dex - rules.BASE_ABILITY_SCORE) // rules.ABILITY_MODIFIER_DIVISOR
        return self.calculate_stat(StatType.INITIATIVE, dex_mod)

    @property
    def armor_class(self) -> int:
        """Derived from 10 + FINAL Dexterity mod + any AC specific modifiers."""
        final_dex = self.get_final_ability_score("Dexterity")
        dex_mod = (final_dex - rules.BASE_ABILITY_SCORE) // rules.ABILITY_MODIFIER_DIVISOR
        base_ac = rules.BASE_AC + dex_mod
        
        return self.calculate_stat(StatType.AC, base_ac)

    # --- Helper methods ---
    def is_skill_proficient(self, ability_name: StatType, skill_name: StatType) -> bool:
        ability = self.ability_scores_list.get(ability_name)
        if ability and skill_name in ability.skills:
            return ability.skills[skill_name].base_proficiency
        return False

    def get_skill_modifier(self, ability_name: StatType, skill_name: StatType) -> int:
        final_score = self.get_final_ability_score(ability_name)
        base_modifier = (final_score - rules.BASE_ABILITY_SCORE) // rules.ABILITY_MODIFIER_DIVISOR
        proficiency_bonus = self.proficiency_bonus if self.is_skill_proficient(ability_name, skill_name) else 0
        
        base_skill_value = base_modifier + proficiency_bonus
        
        # Look how beautifully simple this is now:
        return self.calculate_stat(skill_name, base_skill_value)

    def format_modifier(self, mod: int) -> str:
        return f"+{mod}" if mod >= 0 else str(mod)

    # --- SERIALIZATION / DESERIALIZATION ---
    def convert_to_dictionary(self) -> dict:
        """Built-in standard for converting the dataclass to a JSON-ready dict."""
        return asdict(self)
        
    def load_from_dictionary(self, character_data: dict):
        """Updates the instance data in-place from a loaded dictionary."""
        if not character_data:
            return False

        # Load Standard Types
        for attr in ['charactername', 'characterclass', 'level', 'background', 
                     'player_name', 'race', 'alignment', 'experience_points', 
                     'base_speed', 'base_max_hp', 'current_hp', 'temp_hp']:
            if attr in character_data:
                setattr(self, attr, character_data[attr])
        
        # Load Complex Types (Abilities & Skills)
        if 'abilities' in character_data:
            for ability_str, ability_data in character_data['abilities'].items():
                # Directly cast the JSON string back into our StatType Enum
                ability_enum = StatType(ability_str)
                
                if ability_enum in self.ability_scores_list:
                    self.ability_scores_list[ability_enum].base_score = ability_data.get('base_score', rules.BASE_ABILITY_SCORE)
                    
                    for skill_str, skill_data in ability_data.get('skills', {}).items():
                        # Directly cast the skill JSON string back into our StatType Enum
                        skill_enum = StatType(skill_str)
                        
                        if skill_enum in self.ability_scores_list[ability_enum].skills:
                            self.ability_scores_list[ability_enum].skills[skill_enum].base_proficiency = skill_data.get('base_proficient', False)
        
        # Load Complex Types (Inventory)
        self.inventory = []
        if 'inventory' in character_data:
            for item_data in character_data['inventory']:
                self.inventory.append(InventoryItem(**item_data))
                
        self.update_active_modifiers()
        return True