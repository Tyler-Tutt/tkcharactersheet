"""
Default Stats & Default Stat Arithmetic
"""

from typing import Final, Dict, List
from models.enums import StatType

# --- 5e Core Rules ---
BASE_AC: Final[int] = 10
BASE_ABILITY_SCORE: Final[int] = 10
ABILITY_MODIFIER_DIVISOR: Final[int] = 2

DEFAULT_SPEED: Final[int] = 30
DEFAULT_MAX_HP: Final[int] = 10

PROFICIENCY_BASE: Final[int] = 2
PROFICIENCY_LEVEL_DIVISOR: Final[int] = 4

# --- Character Abilities & Skills ---
ABILITIES: Final[List[StatType]] = [
    StatType.STRENGTH, StatType.DEXTERITY, StatType.CONSTITUTION,
    StatType.INTELLIGENCE, StatType.WISDOM, StatType.CHARISMA
]

SKILLS: Final[Dict[StatType, List[StatType]]] = {
    StatType.STRENGTH: [StatType.SAVING_THROWS, StatType.ATHLETICS],
    StatType.DEXTERITY: [StatType.SAVING_THROWS, StatType.ACROBATICS, StatType.SLEIGHT_OF_HAND, StatType.STEALTH],
    StatType.CONSTITUTION: [StatType.SAVING_THROWS],
    StatType.INTELLIGENCE: [StatType.SAVING_THROWS, StatType.ARCANA, StatType.HISTORY, StatType.INVESTIGATION, StatType.NATURE, StatType.RELIGION],
    StatType.WISDOM: [StatType.SAVING_THROWS, StatType.ANIMAL_HANDLING, StatType.INSIGHT, StatType.MEDICINE, StatType.PERCEPTION, StatType.SURVIVAL],
    StatType.CHARISMA: [StatType.SAVING_THROWS, StatType.DECEPTION, StatType.INTIMIDATION, StatType.PERFORMANCE, StatType.PERSUASION]
}