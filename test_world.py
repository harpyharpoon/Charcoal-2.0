#!/usr/bin/env python3
"""
Test suite for Charcoal 2.0 world and item systems
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from world import WorldManager, Area, AreaType, Dungeon
from character import CharacterManager, Character
from party import PartyManager, Party


class TestWorldSystem(unittest.TestCase):
    """Test the world generation and management system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.world_manager = WorldManager()
        self.character_manager = CharacterManager()
    
    def test_world_manager_initialization(self):
        """Test that WorldManager initializes correctly"""
        self.assertIsInstance(self.world_manager, WorldManager)
        self.assertIsInstance(self.world_manager.dungeons, dict)
        self.assertIn("ruins", self.world_manager.dungeons)
        self.assertIn("grove", self.world_manager.dungeons)
        self.assertIn("caves", self.world_manager.dungeons)
    
    def test_dungeon_creation(self):
        """Test that dungeons are created with areas"""
        ruins = self.world_manager.dungeons["ruins"]
        self.assertEqual(ruins.name, "Ancient Temple Ruins")
        self.assertEqual(ruins.theme, "ancient")
        self.assertIsInstance(ruins.areas, dict)
        self.assertIn("entrance", ruins.areas)
    
    def test_area_structure(self):
        """Test that areas have required attributes"""
        ruins = self.world_manager.dungeons["ruins"]
        entrance = ruins.areas["entrance"]
        
        self.assertIsInstance(entrance, Area)
        self.assertTrue(hasattr(entrance, 'name'))
        self.assertTrue(hasattr(entrance, 'description'))
        self.assertTrue(hasattr(entrance, 'enemies'))
        self.assertTrue(hasattr(entrance, 'treasures'))
        self.assertTrue(hasattr(entrance, 'exits'))
    
    def test_treasure_system(self):
        """Test that areas contain treasures"""
        found_items = []
        for dungeon in self.world_manager.dungeons.values():
            for area in dungeon.areas.values():
                found_items.extend(area.treasures)
        
        self.assertGreater(len(found_items), 0, "Should find some treasures")
        
        # Check that we have actual Item objects
        from items import Item
        for item in found_items:
            self.assertIsInstance(item, Item, "All treasures should be Item objects")
        
        # Check that we have variety in item types
        item_types = set(item.item_type.value for item in found_items)
        self.assertGreater(len(item_types), 1, "Should have variety in item types")


class TestCharacterSystem(unittest.TestCase):
    """Test the character creation and management system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.character_manager = CharacterManager()
    
    def test_character_creation(self):
        """Test creating a new character"""
        char = self.character_manager.create_character("TestHero", "Warrior", "Noble", "brave")
        self.assertEqual(char.name, "TestHero")
        self.assertEqual(char.character_class, "Warrior")
        self.assertEqual(char.background, "Noble")
        self.assertEqual(char.personality, "brave")
    
    def test_default_characters_exist(self):
        """Test that default characters are loaded"""
        characters = self.character_manager.list_characters()
        self.assertGreater(len(characters), 0, "Should have default characters")


class TestPartySystem(unittest.TestCase):
    """Test the party management system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.character_manager = CharacterManager()
        self.world_manager = WorldManager()
        self.party_manager = PartyManager(self.character_manager, self.world_manager)
    
    def test_party_creation(self):
        """Test creating a party"""
        characters = self.character_manager.list_characters()[:3]  # Take first 3 characters
        party = Party("Test Party", characters)
        
        self.assertEqual(party.name, "Test Party")
        self.assertEqual(len(party.characters), 3)
        self.assertEqual(len(party.inventory), 0)
        self.assertTrue(party.active)
    
    def test_party_inventory(self):
        """Test party inventory system"""
        characters = self.character_manager.list_characters()[:2]
        party = Party("Test Party", characters)
        
        # Add some items to inventory
        from items import Item, ItemType, ItemRarity, ItemStats
        test_sword = Item("Test Sword", "A sword for testing", ItemType.WEAPON, ItemRarity.COMMON, ItemStats(attack=5))
        test_shield = Item("Test Shield", "A shield for testing", ItemType.ARMOR, ItemRarity.COMMON, ItemStats(defense=3))
        
        party.inventory.append(test_sword)
        party.inventory.append(test_shield)
        
        self.assertEqual(len(party.inventory), 2)
        self.assertIn(test_sword, party.inventory)
        self.assertIn(test_shield, party.inventory)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()