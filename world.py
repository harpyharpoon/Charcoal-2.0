import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from items import Item, item_generator


class AreaType(Enum):
    ENTRANCE = "entrance"
    CHAMBER = "chamber"
    CORRIDOR = "corridor"
    BOSS_ROOM = "boss_room"
    TREASURE_ROOM = "treasure_room"
    TRAP_ROOM = "trap_room"
    PUZZLE_ROOM = "puzzle_room"
    SECRET_ROOM = "secret_room"
    SANCTUM = "sanctum"


@dataclass
class Area:
    """Represents an area within a dungeon"""
    name: str
    description: str
    area_type: AreaType
    enemies: List[str]
    treasures: List[Item]  # Changed from List[str] to List[Item]
    exits: List[str]
    difficulty: int = 1
    discovered: bool = False
    
    def get_description(self) -> str:
        """Get a detailed description of the area"""
        desc = f"**{self.name}**\n{self.description}"
        if self.enemies:
            desc += f"\n*Potential threats: {', '.join(self.enemies)}*"
        if self.treasures:
            treasure_names = [item.get_display_name() for item in self.treasures]
            desc += f"\n*Treasures spotted: {', '.join(treasure_names)}*"
        if self.exits:
            desc += f"\n*Exits lead to: {', '.join(self.exits)}*"
        return desc


