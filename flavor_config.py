"""
Flavor text and configuration management for Charcoal 2.0
Separates game mechanics from flavor text for easier customization
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FlavorTextSet:
    """Represents a set of flavor text for a particular theme or world"""
    name: str
    description: str
    character_descriptions: Dict[str, Dict[str, str]]  # class -> personality -> description templates
    item_descriptions: Dict[str, Dict[str, str]]       # item_type -> rarity -> description templates
    location_descriptions: Dict[str, List[str]]        # location_type -> description templates
    event_descriptions: Dict[str, List[str]]           # event_type -> description templates
    dialogue_templates: Dict[str, Dict[str, List[str]]] # class -> personality -> dialogue templates


class FlavorTextManager:
    """Manages flavor text sets and allows easy switching between themes"""
    
    def __init__(self, config_directory: str = "config"):
        self.config_directory = config_directory
        self.current_theme = "default"
        self.flavor_sets = {}
        self.load_all_flavor_sets()
    
    def load_all_flavor_sets(self):
        """Load all available flavor text sets"""
        # Ensure config directory exists
        os.makedirs(self.config_directory, exist_ok=True)
        
        # Load default flavor set
        self.flavor_sets["default"] = self._create_default_flavor_set()
        
        # Load custom flavor sets from files
        config_files = [f for f in os.listdir(self.config_directory) if f.endswith('_flavor.json')]
        for config_file in config_files:
            theme_name = config_file.replace('_flavor.json', '')
            try:
                with open(os.path.join(self.config_directory, config_file), 'r') as f:
                    data = json.load(f)
                    self.flavor_sets[theme_name] = FlavorTextSet(**data)
            except Exception as e:
                print(f"Error loading flavor set {theme_name}: {e}")
    
    def _create_default_flavor_set(self) -> FlavorTextSet:
        """Create the default fantasy flavor text set"""
        return FlavorTextSet(
            name="Classic Fantasy",
            description="Traditional fantasy adventure setting with classic tropes",
            
            character_descriptions={
                "Warrior": {
                    "brave": [
                        "A stalwart {background} whose courage never wavers in the face of danger",
                        "A fearless champion who stands between allies and harm",
                        "A bold warrior whose battle cry rallies others to victory"
                    ],
                    "cautious": [
                        "A careful {background} who thinks before acting in combat",
                        "A tactical warrior who values strategy over reckless bravery",
                        "A prudent fighter who has survived by being prepared"
                    ],
                    "hot-headed": [
                        "A fierce {background} whose temper burns as hot as their blade",
                        "An impulsive warrior who charges into battle without hesitation",
                        "A passionate fighter whose emotions fuel their combat prowess"
                    ]
                },
                "Mage": {
                    "wise": [
                        "A learned {background} whose knowledge of arcane arts runs deep",
                        "A scholarly spellcaster who approaches magic with reverence",
                        "An ancient soul whose wisdom guides their magical practice"
                    ],
                    "curious": [
                        "An inquisitive {background} always seeking new magical knowledge",
                        "A researcher whose thirst for magical discovery knows no bounds",
                        "An experimenter who pushes the boundaries of known magic"
                    ],
                    "mischievous": [
                        "A playful {background} who delights in magical pranks and tricks",
                        "A cunning spellcaster who uses magic for clever schemes",
                        "A wily mage whose magic often serves their sense of humor"
                    ]
                },
                "Rogue": {
                    "mischievous": [
                        "A sly {background} whose quick fingers match their quicker wit",
                        "A cunning infiltrator who finds opportunity in every shadow",
                        "A clever thief who views the world as their personal playground"
                    ],
                    "cautious": [
                        "A careful {background} who trusts no one and questions everything",
                        "A paranoid scout who has survived by being suspicious",
                        "A wary spy who knows that everyone has secrets worth hiding"
                    ],
                    "independent": [
                        "A lone wolf {background} who prefers to work without partners",
                        "A self-reliant wanderer who trusts only their own skills",
                        "A solitary figure who values freedom above all else"
                    ]
                }
            },
            
            item_descriptions={
                "weapon": {
                    "common": [
                        "A simple but reliable {item_type} that has seen honest use",
                        "A basic {item_type} favored by common soldiers and adventurers",
                        "An ordinary {item_type} that gets the job done without fanfare"
                    ],
                    "rare": [
                        "A masterwork {item_type} crafted by legendary smiths",
                        "An exceptional {item_type} that few warriors are worthy to wield",
                        "A renowned {item_type} with a history of great deeds"
                    ],
                    "legendary": [
                        "A mythical {item_type} spoken of in ancient prophecies",
                        "An artifact {item_type} from the age of heroes",
                        "A divine {item_type} blessed by the gods themselves"
                    ]
                },
                "armor": {
                    "common": [
                        "Sturdy {item_type} that provides basic protection",
                        "Well-made {item_type} suitable for any adventurer",
                        "Practical {item_type} designed for comfort and utility"
                    ],
                    "rare": [
                        "Expertly crafted {item_type} that offers superior protection",
                        "Enchanted {item_type} that shimmers with protective magic",
                        "Masterwork {item_type} worn by elite warriors"
                    ],
                    "legendary": [
                        "Legendary {item_type} that has protected heroes throughout the ages",
                        "Divine {item_type} forged in the celestial forges",
                        "Mythical {item_type} that grants near-invulnerability"
                    ]
                }
            },
            
            location_descriptions={
                "entrance": [
                    "The entrance yawns before you like a hungry maw",
                    "Ancient stonework frames a passage into darkness",
                    "Weathered steps lead down into the unknown depths"
                ],
                "chamber": [
                    "A vast chamber opens before you, filled with echoing silence",
                    "Pillars stretch upward into shadow-shrouded heights",
                    "The room feels heavy with the weight of forgotten ages"
                ],
                "treasure_room": [
                    "Glittering treasures catch the light from every surface",
                    "Piles of coins and gems create a dazzling display of wealth",
                    "Ancient riches lie scattered in magnificent disarray"
                ]
            },
            
            event_descriptions={
                "discovery": [
                    "Your keen eyes spot something hidden in the shadows",
                    "A glint of metal catches your attention",
                    "Something valuable lies partially concealed nearby"
                ],
                "combat": [
                    "Battle erupts with the clash of steel and cry of war",
                    "Violence fills the air as weapons are drawn",
                    "The dance of death begins as combatants face off"
                ],
                "dialogue": [
                    "Words are exchanged in the flickering torchlight",
                    "Conversation flows as easily as wine at a tavern",
                    "Voices echo in the ancient halls as stories are shared"
                ]
            },
            
            dialogue_templates={
                "Warrior": {
                    "brave": [
                        "Fear not, {companion}! My sword stands ready!",
                        "Let them come! I'll meet them with steel and courage!",
                        "Stand behind me, friends. I'll break through their lines!"
                    ],
                    "cautious": [
                        "Wait... let me scout ahead first.",
                        "Something doesn't feel right about this place.",
                        "We should be careful. Danger lurks in every shadow."
                    ]
                },
                "Mage": {
                    "wise": [
                        "The ancient texts speak of such places...",
                        "Magic flows strangely here. We must be cautious.",
                        "Knowledge is our greatest weapon in these depths."
                    ],
                    "curious": [
                        "Fascinating! I've never seen magic like this before!",
                        "What secrets might these walls hold?",
                        "I must study this phenomenon more closely!"
                    ]
                }
            }
        )
    
    def get_character_description(self, character_class: str, background: str, personality: str) -> str:
        """Get a character description based on current theme"""
        flavor_set = self.flavor_sets.get(self.current_theme, self.flavor_sets["default"])
        
        # Get templates for this class and personality
        class_templates = flavor_set.character_descriptions.get(character_class, {})
        personality_templates = class_templates.get(personality, [])
        
        if not personality_templates:
            # Fallback to generic description
            return f"A {background.lower()} {character_class.lower()} with a {personality.lower()} personality"
        
        # Pick a random template and format it
        import random
        template = random.choice(personality_templates)
        return template.format(background=background.lower(), personality=personality.lower())
    
    def get_item_description(self, item_type: str, item_name: str, rarity: str) -> str:
        """Get an item description based on current theme"""
        flavor_set = self.flavor_sets.get(self.current_theme, self.flavor_sets["default"])
        
        # Get templates for this item type and rarity
        type_templates = flavor_set.item_descriptions.get(item_type.lower(), {})
        rarity_templates = type_templates.get(rarity.lower(), [])
        
        if not rarity_templates:
            # Fallback to basic description
            return f"A {rarity.lower()} {item_type.lower()}"
        
        # Pick a random template and format it
        import random
        template = random.choice(rarity_templates)
        return template.format(item_type=item_type.lower(), item_name=item_name)
    
    def get_location_description(self, location_type: str) -> str:
        """Get a location description based on current theme"""
        flavor_set = self.flavor_sets.get(self.current_theme, self.flavor_sets["default"])
        
        templates = flavor_set.location_descriptions.get(location_type.lower(), [])
        if not templates:
            return f"A {location_type.lower()} area"
        
        import random
        return random.choice(templates)
    
    def get_event_description(self, event_type: str) -> str:
        """Get an event description based on current theme"""
        flavor_set = self.flavor_sets.get(self.current_theme, self.flavor_sets["default"])
        
        templates = flavor_set.event_descriptions.get(event_type.lower(), [])
        if not templates:
            return f"A {event_type.lower()} occurs"
        
        import random
        return random.choice(templates)
    
    def get_dialogue_template(self, character_class: str, personality: str) -> str:
        """Get a dialogue template for a character"""
        flavor_set = self.flavor_sets.get(self.current_theme, self.flavor_sets["default"])
        
        class_templates = flavor_set.dialogue_templates.get(character_class, {})
        personality_templates = class_templates.get(personality, [])
        
        if not personality_templates:
            return "..."  # Fallback silence
        
        import random
        return random.choice(personality_templates)
    
    def set_theme(self, theme_name: str) -> bool:
        """Switch to a different flavor theme"""
        if theme_name in self.flavor_sets:
            self.current_theme = theme_name
            return True
        return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of available flavor themes"""
        return list(self.flavor_sets.keys())
    
    def create_custom_theme(self, theme_name: str, flavor_set: FlavorTextSet):
        """Create a new custom theme"""
        self.flavor_sets[theme_name] = flavor_set
        self._save_flavor_set(theme_name, flavor_set)
    
    def _save_flavor_set(self, theme_name: str, flavor_set: FlavorTextSet):
        """Save a flavor set to file"""
        try:
            filename = os.path.join(self.config_directory, f"{theme_name}_flavor.json")
            with open(filename, 'w') as f:
                # Convert dataclass to dict for JSON serialization
                data = {
                    "name": flavor_set.name,
                    "description": flavor_set.description,
                    "character_descriptions": flavor_set.character_descriptions,
                    "item_descriptions": flavor_set.item_descriptions,
                    "location_descriptions": flavor_set.location_descriptions,
                    "event_descriptions": flavor_set.event_descriptions,
                    "dialogue_templates": flavor_set.dialogue_templates
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving flavor set {theme_name}: {e}")
    
    def export_theme_template(self, theme_name: str = None) -> Dict:
        """Export a theme as a template for customization"""
        if theme_name is None:
            theme_name = self.current_theme
        
        flavor_set = self.flavor_sets.get(theme_name, self.flavor_sets["default"])
        
        return {
            "name": flavor_set.name,
            "description": flavor_set.description,
            "character_descriptions": flavor_set.character_descriptions,
            "item_descriptions": flavor_set.item_descriptions,
            "location_descriptions": flavor_set.location_descriptions,
            "event_descriptions": flavor_set.event_descriptions,
            "dialogue_templates": flavor_set.dialogue_templates
        }


class ConfigurableGameSettings:
    """Manages game settings that can be easily modified"""
    
    def __init__(self, config_file: str = "config/game_settings.json"):
        self.config_file = config_file
        self.settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self) -> Dict:
        """Load default game settings"""
        return {
            "permadeath": {
                "enabled_by_default": False,
                "allow_resurrection": True,
                "resurrection_cost_multiplier": 2.0,
                "death_penalty_experience_loss": 0.1
            },
            "difficulty": {
                "base_enemy_strength": 1.0,
                "treasure_rarity_modifier": 1.0,
                "experience_gain_multiplier": 1.0,
                "risk_reward_balance": 1.0
            },
            "engagement": {
                "focus_on_synergies": True,
                "emphasize_gear_combinations": True,
                "minimize_level_importance": True,
                "encourage_experimentation": True
            },
            "world_theme": {
                "current_flavor": "default",
                "allow_theme_mixing": False,
                "custom_themes_enabled": True
            },
            "character_creation": {
                "max_traits": 3,
                "min_traits": 1,
                "allow_custom_traits": False,
                "trait_reroll_cost": 50
            },
            "gear_system": {
                "synergy_bonus_multiplier": 1.0,
                "set_bonus_stacking": True,
                "equipment_durability": False,
                "gear_upgrade_system": True
            }
        }
    
    def load_settings(self):
        """Load settings from file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'r') as f:
                loaded_settings = json.load(f)
                # Merge with defaults to handle missing keys
                self._merge_settings(self.settings, loaded_settings)
        except FileNotFoundError:
            # Save default settings if file doesn't exist
            self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _merge_settings(self, default: Dict, loaded: Dict):
        """Recursively merge loaded settings with defaults"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_settings(default[key], value)
                else:
                    default[key] = value
    
    def get_setting(self, path: str, default=None):
        """Get a setting using dot notation (e.g., 'permadeath.enabled_by_default')"""
        keys = path.split('.')
        current = self.settings
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set_setting(self, path: str, value):
        """Set a setting using dot notation"""
        keys = path.split('.')
        current = self.settings
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self._load_default_settings()
        self.save_settings()
    
    def export_settings(self) -> Dict:
        """Export current settings for backup or sharing"""
        return self.settings.copy()
    
    def import_settings(self, settings: Dict):
        """Import settings from a dictionary"""
        self.settings = settings.copy()
        self.save_settings()