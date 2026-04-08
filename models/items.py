from dataclasses import dataclass
from .base_entity import StatAffectingEntity

@dataclass(kw_only=True)
class InventoryItem(StatAffectingEntity):
    """Represents an item within a character's inventory"""
    category: str = "Gear"
    rarity: str = "Common"
    requires_attunement: bool = False
    
    # name, description, short_description, is_active, and modifiers are inherited from StatAffectingEntity.