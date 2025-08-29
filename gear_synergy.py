"""
Gear synergy system for Charcoal 2.0
Creates interesting combinations and set bonuses for equipment
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set
from items import Item, ItemType, ItemRarity, ItemStats


class SynergyType(Enum):
    SET_BONUS = "set_bonus"           # Multiple items from same set
    ELEMENT_SYNERGY = "element_synergy"  # Items with matching elements
    CLASS_SYNERGY = "class_synergy"   # Items designed for same class
    COMBAT_STYLE = "combat_style"     # Items that support same fighting style
    MAGICAL_RESONANCE = "magical_resonance"  # Magical items that amplify each other


@dataclass
class SynergyBonus:
    """Represents a bonus from item synergies"""
    name: str
    description: str
    stat_bonuses: Dict[str, int]
    special_effects: List[str]
    required_items: int  # How many items needed for this bonus
    
    def get_display_text(self) -> str:
        """Get formatted display text for the synergy"""
        text = f"**{self.name}** ({self.required_items} items)\n{self.description}"
        
        if self.stat_bonuses:
            text += "\nBonuses:"
            for stat, bonus in self.stat_bonuses.items():
                text += f"\n  +{bonus} {stat.replace('_', ' ').title()}"
        
        if self.special_effects:
            text += "\nSpecial Effects:"
            for effect in self.special_effects:
                text += f"\n  • {effect}"
        
        return text


@dataclass 
class ItemSet:
    """Represents a set of items with synergy bonuses"""
    name: str
    theme: str
    items: List[str]  # Item names that belong to this set
    bonuses: Dict[int, SynergyBonus]  # Number of items -> bonus
    
    def get_active_bonuses(self, equipped_items: List[str]) -> List[SynergyBonus]:
        """Get active bonuses based on equipped items"""
        equipped_set_items = [item for item in equipped_items if item in self.items]
        active_bonuses = []
        
        for required_count, bonus in sorted(self.bonuses.items()):
            if len(equipped_set_items) >= required_count:
                active_bonuses.append(bonus)
        
        return active_bonuses


class GearSynergyManager:
    """Manages gear synergies and combination effects"""
    
    def __init__(self):
        self.item_sets = self._create_item_sets()
        self.elemental_groups = self._create_elemental_groups()
        self.class_synergies = self._create_class_synergies()
        self.combat_styles = self._create_combat_styles()
    
    def _create_item_sets(self) -> Dict[str, ItemSet]:
        """Create predefined item sets with bonuses"""
        sets = {}
        
        # Flameguard Set
        sets["flameguard"] = ItemSet(
            name="Flameguard Arsenal",
            theme="fire",
            items=["Flameforge Hammer", "Dragon Scale Mail", "Ring of Fire Resistance"],
            bonuses={
                2: SynergyBonus(
                    name="Flame Touched",
                    description="Your weapons burn with inner fire",
                    stat_bonuses={"attack": 5, "fire_damage": 10},
                    special_effects=["Weapon attacks have chance to burn enemies"],
                    required_items=2
                ),
                3: SynergyBonus(
                    name="Avatar of Flame",
                    description="You become one with the eternal fire",
                    stat_bonuses={"attack": 12, "fire_damage": 25, "fire_resistance": 50},
                    special_effects=[
                        "Weapon attacks always burn enemies",
                        "Fire immunity",
                        "Aura of flame damages nearby enemies"
                    ],
                    required_items=3
                )
            }
        )
        
        # Shadowweaver Set
        sets["shadowweaver"] = ItemSet(
            name="Shadowweaver's Collection",
            theme="shadow",
            items=["Shadowbane", "Cloak of Shadows", "Amulet of the Void"],
            bonuses={
                2: SynergyBonus(
                    name="Shadow Step",
                    description="Move through shadows with supernatural grace",
                    stat_bonuses={"dexterity": 8, "stealth": 20},
                    special_effects=["Can teleport short distances through shadows"],
                    required_items=2
                ),
                3: SynergyBonus(
                    name="Master of Shadows", 
                    description="Command the very darkness itself",
                    stat_bonuses={"dexterity": 15, "stealth": 40, "shadow_damage": 30},
                    special_effects=[
                        "Become invisible in darkness",
                        "Shadow clone ability",
                        "Darkness aura blinds enemies"
                    ],
                    required_items=3
                )
            }
        )
        
        # Arcane Scholar Set
        sets["arcane_scholar"] = ItemSet(
            name="Arcane Scholar's Regalia",
            theme="knowledge",
            items=["Staff of Storms", "Robes of the Archmage", "Orb of Infinite Wisdom"],
            bonuses={
                2: SynergyBonus(
                    name="Mystical Focus",
                    description="Your magical studies pay off in power",
                    stat_bonuses={"magic_power": 10, "mana_efficiency": 15},
                    special_effects=["Spells cost less mana", "Enhanced spell critical chance"],
                    required_items=2
                ),
                3: SynergyBonus(
                    name="Archmage Ascendant",
                    description="Transcend mortal magical limitations",
                    stat_bonuses={"magic_power": 20, "mana_efficiency": 30, "intelligence": 10},
                    special_effects=[
                        "All spells enhanced",
                        "Mana regeneration tripled",
                        "Can cast multiple spells per turn"
                    ],
                    required_items=3
                )
            }
        )
        
        # Nature's Guardian Set
        sets["natures_guardian"] = ItemSet(
            name="Nature's Guardian Collection",
            theme="nature",
            items=["Staff of the Grove", "Bark Armor", "Heart of the Forest"],
            bonuses={
                2: SynergyBonus(
                    name="Nature's Blessing",
                    description="The natural world aids your cause",
                    stat_bonuses={"health": 25, "nature_resistance": 25},
                    special_effects=["Slowly regenerate health over time"],
                    required_items=2
                ),
                3: SynergyBonus(
                    name="Druid Sovereign",
                    description="Command all aspects of the natural world",
                    stat_bonuses={"health": 50, "nature_resistance": 50, "magic_power": 8},
                    special_effects=[
                        "Rapid health regeneration",
                        "Can summon nature allies",
                        "Plants and animals aid in combat"
                    ],
                    required_items=3
                )
            }
        )
        
        return sets
    
    def _create_elemental_groups(self) -> Dict[str, Dict]:
        """Create elemental synergy groups"""
        return {
            "fire": {
                "items": ["Flameforge Hammer", "Ring of Fire", "Cloak of Flames"],
                "bonus": SynergyBonus(
                    name="Elemental Fire Mastery",
                    description="Master the destructive power of flame",
                    stat_bonuses={"fire_damage": 15, "fire_resistance": 25},
                    special_effects=["Fire spells enhanced", "Immune to burning"],
                    required_items=2
                )
            },
            "ice": {
                "items": ["Frostbite Blade", "Cloak of Winter", "Crystal of Eternal Ice"],
                "bonus": SynergyBonus(
                    name="Elemental Ice Mastery",
                    description="Harness the preserving power of ice",
                    stat_bonuses={"ice_damage": 15, "ice_resistance": 25},
                    special_effects=["Ice spells enhanced", "Chance to freeze enemies"],
                    required_items=2
                )
            },
            "lightning": {
                "items": ["Staff of Storms", "Boots of Speed", "Amulet of Thunder"],
                "bonus": SynergyBonus(
                    name="Elemental Lightning Mastery", 
                    description="Channel the swift power of storms",
                    stat_bonuses={"lightning_damage": 15, "dexterity": 5},
                    special_effects=["Lightning spells enhanced", "Increased movement speed"],
                    required_items=2
                )
            }
        }
    
    def _create_class_synergies(self) -> Dict[str, Dict]:
        """Create class-specific synergies"""
        return {
            "warrior": {
                "preferred_items": ["Iron Sword", "Enchanted Blade", "Flameforge Hammer", 
                                  "Chainmail Shirt", "Plate Mail", "Dragon Scale Mail"],
                "bonus": SynergyBonus(
                    name="Master-at-Arms",
                    description="Expertise with martial weapons and armor",
                    stat_bonuses={"attack": 8, "defense": 8},
                    special_effects=["Enhanced weapon proficiency", "Armor mastery"],
                    required_items=3
                )
            },
            "mage": {
                "preferred_items": ["Wooden Staff", "Crystal Wand", "Staff of Storms",
                                  "Cloth Robes", "Mage Robes", "Robes of the Archmage"],
                "bonus": SynergyBonus(
                    name="Arcane Specialist",
                    description="Mastery of magical arts and implements",
                    stat_bonuses={"magic_power": 12, "mana_efficiency": 20},
                    special_effects=["Spell mastery", "Enhanced magical focus"],
                    required_items=3
                )
            },
            "rogue": {
                "preferred_items": ["Shadowbane", "Assassin's Blade", "Leather Armor",
                                  "Cloak of Shadows", "Boots of Stealth"],
                "bonus": SynergyBonus(
                    name="Shadow Specialist",
                    description="Master of stealth and precision strikes",
                    stat_bonuses={"dexterity": 10, "stealth": 30},
                    special_effects=["Critical strike mastery", "Stealth expertise"],
                    required_items=3
                )
            }
        }
    
    def _create_combat_styles(self) -> Dict[str, Dict]:
        """Create combat style synergies"""
        return {
            "berserker": {
                "items": ["two_handed_weapons", "light_armor", "rage_items"],
                "bonus": SynergyBonus(
                    name="Berserker's Fury",
                    description="Abandon defense for overwhelming offense",
                    stat_bonuses={"attack": 15, "critical_chance": 10},
                    special_effects=["Damage increases as health decreases"],
                    required_items=2
                )
            },
            "tank": {
                "items": ["shields", "heavy_armor", "defensive_items"],
                "bonus": SynergyBonus(
                    name="Immovable Object",
                    description="Become an unbreakable wall of defense",
                    stat_bonuses={"defense": 20, "health": 40},
                    special_effects=["Taunt enemies", "Damage reduction"],
                    required_items=2
                )
            },
            "caster": {
                "items": ["staves", "robes", "magical_accessories"],
                "bonus": SynergyBonus(
                    name="Magical Supremacy",
                    description="Maximize your arcane potential",
                    stat_bonuses={"magic_power": 18, "mana_efficiency": 25},
                    special_effects=["Enhanced spellcasting", "Mana overflow"],
                    required_items=2
                )
            }
        }
    
    def analyze_equipment_synergies(self, equipped_items: List[Item]) -> Dict[str, List[SynergyBonus]]:
        """Analyze equipped items for synergies and return active bonuses"""
        synergies = {
            "set_bonuses": [],
            "elemental_synergies": [],
            "class_synergies": [],
            "combat_style_synergies": []
        }
        
        item_names = [item.name for item in equipped_items]
        
        # Check set bonuses
        for set_name, item_set in self.item_sets.items():
            active_bonuses = item_set.get_active_bonuses(item_names)
            synergies["set_bonuses"].extend(active_bonuses)
        
        # Check elemental synergies
        for element, group in self.elemental_groups.items():
            equipped_elemental = [name for name in item_names if name in group["items"]]
            if len(equipped_elemental) >= group["bonus"].required_items:
                synergies["elemental_synergies"].append(group["bonus"])
        
        # Check class synergies (would need character class as parameter)
        # This is a placeholder - in real implementation, pass character class
        
        return synergies
    
    def get_synergy_recommendations(self, current_items: List[Item], 
                                   character_class: str = None) -> List[Dict]:
        """Get recommendations for items that would create synergies"""
        recommendations = []
        current_names = [item.name for item in current_items]
        
        # Check which sets the player is close to completing
        for set_name, item_set in self.item_sets.items():
            equipped_from_set = [name for name in current_names if name in item_set.items]
            missing_items = [item for item in item_set.items if item not in current_names]
            
            if equipped_from_set and missing_items:
                next_bonus_threshold = None
                for threshold in sorted(item_set.bonuses.keys()):
                    if len(equipped_from_set) < threshold:
                        next_bonus_threshold = threshold
                        break
                
                if next_bonus_threshold:
                    items_needed = next_bonus_threshold - len(equipped_from_set)
                    recommendations.append({
                        "type": "set_completion",
                        "set_name": item_set.name,
                        "current_items": len(equipped_from_set),
                        "needed_items": items_needed,
                        "recommended_items": missing_items[:items_needed],
                        "bonus": item_set.bonuses[next_bonus_threshold]
                    })
        
        return recommendations
    
    def calculate_total_synergy_bonuses(self, synergies: Dict[str, List[SynergyBonus]]) -> Dict[str, int]:
        """Calculate total stat bonuses from all active synergies"""
        total_bonuses = {}
        
        for synergy_type, bonus_list in synergies.items():
            for bonus in bonus_list:
                for stat, value in bonus.stat_bonuses.items():
                    total_bonuses[stat] = total_bonuses.get(stat, 0) + value
        
        return total_bonuses
    
    def get_all_special_effects(self, synergies: Dict[str, List[SynergyBonus]]) -> List[str]:
        """Get all special effects from active synergies"""
        effects = []
        
        for synergy_type, bonus_list in synergies.items():
            for bonus in bonus_list:
                effects.extend(bonus.special_effects)
        
        return effects
    
    def format_synergy_display(self, synergies: Dict[str, List[SynergyBonus]]) -> str:
        """Format synergies for display to player"""
        if not any(synergies.values()):
            return "No active synergies"
        
        display = "🔮 **Active Synergies:**\n\n"
        
        for synergy_type, bonus_list in synergies.items():
            if bonus_list:
                type_name = synergy_type.replace("_", " ").title()
                display += f"**{type_name}:**\n"
                for bonus in bonus_list:
                    display += f"  {bonus.get_display_text()}\n\n"
        
        # Summary of total bonuses
        total_bonuses = self.calculate_total_synergy_bonuses(synergies)
        if total_bonuses:
            display += "**Total Synergy Bonuses:**\n"
            for stat, value in total_bonuses.items():
                display += f"  +{value} {stat.replace('_', ' ').title()}\n"
        
        return display