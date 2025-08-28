"""
Item system for Charcoal 2.0 - weapons, armor, and relics
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    RELIC = "relic"
    CONSUMABLE = "consumable"


class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class ItemStats:
    """Stats that an item can provide"""
    attack: int = 0
    defense: int = 0
    magic_power: int = 0
    health: int = 0
    special_effect: str = ""


@dataclass
class Item:
    """Represents an item in the game world"""
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    stats: ItemStats
    value: int = 0
    
    def get_display_name(self) -> str:
        """Get display name with rarity indicator"""
        rarity_symbols = {
            ItemRarity.COMMON: "",
            ItemRarity.UNCOMMON: "★",
            ItemRarity.RARE: "★★",
            ItemRarity.EPIC: "★★★",
            ItemRarity.LEGENDARY: "★★★★"
        }
        symbol = rarity_symbols.get(self.rarity, "")
        return f"{self.name} {symbol}".strip()
    
    def get_full_description(self) -> str:
        """Get full item description including stats"""
        desc = f"**{self.get_display_name()}**\n{self.description}"
        
        if self.stats.attack > 0:
            desc += f"\n+{self.stats.attack} Attack"
        if self.stats.defense > 0:
            desc += f"\n+{self.stats.defense} Defense"
        if self.stats.magic_power > 0:
            desc += f"\n+{self.stats.magic_power} Magic Power"
        if self.stats.health > 0:
            desc += f"\n+{self.stats.health} Health"
        if self.stats.special_effect:
            desc += f"\nSpecial: {self.stats.special_effect}"
        
        return desc


class ItemGenerator:
    """Generates items for dungeons and rewards"""
    
    def __init__(self):
        self.weapon_templates = self._create_weapon_templates()
        self.armor_templates = self._create_armor_templates()
        self.relic_templates = self._create_relic_templates()
        self.consumable_templates = self._create_consumable_templates()
    
    def _create_weapon_templates(self) -> List[Dict]:
        """Create weapon templates"""
        return [
            # Common Weapons
            {
                "name": "Iron Sword",
                "description": "A sturdy iron blade forged by skilled smiths.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(attack=3),
                "value": 25
            },
            {
                "name": "Wooden Staff",
                "description": "A simple staff carved from ancient oak.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(magic_power=2),
                "value": 15
            },
            {
                "name": "Hunting Bow",
                "description": "A reliable bow favored by forest hunters.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(attack=2, magic_power=1),
                "value": 20
            },
            
            # Uncommon Weapons
            {
                "name": "Enchanted Blade",
                "description": "A sword infused with magical energy that glows faintly.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(attack=5, magic_power=2),
                "value": 75
            },
            {
                "name": "Crystal Wand",
                "description": "A delicate wand topped with a shimmering crystal.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(magic_power=4, health=10),
                "value": 60
            },
            
            # Rare Weapons
            {
                "name": "Flameforge Hammer",
                "description": "A massive hammer that burns with eternal flame.",
                "rarity": ItemRarity.RARE,
                "stats": ItemStats(attack=8, special_effect="Burns enemies"),
                "value": 150
            },
            {
                "name": "Staff of Storms",
                "description": "Lightning crackles around this powerful staff.",
                "rarity": ItemRarity.RARE,
                "stats": ItemStats(magic_power=7, special_effect="Lightning damage"),
                "value": 180
            },
            
            # Epic Weapons
            {
                "name": "Shadowbane",
                "description": "A legendary sword that cuts through darkness itself.",
                "rarity": ItemRarity.EPIC,
                "stats": ItemStats(attack=12, magic_power=3, special_effect="Banishes shadows"),
                "value": 400
            },
            
            # Legendary Weapons
            {
                "name": "Dragonslayer",
                "description": "The legendary blade that once felled the ancient dragon king.",
                "rarity": ItemRarity.LEGENDARY,
                "stats": ItemStats(attack=15, magic_power=5, special_effect="Dragon's Bane"),
                "value": 1000
            }
        ]
    
    def _create_armor_templates(self) -> List[Dict]:
        """Create armor templates"""
        return [
            # Common Armor
            {
                "name": "Leather Armor",
                "description": "Basic protection made from tanned hides.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(defense=2),
                "value": 20
            },
            {
                "name": "Cloth Robes",
                "description": "Simple robes that provide minimal protection.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(defense=1, magic_power=2),
                "value": 15
            },
            
            # Uncommon Armor
            {
                "name": "Chainmail Shirt",
                "description": "Interlocked metal rings provide good protection.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(defense=4, health=20),
                "value": 80
            },
            {
                "name": "Mage Robes",
                "description": "Robes woven with protective enchantments.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(defense=2, magic_power=4),
                "value": 70
            },
            
            # Rare Armor
            {
                "name": "Plate Mail",
                "description": "Heavy armor that provides excellent protection.",
                "rarity": ItemRarity.RARE,
                "stats": ItemStats(defense=8, health=30),
                "value": 200
            },
            {
                "name": "Robes of the Archmage",
                "description": "Magnificent robes that amplify magical power.",
                "rarity": ItemRarity.RARE,
                "stats": ItemStats(defense=3, magic_power=8),
                "value": 250
            },
            
            # Epic Armor
            {
                "name": "Dragon Scale Mail",
                "description": "Armor crafted from the scales of an ancient dragon.",
                "rarity": ItemRarity.EPIC,
                "stats": ItemStats(defense=12, magic_power=2, special_effect="Fire resistance"),
                "value": 500
            },
            
            # Legendary Armor
            {
                "name": "Aegis of Eternity",
                "description": "The ultimate protective armor, said to make its wearer invincible.",
                "rarity": ItemRarity.LEGENDARY,
                "stats": ItemStats(defense=15, health=50, special_effect="Damage immunity"),
                "value": 1500
            }
        ]
    
    def _create_relic_templates(self) -> List[Dict]:
        """Create relic templates"""
        return [
            # Common Relics
            {
                "name": "Ancient Coin",
                "description": "A tarnished coin from a long-lost civilization.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(special_effect="Good luck"),
                "value": 10
            },
            {
                "name": "Worn Pendant",
                "description": "A simple pendant that seems to have seen many adventures.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(health=5),
                "value": 15
            },
            
            # Uncommon Relics
            {
                "name": "Crystal of Clarity",
                "description": "A small crystal that enhances mental focus.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(magic_power=3, special_effect="Enhanced perception"),
                "value": 60
            },
            {
                "name": "Ring of Vigor",
                "description": "A ring that fills its wearer with energy.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(health=15, special_effect="Increased stamina"),
                "value": 55
            },
            
            # Rare Relics
            {
                "name": "Amulet of the Depths",
                "description": "An amulet that holds the mysteries of the deep ocean.",
                "rarity": ItemRarity.RARE,
                "stats": ItemStats(magic_power=5, special_effect="Water breathing"),
                "value": 180
            },
            {
                "name": "Crown of Ancient Kings",
                "description": "A crown that once belonged to legendary rulers.",
                "rarity": ItemRarity.RARE,
                "stats": ItemStats(magic_power=4, health=25, special_effect="Leadership aura"),
                "value": 300
            },
            
            # Epic Relics
            {
                "name": "Heart of the Forest",
                "description": "A mystical artifact containing the essence of nature itself.",
                "rarity": ItemRarity.EPIC,
                "stats": ItemStats(magic_power=8, health=30, special_effect="Nature's blessing"),
                "value": 600
            },
            
            # Legendary Relics
            {
                "name": "Orb of Infinite Wisdom",
                "description": "A legendary artifact said to contain all knowledge of the ages.",
                "rarity": ItemRarity.LEGENDARY,
                "stats": ItemStats(magic_power=10, health=40, special_effect="Ultimate knowledge"),
                "value": 2000
            }
        ]
    
    def _create_consumable_templates(self) -> List[Dict]:
        """Create consumable templates"""
        return [
            {
                "name": "Health Potion",
                "description": "A red potion that instantly restores health.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(special_effect="Restores 50 HP"),
                "value": 25
            },
            {
                "name": "Mana Potion",
                "description": "A blue potion that restores magical energy.",
                "rarity": ItemRarity.COMMON,
                "stats": ItemStats(special_effect="Restores 30 MP"),
                "value": 20
            },
            {
                "name": "Scroll of Fireball",
                "description": "A scroll containing a powerful fire spell.",
                "rarity": ItemRarity.UNCOMMON,
                "stats": ItemStats(special_effect="Casts Fireball"),
                "value": 40
            }
        ]
    
    def generate_item(self, item_type: ItemType = None, rarity: ItemRarity = None) -> Item:
        """Generate a random item of specified type and rarity"""
        if item_type is None:
            item_type = random.choice(list(ItemType))
        
        # Select appropriate template list
        if item_type == ItemType.WEAPON:
            templates = self.weapon_templates
        elif item_type == ItemType.ARMOR:
            templates = self.armor_templates
        elif item_type == ItemType.RELIC:
            templates = self.relic_templates
        else:  # CONSUMABLE
            templates = self.consumable_templates
        
        # Filter by rarity if specified
        if rarity is not None:
            filtered_templates = [t for t in templates if t["rarity"] == rarity]
            if filtered_templates:
                templates = filtered_templates
            else:
                # If no templates match the requested rarity for this item type,
                # search all templates for the requested rarity
                all_templates = (self.weapon_templates + self.armor_templates + 
                               self.relic_templates + self.consumable_templates)
                rarity_templates = [t for t in all_templates if t["rarity"] == rarity]
                if rarity_templates:
                    template = random.choice(rarity_templates)
                    # Override item_type with the actual type from the template
                    if template in self.weapon_templates:
                        item_type = ItemType.WEAPON
                    elif template in self.armor_templates:
                        item_type = ItemType.ARMOR
                    elif template in self.relic_templates:
                        item_type = ItemType.RELIC
                    else:
                        item_type = ItemType.CONSUMABLE
                    
                    return Item(
                        name=template["name"],
                        description=template["description"],
                        item_type=item_type,
                        rarity=template["rarity"],
                        stats=template["stats"],
                        value=template["value"]
                    )
        
        if not templates:
            # Final fallback
            templates = self.weapon_templates
        
        template = random.choice(templates)
        
        return Item(
            name=template["name"],
            description=template["description"],
            item_type=item_type,
            rarity=template["rarity"],
            stats=template["stats"],
            value=template["value"]
        )
    
    def generate_treasure_for_area(self, area_type: str, difficulty: int = 1) -> List[Item]:
        """Generate appropriate treasures for an area type"""
        items = []
        
        # Determine number of items based on area type
        if area_type == "boss_room":
            num_items = random.randint(2, 4)
            rarity_weights = {
                ItemRarity.RARE: 40,
                ItemRarity.EPIC: 30,
                ItemRarity.LEGENDARY: 20,
                ItemRarity.UNCOMMON: 10
            }
        elif area_type == "treasure_room":
            num_items = random.randint(2, 3)
            rarity_weights = {
                ItemRarity.UNCOMMON: 40,
                ItemRarity.RARE: 35,
                ItemRarity.EPIC: 20,
                ItemRarity.COMMON: 5
            }
        else:  # Regular areas
            num_items = random.randint(1, 2)  # Changed from 0,2 to 1,2 to ensure at least one item
            rarity_weights = {
                ItemRarity.COMMON: 50,
                ItemRarity.UNCOMMON: 35,
                ItemRarity.RARE: 15
            }
        
        for _ in range(num_items):
            # Choose rarity based on weights
            rarities = list(rarity_weights.keys())
            weights = list(rarity_weights.values())
            rarity = random.choices(rarities, weights=weights)[0]
            
            # Choose item type
            item_type = random.choice(list(ItemType))
            
            items.append(self.generate_item(item_type, rarity))
        
        return items


# Global item generator instance
item_generator = ItemGenerator()