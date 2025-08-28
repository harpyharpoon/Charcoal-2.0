import json
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from config import CHARACTER_CLASSES, CHARACTER_BACKGROUNDS


@dataclass
class Character:
    """Represents an AI character in the game"""
    name: str
    character_class: str
    background: str
    personality: str
    hp: int = 100
    level: int = 1
    experience: int = 0
    description: str = ""
    
    def __post_init__(self):
        if not self.description:
            self.description = f"A {self.background.lower()} {self.character_class.lower()} with a {self.personality.lower()} personality"
    
    def to_dict(self) -> Dict:
        """Convert character to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        """Create character from dictionary"""
        return cls(**data)
    
    def get_prompt_context(self) -> str:
        """Get character context for AI prompts"""
        return (f"You are {self.name}, a {self.background.lower()} {self.character_class.lower()}. "
                f"You have a {self.personality.lower()} personality. {self.description}")


class CharacterManager:
    """Manages character creation, storage, and retrieval"""
    
    def __init__(self):
        self.characters: List[Character] = []
        self.load_characters()
    
    def create_character(self, name: str, character_class: str = None, 
                        background: str = None, personality: str = None) -> Character:
        """Create a new character with random or specified attributes"""
        if character_class is None:
            character_class = random.choice(CHARACTER_CLASSES)
        if background is None:
            background = random.choice(CHARACTER_BACKGROUNDS)
        if personality is None:
            personality = random.choice([
                "brave", "cautious", "curious", "hot-headed", "wise", "mischievous",
                "loyal", "independent", "cheerful", "serious", "witty", "stoic"
            ])
        
        character = Character(
            name=name,
            character_class=character_class,
            background=background,
            personality=personality
        )
        
        self.characters.append(character)
        self.save_characters()
        return character
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get character by name"""
        for char in self.characters:
            if char.name.lower() == name.lower():
                return char
        return None
    
    def list_characters(self) -> List[Character]:
        """Get all characters"""
        return self.characters.copy()
    
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