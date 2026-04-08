# from dataclasses import dataclass, field
# from .effectmodifiers import EffectModifier
# from typing import List

# @dataclass
# class InventoryItem:
#     """Represents an individual item within a character's inventory"""
#     name: str
#     category: str = "Gear"
#     rarity: str = "Common"
#     requires_attunement: bool = False
#     description: str = ""
#     short_description: str = ""
#     is_equipped: bool = False
#     modifiers: List[EffectModifier] = field(default_factory=list)

#     def __post_init__(self):
#         """Converts raw dictionaries from the DB into Modifier objects."""
#         # When loaded from JSON, modifiers might be dictionaries convert them to an EffectModifier
#         if self.modifiers and isinstance(self.modifiers[0], dict):
#             self.modifiers = [EffectModifier(**mod_dict) for mod_dict in self.modifiers]

from dataclasses import dataclass
from .base_entity import StatAffectingEntity

@dataclass(kw_only=True)
class InventoryItem(StatAffectingEntity):
    """Represents an item within a character's inventory"""
    category: str = "Gear"
    rarity: str = "Common"
    requires_attunement: bool = False
    
    # Notice we don't redefine name, description, or modifiers!
    # They are inherited from StatAffectingEntity.