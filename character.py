import json
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from config import CHARACTER_CLASSES, CHARACTER_BACKGROUNDS
from character_traits import CharacterTrait, TraitManager, StartingGearChoice, StartingGearManager, TraitCategory


@dataclass
class CharacterStats:
    """Enhanced character statistics"""
    hp: int = 100
    max_hp: int = 100
    level: int = 1
    experience: int = 0
    
    # Core stats
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    constitution: int = 10
    charisma: int = 10
    
    # Derived stats
    attack_bonus: int = 0
    defense_bonus: int = 0
    magic_power_bonus: int = 0
    health_bonus: int = 0
    
    # Special abilities
    critical_chance: int = 5
    damage_resistance: int = 0
    magic_resistance: int = 0
    luck_bonus: int = 0
    
    def get_effective_hp(self) -> int:
        """Get HP including bonuses"""
        return min(self.hp + self.health_bonus, self.max_hp + self.health_bonus)
    
    def get_effective_attack(self) -> int:
        """Get attack including bonuses"""
        return self.strength + self.attack_bonus
    
    def get_effective_defense(self) -> int:
        """Get defense including bonuses"""
        return self.constitution + self.defense_bonus
    
    def get_effective_magic_power(self) -> int:
        """Get magic power including bonuses"""
        return self.intelligence + self.magic_power_bonus


@dataclass
class Character:
    """Represents an AI character in the game"""
    name: str
    character_class: str
    background: str
    personality: str
    stats: CharacterStats = field(default_factory=CharacterStats)
    traits: List[str] = field(default_factory=list)  # Trait names
    starting_gear_choice: str = ""
    permadeath_enabled: bool = False
    death_count: int = 0
    description: str = ""
    
    # Legacy support for backward compatibility
    @property
    def hp(self) -> int:
        return self.stats.hp
    
    @hp.setter
    def hp(self, value: int):
        self.stats.hp = value
        
    @property
    def level(self) -> int:
        return self.stats.level
    
    @level.setter
    def level(self, value: int):
        self.stats.level = value
        
    @property
    def experience(self) -> int:
        return self.stats.experience
    
    @experience.setter
    def experience(self, value: int):
        self.stats.experience = value
    
    def __post_init__(self):
        if not self.description:
            trait_text = ""
            if self.traits:
                trait_text = f" Known for being {', '.join(self.traits[:2])}."
            self.description = (f"A {self.background.lower()} {self.character_class.lower()} "
                             f"with a {self.personality.lower()} personality.{trait_text}")
    
    def to_dict(self) -> Dict:
        """Convert character to dictionary for serialization"""
        data = asdict(self)
        # Handle stats separately for better structure
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        """Create character from dictionary"""
        # Handle legacy data that doesn't have stats structure
        if 'stats' not in data:
            stats_data = {
                'hp': data.get('hp', 100),
                'level': data.get('level', 1),
                'experience': data.get('experience', 0)
            }
            data['stats'] = stats_data
            # Remove old fields
            data.pop('hp', None)
            data.pop('level', None)
            data.pop('experience', None)
        
        # Handle missing new fields
        data.setdefault('traits', [])
        data.setdefault('starting_gear_choice', "")
        data.setdefault('permadeath_enabled', False)
        data.setdefault('death_count', 0)
        
        # Create stats object
        if isinstance(data['stats'], dict):
            data['stats'] = CharacterStats(**data['stats'])
        
        return cls(**data)
    
    def get_prompt_context(self) -> str:
        """Get character context for AI prompts"""
        trait_context = ""
        if self.traits:
            trait_context = f" You are particularly known for: {', '.join(self.traits[:3])}."
        
        return (f"You are {self.name}, a {self.background.lower()} {self.character_class.lower()}. "
                f"You have a {self.personality.lower()} personality.{trait_context} {self.description}")
    
    def apply_trait_effects(self, trait_manager: 'TraitManager') -> Dict:
        """Apply all trait effects to character stats"""
        effects = {}
        for trait_name in self.traits:
            trait = trait_manager.get_trait_by_name(trait_name)
            if trait:
                trait_effects = trait.apply_effects(self)
                for key, value in trait_effects.items():
                    effects[key] = effects.get(key, 0) + value
        return effects
    
    def get_risk_tolerance(self) -> float:
        """Get character's risk tolerance for permadeath scenarios"""
        base_tolerance = 0.5
        
        # Adjust based on personality
        personality_modifiers = {
            "brave": 0.2,
            "hot-headed": 0.3,
            "cautious": -0.3,
            "wise": -0.1,
            "mischievous": 0.15,
            "serious": -0.05
        }
        
        modifier = personality_modifiers.get(self.personality.lower(), 0)
        return max(0.1, min(0.9, base_tolerance + modifier))
    
    def calculate_death_risk(self, situation_danger: int) -> float:
        """Calculate death risk for a given situation (0-100)"""
        base_risk = situation_danger / 100.0
        
        # Apply constitution and traits
        constitution_modifier = (self.stats.constitution - 10) * 0.02
        trait_modifier = len([t for t in self.traits if "death" in t.lower()]) * 0.1
        
        final_risk = max(0.01, base_risk - constitution_modifier - trait_modifier)
        return min(0.95, final_risk)


