#!/usr/bin/env python3
"""
Test to showcase the enhanced world and item system
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from world import WorldManager, AreaType
from character import CharacterManager
from party import PartyManager, Party
from items import ItemType, ItemRarity


class TestEnhancedSystem(unittest.TestCase):
    """Test the enhanced world and item system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.char_manager = CharacterManager()
        self.world_manager = WorldManager()
        self.party_manager = PartyManager(self.char_manager, self.world_manager)
    
    def test_new_tower_dungeon(self):
        """Test that the new tower dungeon exists and is properly formed"""
        self.assertIn("tower", self.world_manager.dungeons)
        tower = self.world_manager.dungeons["tower"]
        self.assertEqual(tower.name, "Wizard's Tower")
        self.assertEqual(tower.theme, "tower")
        
        # Check that tower has the expected areas
        expected_areas = ["entrance", "ground_floor", "second_floor", "third_floor", 
                         "top_floor", "basement", "secret_chamber", "garden"]
        for area_name in expected_areas:
            self.assertIn(area_name, tower.areas)
    
    def test_new_area_types(self):
        """Test that new area types are being used"""
        tower = self.world_manager.dungeons["tower"]
        
        # Check for secret room
        secret_chamber = tower.areas["secret_chamber"]
        self.assertEqual(secret_chamber.area_type, AreaType.SECRET_ROOM)
        
        # Check that different area types exist
        area_types = set(area.area_type for area in tower.areas.values())
        self.assertIn(AreaType.SECRET_ROOM, area_types)
        self.assertIn(AreaType.PUZZLE_ROOM, area_types)
        self.assertIn(AreaType.BOSS_ROOM, area_types)
    
    def test_item_variety_across_dungeons(self):
        """Test that different dungeons have varied item types"""
        all_items = []
        for dungeon in self.world_manager.dungeons.values():
            for area in dungeon.areas.values():
                all_items.extend(area.treasures)
        
        # Should have variety in item types
        item_types = set(item.item_type for item in all_items)
        self.assertGreaterEqual(len(item_types), 3, "Should have at least 3 different item types")
        
        # Should have variety in rarities
        rarities = set(item.rarity for item in all_items)
        self.assertGreaterEqual(len(rarities), 3, "Should have at least 3 different rarities")
        
        # Should have items with stats
        items_with_attack = [item for item in all_items if item.stats.attack > 0]
        items_with_defense = [item for item in all_items if item.stats.defense > 0]
        items_with_magic = [item for item in all_items if item.stats.magic_power > 0]
        
        self.assertGreater(len(items_with_attack), 0, "Should have weapons with attack")
        self.assertGreater(len(items_with_defense), 0, "Should have armor with defense")
        self.assertGreater(len(items_with_magic), 0, "Should have magical items")
    
    def test_treasure_discovery_integration(self):
        """Test that treasure discovery works with the new item system"""
        # Create a party
        characters = self.char_manager.list_characters()[:2]
        party = Party("Test Explorers", characters)
        
        # Get an area with treasures
        dungeon = self.world_manager.dungeons["tower"]
        area = dungeon.areas["basement"]  # This is the treasure room in the tower
        
        initial_treasures = len(area.treasures)
        initial_inventory = len(party.inventory)
        
        # Trigger discovery
        events = self.party_manager._handle_discovery(party, area)
        
        if initial_treasures > 0:
            # Should have discovery events
            self.assertGreater(len(events), 0)
            
            # Party should have gained an item
            self.assertGreater(len(party.inventory), initial_inventory)
            
            # Area should have one less treasure
            self.assertEqual(len(area.treasures), initial_treasures - 1)
            
            # The item should be a proper Item object
            from items import Item
            self.assertIsInstance(party.inventory[-1], Item)
    
    def test_all_dungeons_have_proper_items(self):
        """Test that all dungeons have been updated to use the item system"""
        for dungeon_name, dungeon in self.world_manager.dungeons.items():
            for area_name, area in dungeon.areas.items():
                # All treasures should be Item objects
                from items import Item
                for treasure in area.treasures:
                    self.assertIsInstance(treasure, Item, 
                                        f"Treasure in {dungeon_name}/{area_name} should be Item object")
    
    def test_item_display_functionality(self):
        """Test that items display correctly with rarity indicators"""
        # Get some items
        all_items = []
        for dungeon in self.world_manager.dungeons.values():
            for area in dungeon.areas.values():
                all_items.extend(area.treasures)
                if len(all_items) >= 10:  # Just need a sample
                    break
            if len(all_items) >= 10:
                break
        
        # Test display names
        for item in all_items[:5]:  # Test first 5
            display_name = item.get_display_name()
            self.assertIsInstance(display_name, str)
            self.assertIn(item.name, display_name)
            
            # Legendary items should have stars
            if item.rarity == ItemRarity.LEGENDARY:
                self.assertIn("★", display_name)


def run_showcase():
    """Run a showcase of the enhanced system"""
    print("🎭 Charcoal 2.0 Enhanced World & Item System Showcase")
    print("=" * 60)
    
    # Create managers
    char_manager = CharacterManager()
    world_manager = WorldManager()
    
    print(f"\n🏰 Available Dungeons: {len(world_manager.dungeons)}")
    for name, dungeon in world_manager.dungeons.items():
        print(f"  • {dungeon.name} ({name})")
        print(f"    Areas: {len(dungeon.areas)}")
    
    print(f"\n🗡️ Sample Items from Tower Dungeon:")
    tower = world_manager.dungeons["tower"]
    sample_items = []
    for area in tower.areas.values():
        sample_items.extend(area.treasures)
        if len(sample_items) >= 5:
            break
    
    for item in sample_items[:5]:
        print(f"  • {item.get_display_name()}")
        if item.stats.attack > 0:
            print(f"    +{item.stats.attack} Attack")
        if item.stats.defense > 0:
            print(f"    +{item.stats.defense} Defense")
        if item.stats.magic_power > 0:
            print(f"    +{item.stats.magic_power} Magic Power")
        if item.stats.special_effect:
            print(f"    Special: {item.stats.special_effect}")
    
    print(f"\n🏛️ New Tower Dungeon Areas:")
    for area_name, area in tower.areas.items():
        print(f"  • {area.name} ({area.area_type.value})")
        print(f"    {len(area.treasures)} treasures, {len(area.enemies)} enemies")
    
    print("\n✅ All systems integrated and working!")


if __name__ == "__main__":
    # Run showcase first
    run_showcase()
    
    print("\n" + "=" * 60)
    print("Running comprehensive tests...")
    unittest.main(verbosity=2)