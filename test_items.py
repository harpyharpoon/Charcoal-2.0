#!/usr/bin/env python3
"""
Test suite for the item system
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from items import Item, ItemType, ItemRarity, ItemStats, ItemGenerator


class TestItemSystem(unittest.TestCase):
    """Test the item creation and generation system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = ItemGenerator()
    
    def test_item_creation(self):
        """Test creating a basic item"""
        stats = ItemStats(attack=5, defense=2)
        item = Item(
            name="Test Sword",
            description="A sword for testing",
            item_type=ItemType.WEAPON,
            rarity=ItemRarity.COMMON,
            stats=stats,
            value=100
        )
        
        self.assertEqual(item.name, "Test Sword")
        self.assertEqual(item.item_type, ItemType.WEAPON)
        self.assertEqual(item.rarity, ItemRarity.COMMON)
        self.assertEqual(item.stats.attack, 5)
        self.assertEqual(item.stats.defense, 2)
    
    def test_item_display_name(self):
        """Test item display names with rarity indicators"""
        stats = ItemStats()
        
        common_item = Item("Sword", "A sword", ItemType.WEAPON, ItemRarity.COMMON, stats)
        legendary_item = Item("Excalibur", "Legendary sword", ItemType.WEAPON, ItemRarity.LEGENDARY, stats)
        
        self.assertEqual(common_item.get_display_name(), "Sword")
        self.assertEqual(legendary_item.get_display_name(), "Excalibur ★★★★")
    
    def test_item_generator_initialization(self):
        """Test that ItemGenerator initializes with templates"""
        self.assertGreater(len(self.generator.weapon_templates), 0)
        self.assertGreater(len(self.generator.armor_templates), 0)
        self.assertGreater(len(self.generator.relic_templates), 0)
        self.assertGreater(len(self.generator.consumable_templates), 0)
    
    def test_generate_specific_item_type(self):
        """Test generating items of specific types"""
        weapon = self.generator.generate_item(ItemType.WEAPON)
        armor = self.generator.generate_item(ItemType.ARMOR)
        relic = self.generator.generate_item(ItemType.RELIC)
        
        self.assertEqual(weapon.item_type, ItemType.WEAPON)
        self.assertEqual(armor.item_type, ItemType.ARMOR)
        self.assertEqual(relic.item_type, ItemType.RELIC)
    
    def test_generate_specific_rarity(self):
        """Test generating items of specific rarities"""
        common = self.generator.generate_item(rarity=ItemRarity.COMMON)
        legendary = self.generator.generate_item(rarity=ItemRarity.LEGENDARY)
        
        self.assertEqual(common.rarity, ItemRarity.COMMON)
        self.assertEqual(legendary.rarity, ItemRarity.LEGENDARY)
    
    def test_generate_treasure_for_area(self):
        """Test generating treasures for different area types"""
        boss_treasures = self.generator.generate_treasure_for_area("boss_room")
        regular_treasures = self.generator.generate_treasure_for_area("chamber")
        
        # Boss rooms should generally have more/better treasures
        self.assertIsInstance(boss_treasures, list)
        self.assertIsInstance(regular_treasures, list)
        
        # All generated items should be Item instances
        for item in boss_treasures + regular_treasures:
            self.assertIsInstance(item, Item)
    
    def test_item_stats_variety(self):
        """Test that different items have different stats"""
        items = [self.generator.generate_item() for _ in range(20)]
        
        # Should have some variety in stats
        attack_values = set(item.stats.attack for item in items)
        defense_values = set(item.stats.defense for item in items)
        
        # At least some variety should exist
        self.assertGreater(len(attack_values), 1)
        self.assertGreater(len(defense_values), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)