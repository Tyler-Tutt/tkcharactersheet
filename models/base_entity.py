from dataclasses import dataclass, field
from typing import List
from .effectmodifiers import EffectModifier

@dataclass(kw_only=True)
class StatAffectingEntity:
    """Base class for anything that can modify a character's stats: Items, Feats, Spells, etc."""
    name: str
    description: str = ""
    short_description: str = ""
    is_active: bool = False # For an item, this means 'equipped'. For a spell, 'concentrating'.
    modifiers: List[EffectModifier] = field(default_factory=list)

    def __post_init__(self):
        """Converts raw dictionaries from the DB into Modifier objects."""
        if self.modifiers and isinstance(self.modifiers[0], dict):
            self.modifiers = [EffectModifier(**mod_dict) for mod_dict in self.modifiers]