"""
Enhanced character traits and abilities system for Charcoal 2.0
Provides more depth to character customization beyond basic class/background
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TraitCategory(Enum):
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    MYSTICAL = "mystical"
    SURVIVAL = "survival"


@dataclass
class CharacterTrait:
    """Represents a character trait that provides unique abilities or bonuses"""
    name: str
    description: str
    category: TraitCategory
    mechanical_effect: Dict  # Stats bonuses, special abilities, etc.
    flavor_text: str
    
    def apply_effects(self, character) -> Dict:
        """Apply trait effects to character stats"""
        return self.mechanical_effect.copy()


class TraitManager:
    """Manages character traits and their effects"""
    
    def __init__(self):
        self.traits = self._create_trait_templates()
    
    def _create_trait_templates(self) -> Dict[str, CharacterTrait]:
        """Create available character traits"""
        traits = {}
        
        # Combat Traits
        traits["battle_hardened"] = CharacterTrait(
            name="Battle Hardened",
            description="Veteran of countless battles, harder to kill",
            category=TraitCategory.COMBAT,
            mechanical_effect={"hp_bonus": 25, "damage_resistance": 10},
            flavor_text="Scars tell stories of survival against impossible odds"
        )
        
        traits["weapon_master"] = CharacterTrait(
            name="Weapon Master",
            description="Exceptional skill with all weapons",
            category=TraitCategory.COMBAT,
            mechanical_effect={"attack_bonus": 15, "critical_chance": 5},
            flavor_text="Each weapon becomes an extension of their will"
        )
        
        traits["berserker_fury"] = CharacterTrait(
            name="Berserker's Fury",
            description="Damage increases as health decreases",
            category=TraitCategory.COMBAT,
            mechanical_effect={"fury_scaling": True, "max_fury_bonus": 30},
            flavor_text="Pain fuels an unstoppable rage"
        )
        
        # Social Traits
        traits["silver_tongue"] = CharacterTrait(
            name="Silver Tongue",
            description="Masterful at persuasion and deception",
            category=TraitCategory.SOCIAL,
            mechanical_effect={"dialogue_bonus": 20, "merchant_discount": 15},
            flavor_text="Words flow like honey, hiding thorns beneath"
        )
        
        traits["natural_leader"] = CharacterTrait(
            name="Natural Leader",
            description="Inspires allies and boosts party morale",
            category=TraitCategory.SOCIAL,
            mechanical_effect={"party_hp_bonus": 10, "inspiration_charges": 3},
            flavor_text="Others naturally gravitate toward their presence"
        )
        
        traits["intimidating_presence"] = CharacterTrait(
            name="Intimidating Presence",
            description="Enemies hesitate before striking",
            category=TraitCategory.SOCIAL,
            mechanical_effect={"fear_chance": 15, "intimidation_bonus": 25},
            flavor_text="A single glance can freeze blood in veins"
        )
        
        # Exploration Traits
        traits["pathfinder"] = CharacterTrait(
            name="Pathfinder",
            description="Expert at navigation and finding hidden routes",
            category=TraitCategory.EXPLORATION,
            mechanical_effect={"secret_detection": 30, "movement_bonus": 10},
            flavor_text="The wilderness holds no secrets from them"
        )
        
        traits["keen_observer"] = CharacterTrait(
            name="Keen Observer",
            description="Notices details others miss",
            category=TraitCategory.EXPLORATION,
            mechanical_effect={"treasure_find_bonus": 25, "trap_detection": 20},
            flavor_text="Nothing escapes their watchful gaze"
        )
        
        traits["lucky"] = CharacterTrait(
            name="Lucky",
            description="Fortune favors this character",
            category=TraitCategory.EXPLORATION,
            mechanical_effect={"luck_bonus": 15, "critical_luck": 10},
            flavor_text="Fate seems to smile upon their endeavors"
        )
        
        # Mystical Traits
        traits["arcane_scholar"] = CharacterTrait(
            name="Arcane Scholar",
            description="Deep understanding of magical forces",
            category=TraitCategory.MYSTICAL,
            mechanical_effect={"magic_power_bonus": 20, "spell_efficiency": 15},
            flavor_text="Ancient secrets whisper in their mind"
        )
        
        traits["mana_touched"] = CharacterTrait(
            name="Mana Touched",
            description="Born with natural magical affinity",
            category=TraitCategory.MYSTICAL,
            mechanical_effect={"mana_regeneration": 25, "magic_resistance": 15},
            flavor_text="Magic flows through their veins like blood"
        )
        
        traits["spirit_walker"] = CharacterTrait(
            name="Spirit Walker",
            description="Can commune with spirits and the dead",
            category=TraitCategory.MYSTICAL,
            mechanical_effect={"spirit_communication": True, "undead_resistance": 20},
            flavor_text="They walk between the world of the living and dead"
        )
        
        # Survival Traits
        traits["wilderness_survivor"] = CharacterTrait(
            name="Wilderness Survivor",
            description="Thrives in harsh natural environments",
            category=TraitCategory.SURVIVAL,
            mechanical_effect={"environmental_resistance": 20, "foraging_bonus": 30},
            flavor_text="Nature is both home and ally"
        )
        
        traits["poison_resistant"] = CharacterTrait(
            name="Poison Resistant",
            description="Natural immunity to toxins and disease",
            category=TraitCategory.SURVIVAL,
            mechanical_effect={"poison_immunity": 75, "disease_resistance": 50},
            flavor_text="Toxins that fell others barely affect them"
        )
        
        traits["death_defiant"] = CharacterTrait(
            name="Death Defiant",
            description="Refuses to stay down when defeated",
            category=TraitCategory.SURVIVAL,
            mechanical_effect={"death_save_bonus": 40, "resurrection_chance": 25},
            flavor_text="Death must work harder to claim this soul"
        )
        
        return traits
    
    def get_random_trait(self, category: TraitCategory = None) -> CharacterTrait:
        """Get a random trait, optionally filtered by category"""
        available_traits = list(self.traits.values())
        if category:
            available_traits = [t for t in available_traits if t.category == category]
        return random.choice(available_traits)
    
    def get_trait_by_name(self, name: str) -> Optional[CharacterTrait]:
        """Get a specific trait by name"""
        return self.traits.get(name.lower().replace(" ", "_"))
    
    def get_traits_by_category(self, category: TraitCategory) -> List[CharacterTrait]:
        """Get all traits in a specific category"""
        return [trait for trait in self.traits.values() if trait.category == category]
    
    def get_recommended_traits_for_class(self, character_class: str) -> List[CharacterTrait]:
        """Get traits that synergize well with a character class"""
        class_recommendations = {
            "Warrior": [TraitCategory.COMBAT, TraitCategory.SURVIVAL],
            "Mage": [TraitCategory.MYSTICAL, TraitCategory.SOCIAL],
            "Rogue": [TraitCategory.EXPLORATION, TraitCategory.SOCIAL],
            "Cleric": [TraitCategory.MYSTICAL, TraitCategory.SOCIAL],
            "Archer": [TraitCategory.EXPLORATION, TraitCategory.COMBAT],
            "Paladin": [TraitCategory.COMBAT, TraitCategory.MYSTICAL],
            "Bard": [TraitCategory.SOCIAL, TraitCategory.MYSTICAL],
            "Druid": [TraitCategory.MYSTICAL, TraitCategory.SURVIVAL]
        }
        
        recommended_categories = class_recommendations.get(character_class, [TraitCategory.COMBAT])
        recommended_traits = []
        
        for category in recommended_categories:
            recommended_traits.extend(self.get_traits_by_category(category))
        
        return recommended_traits


@dataclass
class StartingGearChoice:
    """Represents a choice of starting equipment for a character"""
    name: str
    description: str
    items: List[str]  # Item names to generate
    bonus_stats: Dict = None
    
    def __post_init__(self):
        if self.bonus_stats is None:
            self.bonus_stats = {}


class StartingGearManager:
    """Manages starting gear options for character creation"""
    
    def __init__(self):
        self.gear_choices = self._create_gear_choices()
    
    def _create_gear_choices(self) -> Dict[str, List[StartingGearChoice]]:
        """Create starting gear choices organized by class"""
        choices = {}
        
        # Warrior choices
        choices["Warrior"] = [
            StartingGearChoice(
                name="Guardian's Arsenal",
                description="Heavy armor and sword for the frontline protector",
                items=["Iron Sword", "Chainmail Shirt", "Health Potion"],
                bonus_stats={"defense": 5}
            ),
            StartingGearChoice(
                name="Berserker's Fury",
                description="Two-handed weapon and light armor for aggressive combat",
                items=["Flameforge Hammer", "Leather Armor", "Mana Potion"],
                bonus_stats={"attack": 8}
            ),
            StartingGearChoice(
                name="Veteran's Kit",
                description="Balanced equipment for the experienced fighter",
                items=["Enchanted Blade", "Mage Robes", "Health Potion", "Scroll of Fireball"],
                bonus_stats={"attack": 3, "defense": 2}
            )
        ]
        
        # Mage choices
        choices["Mage"] = [
            StartingGearChoice(
                name="Arcane Researcher",
                description="Focused on magical power and knowledge",
                items=["Staff of Storms", "Robes of the Archmage", "Mana Potion", "Mana Potion"],
                bonus_stats={"magic_power": 10}
            ),
            StartingGearChoice(
                name="Battle Mage",
                description="Combination of magic and martial prowess",
                items=["Crystal Wand", "Chainmail Shirt", "Health Potion", "Scroll of Fireball"],
                bonus_stats={"magic_power": 5, "defense": 3}
            ),
            StartingGearChoice(
                name="Hedge Wizard",
                description="Practical magic with survival gear",
                items=["Wooden Staff", "Cloth Robes", "Health Potion", "Mana Potion"],
                bonus_stats={"magic_power": 6, "health": 15}
            )
        ]
        
        # Rogue choices  
        choices["Rogue"] = [
            StartingGearChoice(
                name="Shadow Assassin",
                description="Stealth and precision strikes",
                items=["Shadowbane", "Leather Armor", "Health Potion"],
                bonus_stats={"attack": 6, "stealth": 20}
            ),
            StartingGearChoice(
                name="Treasure Hunter",
                description="Focus on exploration and finding secrets",
                items=["Iron Sword", "Leather Armor", "Health Potion", "Crystal of Clarity"],
                bonus_stats={"treasure_finding": 25}
            ),
            StartingGearChoice(
                name="Street Fighter",
                description="Tough and adaptable urban warrior",
                items=["Enchanted Blade", "Chainmail Shirt", "Health Potion"],
                bonus_stats={"defense": 4, "social": 10}
            )
        ]
        
        # Add choices for other classes with similar patterns
        for class_name in ["Cleric", "Archer", "Paladin", "Bard", "Druid"]:
            if class_name not in choices:
                choices[class_name] = [
                    StartingGearChoice(
                        name=f"Traditional {class_name}",
                        description=f"Classic {class_name.lower()} equipment and approach",
                        items=["Iron Sword", "Leather Armor", "Health Potion"],
                        bonus_stats={"balanced": 5}
                    ),
                    StartingGearChoice(
                        name=f"Specialized {class_name}",
                        description=f"Focused on {class_name.lower()}-specific abilities",
                        items=["Crystal Wand", "Mage Robes", "Mana Potion"],
                        bonus_stats={"specialty": 8}
                    )
                ]
        
        return choices
    
    def get_choices_for_class(self, character_class: str) -> List[StartingGearChoice]:
        """Get starting gear choices for a specific class"""
        return self.gear_choices.get(character_class, [])
    
    def get_choice_by_name(self, character_class: str, choice_name: str) -> Optional[StartingGearChoice]:
        """Get a specific starting gear choice"""
        choices = self.get_choices_for_class(character_class)
        for choice in choices:
            if choice.name.lower() == choice_name.lower():
                return choice
        return None