class CharacterManager:
    """Manages character creation, storage, and retrieval"""
    
    def __init__(self):
        self.characters: List[Character] = []
        self.trait_manager = TraitManager()
        self.gear_manager = StartingGearManager()
        self.load_characters()
    
    def create_character(self, name: str, character_class: str = None, 
                        background: str = None, personality: str = None,
                        traits: List[str] = None, starting_gear_choice: str = None,
                        permadeath_enabled: bool = False) -> Character:
        """Create a new character with enhanced customization options"""
        if character_class is None:
            character_class = random.choice(CHARACTER_CLASSES)
        if background is None:
            background = random.choice(CHARACTER_BACKGROUNDS)
        if personality is None:
            personality = random.choice([
                "brave", "cautious", "curious", "hot-headed", "wise", "mischievous",
                "loyal", "independent", "cheerful", "serious", "witty", "stoic"
            ])
        
        # Generate random traits if none provided
        if traits is None:
            traits = []
            # Get 1-3 random traits, favoring class-appropriate ones
            num_traits = random.randint(1, 3)
            recommended_traits = self.trait_manager.get_recommended_traits_for_class(character_class)
            
            for _ in range(num_traits):
                if random.random() < 0.7 and recommended_traits:  # 70% chance for recommended trait
                    trait = random.choice(recommended_traits)
                    recommended_traits.remove(trait)  # Don't duplicate
                else:
                    trait = self.trait_manager.get_random_trait()
                
                if trait.name not in traits:
                    traits.append(trait.name)
        
        # Generate starting gear choice if none provided
        if starting_gear_choice is None:
            available_choices = self.gear_manager.get_choices_for_class(character_class)
            if available_choices:
                starting_gear_choice = random.choice(available_choices).name
        
        # Create character with enhanced stats
        stats = CharacterStats()
        
        # Adjust base stats based on class
        class_stat_bonuses = {
            "Warrior": {"strength": 3, "constitution": 2},
            "Mage": {"intelligence": 3, "charisma": 1},
            "Rogue": {"dexterity": 3, "intelligence": 1},
            "Cleric": {"charisma": 2, "constitution": 2},
            "Archer": {"dexterity": 3, "strength": 1},
            "Paladin": {"strength": 2, "charisma": 2},
            "Bard": {"charisma": 3, "dexterity": 1},
            "Druid": {"intelligence": 2, "constitution": 2}
        }
        
        bonuses = class_stat_bonuses.get(character_class, {})
        for stat, bonus in bonuses.items():
            setattr(stats, stat, getattr(stats, stat) + bonus)
        
        character = Character(
            name=name,
            character_class=character_class,
            background=background,
            personality=personality,
            stats=stats,
            traits=traits,
            starting_gear_choice=starting_gear_choice,
            permadeath_enabled=permadeath_enabled
        )
        
        # Apply trait effects to stats
        trait_effects = character.apply_trait_effects(self.trait_manager)
        for effect, value in trait_effects.items():
            if hasattr(character.stats, effect):
                current_value = getattr(character.stats, effect)
                setattr(character.stats, effect, current_value + value)
        
        self.characters.append(character)
        self.save_characters()
        return character
    
    def create_custom_character(self, name: str, character_class: str, background: str,
                              personality: str, selected_traits: List[str],
                              starting_gear_choice: str, permadeath_enabled: bool = False) -> Character:
        """Create a character with fully custom options"""
        return self.create_character(
            name=name,
            character_class=character_class,
            background=background,
            personality=personality,
            traits=selected_traits,
            starting_gear_choice=starting_gear_choice,
            permadeath_enabled=permadeath_enabled
        )
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get character by name"""
        for char in self.characters:
            if char.name.lower() == name.lower():
                return char
        return None
    
    def list_characters(self) -> List[Character]:
        """Get all characters"""
        return self.characters.copy()
    
    def get_character_customization_options(self, character_class: str = None) -> Dict:
        """Get available customization options for character creation"""
        options = {
            "classes": CHARACTER_CLASSES,
            "backgrounds": CHARACTER_BACKGROUNDS,
            "personalities": [
                "brave", "cautious", "curious", "hot-headed", "wise", "mischievous",
                "loyal", "independent", "cheerful", "serious", "witty", "stoic"
            ],
            "traits": {
                "all": list(self.trait_manager.traits.keys()),
                "by_category": {
                    category.value: [trait.name for trait in self.trait_manager.get_traits_by_category(category)]
                    for category in TraitCategory
                }
            },
            "starting_gear": {}
        }
        
        # Add starting gear choices
        if character_class:
            options["starting_gear"][character_class] = [
                {"name": choice.name, "description": choice.description}
                for choice in self.gear_manager.get_choices_for_class(character_class)
            ]
        else:
            for class_name in CHARACTER_CLASSES:
                options["starting_gear"][class_name] = [
                    {"name": choice.name, "description": choice.description}
                    for choice in self.gear_manager.get_choices_for_class(class_name)
                ]
        
        return options
    
    def save_characters(self):
        """Save characters to file"""
        try:
            with open('characters.json', 'w') as f:
                json.dump([char.to_dict() for char in self.characters], f, indent=2)
        except Exception as e:
            print(f"Error saving characters: {e}")
    
    def load_characters(self):
        """Load characters from file"""
        try:
            with open('characters.json', 'r') as f:
                data = json.load(f)
                self.characters = [Character.from_dict(char_data) for char_data in data]
        except FileNotFoundError:
            # Create some default characters if no file exists
            self._create_default_characters()
        except Exception as e:
            print(f"Error loading characters: {e}")
            self._create_default_characters()
    
    def _create_default_characters(self):
        """Create some default characters for demonstration"""
        default_chars = [
            ("Theron", "Warrior", "Soldier", "brave"),
            ("Lyra", "Mage", "Sage", "wise"), 
            ("Kael", "Rogue", "Criminal", "mischievous"),
            ("Sera", "Cleric", "Folk Hero", "loyal"),
            ("Gareth", "Paladin", "Noble", "righteous"),
            ("Zara", "Archer", "Outlander", "independent"),
            ("Felix", "Bard", "Entertainer", "cheerful"),
            ("Nyssa", "Druid", "Hermit", "wise")
        ]
        
        for name, char_class, background, personality in default_chars:
            self.create_character(name, char_class, background, personality)