class Dungeon:
    """Represents a dungeon with multiple areas"""
    
    def __init__(self, name: str, theme: str = "ancient"):
        self.name = name
        self.theme = theme
        self.areas: Dict[str, Area] = {}
        self.current_area = "entrance"
        self.generate_dungeon()
    
    def generate_dungeon(self):
        """Generate a random dungeon layout"""
        # Define area templates based on theme
        if self.theme == "ancient":
            self._generate_ancient_dungeon()
        elif self.theme == "forest":
            self._generate_forest_dungeon()
        elif self.theme == "underground":
            self._generate_underground_dungeon()
        elif self.theme == "tower":
            self._generate_tower_dungeon()
        else:
            self._generate_ancient_dungeon()
    
    def _generate_treasures_for_area_type(self, area_type: AreaType, num_items: int = None) -> List[Item]:
        """Generate appropriate treasures for an area type"""
        return item_generator.generate_treasure_for_area(area_type.value, difficulty=self._get_area_difficulty(area_type))
    
    def _get_area_difficulty(self, area_type: AreaType) -> int:
        """Get difficulty level for area type"""
        difficulty_map = {
            AreaType.ENTRANCE: 1,
            AreaType.CORRIDOR: 1,
            AreaType.CHAMBER: 2,
            AreaType.TRAP_ROOM: 3,
            AreaType.PUZZLE_ROOM: 3,
            AreaType.SECRET_ROOM: 4,
            AreaType.TREASURE_ROOM: 4,
            AreaType.SANCTUM: 5,
            AreaType.BOSS_ROOM: 5
        }
        return difficulty_map.get(area_type, 2)
    
    def _generate_ancient_dungeon(self):
        """Generate an ancient temple/ruins dungeon"""
        areas = {
            "entrance": Area(
                name="Temple Entrance",
                description="Crumbling stone pillars frame the entrance to an ancient temple. Moss covers the weathered reliefs.",
                area_type=AreaType.ENTRANCE,
                enemies=["Stone Guardian"],
                treasures=self._generate_treasures_for_area_type(AreaType.ENTRANCE),
                exits=["main_hall", "side_chamber"]
            ),
            "main_hall": Area(
                name="Grand Hall",
                description="A vast chamber with a vaulted ceiling. Broken statues line the walls, and dust motes dance in shafts of light.",
                area_type=AreaType.CHAMBER,
                enemies=["Skeletal Warrior", "Shadow"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["entrance", "throne_room", "crypt"]
            ),
            "side_chamber": Area(
                name="Scribe's Chamber",
                description="A smaller room filled with ancient scrolls and stone tablets. Some writings still glow with magical energy.",
                area_type=AreaType.CHAMBER,
                enemies=["Animated Book", "Wisp"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["entrance", "hidden_passage"]
            ),
            "throne_room": Area(
                name="Throne Room",
                description="A majestic chamber dominated by a massive stone throne. The air hums with ancient power.",
                area_type=AreaType.BOSS_ROOM,
                enemies=["Ancient King", "Royal Guards"],
                treasures=self._generate_treasures_for_area_type(AreaType.BOSS_ROOM),
                exits=["main_hall"]
            ),
            "crypt": Area(
                name="Sacred Crypt",
                description="A solemn burial chamber with ornate sarcophagi. The air is cold and still.",
                area_type=AreaType.CHAMBER,
                enemies=["Undead Priest", "Spectral Warriors"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["main_hall", "treasure_vault"]
            ),
            "hidden_passage": Area(
                name="Secret Tunnel",
                description="A narrow passage hidden behind a false wall. The path winds deeper into darkness.",
                area_type=AreaType.CORRIDOR,
                enemies=["Cave Spider"],
                treasures=self._generate_treasures_for_area_type(AreaType.CORRIDOR),
                exits=["side_chamber", "treasure_vault"]
            ),
            "treasure_vault": Area(
                name="Ancient Vault",
                description="A sealed chamber filled with gleaming treasures and magical artifacts from a bygone era.",
                area_type=AreaType.TREASURE_ROOM,
                enemies=["Treasure Guardian", "Mimic Chest"],
                treasures=self._generate_treasures_for_area_type(AreaType.TREASURE_ROOM),
                exits=["crypt", "hidden_passage"]
            )
        }
        self.areas = areas
    
    def _generate_forest_dungeon(self):
        """Generate a forest grove dungeon"""
        areas = {
            "entrance": Area(
                name="Forest Edge",
                description="Ancient trees form a natural archway leading into a mystical grove. Flowers glow softly in the twilight.",
                area_type=AreaType.ENTRANCE,
                enemies=["Wild Wolf"],
                treasures=self._generate_treasures_for_area_type(AreaType.ENTRANCE),
                exits=["sacred_grove", "bramble_path"]
            ),
            "sacred_grove": Area(
                name="Sacred Grove",
                description="A circular clearing where ancient druids once gathered. The trees whisper ancient secrets.",
                area_type=AreaType.CHAMBER,
                enemies=["Dryad", "Treant Sapling"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["entrance", "spirit_pool", "elder_tree"]
            ),
            "bramble_path": Area(
                name="Thorny Passage",
                description="A winding path through dense brambles and thorns. Something moves in the shadows.",
                area_type=AreaType.CORRIDOR,
                enemies=["Thorn Beast", "Poison Ivy"],
                treasures=self._generate_treasures_for_area_type(AreaType.CORRIDOR),
                exits=["entrance", "spider_den"]
            ),
            "spirit_pool": Area(
                name="Moonlit Pool",
                description="A crystal-clear pool reflects the moon above. Ancient spirits dance on the water's surface.",
                area_type=AreaType.CHAMBER,
                enemies=["Water Spirit", "Reflection"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["sacred_grove", "elder_tree"]
            ),
            "elder_tree": Area(
                name="The Elder Tree",
                description="A massive ancient tree towers above all others. Its trunk is hollow, forming a natural cathedral.",
                area_type=AreaType.BOSS_ROOM,
                enemies=["Elder Treant", "Forest Guardians"],
                treasures=self._generate_treasures_for_area_type(AreaType.BOSS_ROOM),
                exits=["sacred_grove", "spirit_pool"]
            ),
            "spider_den": Area(
                name="Spider's Lair",
                description="Thick webs stretch between the trees, creating a maze of silk and shadow.",
                area_type=AreaType.TRAP_ROOM,
                enemies=["Giant Spider", "Web Crawler"],
                treasures=self._generate_treasures_for_area_type(AreaType.TRAP_ROOM),
                exits=["bramble_path"]
            )
        }
        self.areas = areas
    
    def _generate_underground_dungeon(self):
        """Generate an underground cave system"""
        areas = {
            "entrance": Area(
                name="Cave Mouth",
                description="A dark opening in the mountainside. Cool air flows from the depths, carrying strange echoes.",
                area_type=AreaType.ENTRANCE,
                enemies=["Cave Bat"],
                treasures=self._generate_treasures_for_area_type(AreaType.ENTRANCE),
                exits=["main_tunnel", "shallow_cave"]
            ),
            "main_tunnel": Area(
                name="Main Passage",
                description="A wide tunnel carved by ancient waters. Glowing fungi provide eerie illumination.",
                area_type=AreaType.CORRIDOR,
                enemies=["Cave Goblin", "Rock Worm"],
                treasures=self._generate_treasures_for_area_type(AreaType.CORRIDOR),
                exits=["entrance", "underground_lake", "crystal_cavern"]
            ),
            "shallow_cave": Area(
                name="Shallow Grotto",
                description="A small cave chamber with a low ceiling. Strange symbols are carved into the walls.",
                area_type=AreaType.CHAMBER,
                enemies=["Cave Bear"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["entrance", "hidden_chamber"]
            ),
            "underground_lake": Area(
                name="Subterranean Lake",
                description="A vast underground lake stretches into darkness. The water is perfectly still and black as night.",
                area_type=AreaType.CHAMBER,
                enemies=["Lake Monster", "Blind Fish"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["main_tunnel", "crystal_cavern"]
            ),
            "crystal_cavern": Area(
                name="Crystal Chamber",
                description="A breathtaking cavern filled with massive crystals that pulse with inner light.",
                area_type=AreaType.TREASURE_ROOM,
                enemies=["Crystal Golem", "Living Crystal"],
                treasures=self._generate_treasures_for_area_type(AreaType.TREASURE_ROOM),
                exits=["main_tunnel", "underground_lake", "deep_chasm"]
            ),
            "hidden_chamber": Area(
                name="Secret Chamber",
                description="A hidden room behind a rock fall. Ancient tools and weapons are scattered about.",
                area_type=AreaType.CHAMBER,
                enemies=["Undead Miner"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["shallow_cave"]
            ),
            "deep_chasm": Area(
                name="The Abyss",
                description="A terrifying chasm that drops into bottomless darkness. Strange sounds echo from below.",
                area_type=AreaType.BOSS_ROOM,
                enemies=["Chasm Lord", "Shadow Spawn"],
                treasures=self._generate_treasures_for_area_type(AreaType.BOSS_ROOM),
                exits=["crystal_cavern"]
            )
        }
        self.areas = areas
    
    def _generate_tower_dungeon(self):
        """Generate a multi-level wizard's tower"""
        areas = {
            "entrance": Area(
                name="Tower Base",
                description="The base of a towering spire of dark stone. Arcane symbols pulse with blue light around the entrance.",
                area_type=AreaType.ENTRANCE,
                enemies=["Magical Ward", "Summoned Guard"],
                treasures=self._generate_treasures_for_area_type(AreaType.ENTRANCE),
                exits=["ground_floor", "garden"]
            ),
            "ground_floor": Area(
                name="Ground Floor",
                description="A circular chamber filled with floating books and swirling magical energies. Stairs spiral upward.",
                area_type=AreaType.CHAMBER,
                enemies=["Animated Tome", "Magic Missile Trap"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["entrance", "second_floor", "basement"]
            ),
            "second_floor": Area(
                name="Second Floor",
                description="An alchemical laboratory with bubbling cauldrons and shelves of glowing reagents.",
                area_type=AreaType.CHAMBER,
                enemies=["Alchemical Golem", "Poison Cloud"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["ground_floor", "third_floor"]
            ),
            "third_floor": Area(
                name="Third Floor",
                description="A divination chamber where crystal spheres float in mid-air, showing glimpses of distant places.",
                area_type=AreaType.PUZZLE_ROOM,
                enemies=["Scrying Eye", "Time Phantom"],
                treasures=self._generate_treasures_for_area_type(AreaType.PUZZLE_ROOM),
                exits=["second_floor", "top_floor", "secret_chamber"]
            ),
            "top_floor": Area(
                name="Archmage's Sanctum",
                description="The tower's peak, where a powerful archmage once commanded the very forces of magic itself.",
                area_type=AreaType.BOSS_ROOM,
                enemies=["Archmage's Spirit", "Elemental Guardians"],
                treasures=self._generate_treasures_for_area_type(AreaType.BOSS_ROOM),
                exits=["third_floor"]
            ),
            "basement": Area(
                name="Hidden Vault",
                description="A hidden chamber beneath the tower, sealed with powerful enchantments.",
                area_type=AreaType.TREASURE_ROOM,
                enemies=["Vault Guardian", "Magical Trap"],
                treasures=self._generate_treasures_for_area_type(AreaType.TREASURE_ROOM),
                exits=["ground_floor"]
            ),
            "secret_chamber": Area(
                name="Secret Study",
                description="A hidden room behind a magical illusion, containing the wizard's most private research.",
                area_type=AreaType.SECRET_ROOM,
                enemies=["Bound Demon", "Cursed Manuscript"],
                treasures=self._generate_treasures_for_area_type(AreaType.SECRET_ROOM),
                exits=["third_floor"]
            ),
            "garden": Area(
                name="Enchanted Garden",
                description="A mystical garden where magical plants grow under an eternal twilight sky.",
                area_type=AreaType.CHAMBER,
                enemies=["Carnivorous Plant", "Garden Sprite"],
                treasures=self._generate_treasures_for_area_type(AreaType.CHAMBER),
                exits=["entrance"]
            )
        }
        self.areas = areas
    
    def get_current_area(self) -> Area:
        """Get the current area"""
        return self.areas[self.current_area]
    
    def move_to_area(self, area_name: str) -> bool:
        """Move to a new area if possible"""
        current = self.get_current_area()
        if area_name in current.exits and area_name in self.areas:
            self.current_area = area_name
            self.areas[area_name].discovered = True
            return True
        return False
    
    def get_available_moves(self) -> List[str]:
        """Get list of areas the party can move to"""
        return self.get_current_area().exits
    
    def get_dungeon_info(self) -> str:
        """Get information about the dungeon"""
        discovered_count = sum(1 for area in self.areas.values() if area.discovered)
        total_count = len(self.areas)
        return f"**{self.name}** ({self.theme} theme)\nAreas discovered: {discovered_count}/{total_count}"


class WorldManager:
    """Manages the game world and dungeons"""
    
    def __init__(self):
        self.dungeons: Dict[str, Dungeon] = {}
        self.current_dungeon: Optional[str] = None
        self._create_default_dungeons()
    
    def _create_default_dungeons(self):
        """Create some default dungeons"""
        self.dungeons["ruins"] = Dungeon("Ancient Temple Ruins", "ancient")
        self.dungeons["grove"] = Dungeon("Enchanted Grove", "forest")
        self.dungeons["caves"] = Dungeon("Crystal Caves", "underground")
        self.dungeons["tower"] = Dungeon("Wizard's Tower", "tower")
        
        # Start in the first dungeon
        self.current_dungeon = "ruins"
        self.dungeons[self.current_dungeon].areas["entrance"].discovered = True
    
    def get_current_dungeon(self) -> Optional[Dungeon]:
        """Get the current dungeon"""
        if self.current_dungeon:
            return self.dungeons[self.current_dungeon]
        return None
    
    def change_dungeon(self, dungeon_name: str) -> bool:
        """Change to a different dungeon"""
        if dungeon_name in self.dungeons:
            self.current_dungeon = dungeon_name
            self.dungeons[dungeon_name].areas["entrance"].discovered = True
            return True
        return False
    
    def list_dungeons(self) -> List[str]:
        """Get list of available dungeons"""
        return list(self.dungeons.keys())
    
    def get_world_status(self) -> str:
        """Get current world status"""
        if not self.current_dungeon:
            return "No active dungeon"
        
        dungeon = self.get_current_dungeon()
        area = dungeon.get_current_area()
        return f"Currently in: {dungeon.name} - {area.name}"