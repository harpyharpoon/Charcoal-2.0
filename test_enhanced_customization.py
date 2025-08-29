#!/usr/bin/env python3
"""
Test the enhanced character customization and gear synergy systems
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import CharacterManager, Character, CharacterStats
from character_traits import TraitManager, TraitCategory, StartingGearManager
from gear_synergy import GearSynergyManager, SynergyType
from items import ItemGenerator, Item, ItemType, ItemRarity, ItemStats


class TestEnhancedCustomization(unittest.TestCase):
    """Test the enhanced character customization system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.char_manager = CharacterManager()
        self.trait_manager = TraitManager()
        self.gear_manager = StartingGearManager()
        self.synergy_manager = GearSynergyManager()
        self.item_generator = ItemGenerator()
    
    def test_trait_system_initialization(self):
        """Test that the trait system initializes correctly"""
        self.assertGreater(len(self.trait_manager.traits), 10)
        
        # Test trait categories
        combat_traits = self.trait_manager.get_traits_by_category(TraitCategory.COMBAT)
        self.assertGreater(len(combat_traits), 0)
        
        social_traits = self.trait_manager.get_traits_by_category(TraitCategory.SOCIAL)
        self.assertGreater(len(social_traits), 0)
    
    def test_enhanced_character_creation(self):
        """Test creating characters with enhanced customization"""
        # Create a custom character with traits
        character = self.char_manager.create_character(
            name="TestHero",
            character_class="Warrior",
            background="Soldier",
            personality="brave",
            traits=["Battle Hardened", "Natural Leader"],
            permadeath_enabled=True
        )
        
        self.assertEqual(character.name, "TestHero")
        self.assertEqual(character.character_class, "Warrior")
        self.assertIn("Battle Hardened", character.traits)
        self.assertIn("Natural Leader", character.traits)
        self.assertTrue(character.permadeath_enabled)
        
        # Test that stats were enhanced
        self.assertIsInstance(character.stats, CharacterStats)
        self.assertGreater(character.stats.strength, 10)  # Should have class bonus
    
    def test_trait_effects_application(self):
        """Test that trait effects are properly applied"""
        character = self.char_manager.create_character(
            name="TraitTest",
            character_class="Mage",
            traits=["Arcane Scholar", "Mana Touched"]
        )
        
        # Apply trait effects
        effects = character.apply_trait_effects(self.trait_manager)
        
        # Should have magic-related bonuses
        self.assertIn("magic_power_bonus", effects)
        self.assertGreater(effects["magic_power_bonus"], 0)
    
    def test_starting_gear_choices(self):
        """Test the starting gear choice system"""
        # Get choices for a warrior
        choices = self.gear_manager.get_choices_for_class("Warrior")
        self.assertGreater(len(choices), 0)
        
        # Check choice structure
        first_choice = choices[0]
        self.assertTrue(hasattr(first_choice, 'name'))
        self.assertTrue(hasattr(first_choice, 'description'))
        self.assertTrue(hasattr(first_choice, 'items'))
    
    def test_character_customization_options(self):
        """Test getting available customization options"""
        options = self.char_manager.get_character_customization_options("Warrior")
        
        self.assertIn("classes", options)
        self.assertIn("backgrounds", options)
        self.assertIn("personalities", options)
        self.assertIn("traits", options)
        self.assertIn("starting_gear", options)
        
        # Check traits are organized by category
        self.assertIn("by_category", options["traits"])
        self.assertIn("combat", options["traits"]["by_category"])
    
    def test_gear_synergy_system(self):
        """Test the gear synergy system"""
        # Create some items
        items = [
            Item("Flameforge Hammer", "A fiery hammer", ItemType.WEAPON, 
                 ItemRarity.RARE, ItemStats(attack=8)),
            Item("Dragon Scale Mail", "Armor made from dragon scales", ItemType.ARMOR,
                 ItemRarity.EPIC, ItemStats(defense=12))
        ]
        
        # Analyze synergies
        synergies = self.synergy_manager.analyze_equipment_synergies(items)
        
        self.assertIn("set_bonuses", synergies)
        self.assertIn("elemental_synergies", synergies)
    
    def test_set_bonus_detection(self):
        """Test that set bonuses are detected correctly"""
        # Create items from the same set
        flameguard_items = [
            Item("Flameforge Hammer", "A fiery hammer", ItemType.WEAPON,
                 ItemRarity.RARE, ItemStats(attack=8)),
            Item("Dragon Scale Mail", "Dragon armor", ItemType.ARMOR,
                 ItemRarity.EPIC, ItemStats(defense=12))
        ]
        
        synergies = self.synergy_manager.analyze_equipment_synergies(flameguard_items)
        
        # Should detect set bonus
        self.assertGreater(len(synergies["set_bonuses"]), 0)
    
    def test_synergy_recommendations(self):
        """Test synergy recommendations system"""
        current_items = [
            Item("Flameforge Hammer", "A fiery hammer", ItemType.WEAPON,
                 ItemRarity.RARE, ItemStats(attack=8))
        ]
        
        recommendations = self.synergy_manager.get_synergy_recommendations(current_items)
        
        # Should suggest items to complete sets
        self.assertIsInstance(recommendations, list)
    
    def test_permadeath_mechanics(self):
        """Test permadeath and risk calculation"""
        character = self.char_manager.create_character(
            name="RiskTaker",
            character_class="Rogue",
            personality="hot-headed",
            permadeath_enabled=True
        )
        
        # Test risk tolerance calculation
        risk_tolerance = character.get_risk_tolerance()
        self.assertIsInstance(risk_tolerance, float)
        self.assertGreater(risk_tolerance, 0)
        self.assertLess(risk_tolerance, 1)
        
        # Test death risk calculation
        death_risk = character.calculate_death_risk(50)  # Medium danger situation
        self.assertIsInstance(death_risk, float)
        self.assertGreaterEqual(death_risk, 0)
        self.assertLessEqual(death_risk, 1)
    
    def test_legacy_compatibility(self):
        """Test that the system is compatible with existing characters"""
        # Create a character with old format
        old_char_data = {
            "name": "Legacy",
            "character_class": "Warrior", 
            "background": "Soldier",
            "personality": "brave",
            "hp": 100,
            "level": 1,
            "experience": 0,
            "description": "A legacy character"
        }
        
        # Should be able to load this character
        character = Character.from_dict(old_char_data)
        self.assertEqual(character.name, "Legacy")
        self.assertIsInstance(character.stats, CharacterStats)
        self.assertEqual(character.stats.hp, 100)
    
    def test_synergy_display_formatting(self):
        """Test that synergy display is properly formatted"""
        items = [
            Item("Flameforge Hammer", "A fiery hammer", ItemType.WEAPON,
                 ItemRarity.RARE, ItemStats(attack=8)),
            Item("Dragon Scale Mail", "Dragon armor", ItemType.ARMOR,
                 ItemRarity.EPIC, ItemStats(defense=12))
        ]
        
        synergies = self.synergy_manager.analyze_equipment_synergies(items)
        display = self.synergy_manager.format_synergy_display(synergies)
        
        self.assertIsInstance(display, str)
        self.assertIn("Synergies", display)


def run_showcase():
    """Run a showcase of the enhanced features"""
    print("🎭 Enhanced Character Customization & Gear Synergy Showcase")
    print("=" * 65)
    
    char_manager = CharacterManager()
    trait_manager = TraitManager()
    synergy_manager = GearSynergyManager()
    item_generator = ItemGenerator()
    
    # Show customization options
    print("\n🎨 Character Customization Options:")
    options = char_manager.get_character_customization_options("Warrior")
    print(f"  Classes: {len(options['classes'])}")
    print(f"  Backgrounds: {len(options['backgrounds'])}")
    print(f"  Personalities: {len(options['personalities'])}")
    print(f"  Total Traits: {len(options['traits']['all'])}")
    
    # Show trait categories
    print("\n🎯 Trait Categories:")
    for category, traits in options['traits']['by_category'].items():
        print(f"  {category.title()}: {len(traits)} traits")
    
    # Create an enhanced character
    print("\n👤 Creating Enhanced Character:")
    character = char_manager.create_character(
        name="Synergia",
        character_class="Warrior",
        background="Soldier",
        personality="brave",
        traits=["Battle Hardened", "Weapon Master", "Natural Leader"],
        permadeath_enabled=True
    )
    
    print(f"  Name: {character.name}")
    print(f"  Class: {character.character_class}")
    print(f"  Traits: {', '.join(character.traits)}")
    print(f"  Permadeath: {character.permadeath_enabled}")
    print(f"  Stats: STR {character.stats.strength}, DEX {character.stats.dexterity}, INT {character.stats.intelligence}")
    
    # Show gear synergies
    print("\n⚔️ Gear Synergy Examples:")
    test_items = [
        item_generator.generate_item(ItemType.WEAPON, ItemRarity.RARE),
        item_generator.generate_item(ItemType.ARMOR, ItemRarity.RARE),
        item_generator.generate_item(ItemType.RELIC, ItemRarity.UNCOMMON)
    ]
    
    print("  Equipped Items:")
    for item in test_items:
        print(f"    • {item.get_display_name()} - {item.description}")
    
    synergies = synergy_manager.analyze_equipment_synergies(test_items)
    recommendations = synergy_manager.get_synergy_recommendations(test_items)
    
    print(f"\n  Active Synergies: {len([b for bonuses in synergies.values() for b in bonuses])}")
    print(f"  Recommendations: {len(recommendations)}")
    
    # Show available item sets
    print("\n🛡️ Available Item Sets:")
    for set_name, item_set in synergy_manager.item_sets.items():
        print(f"  {item_set.name} ({len(item_set.items)} items)")
        print(f"    Theme: {item_set.theme}")
        print(f"    Bonuses: {len(item_set.bonuses)} tiers")
    
    print("\n✅ Enhanced systems ready for adventure!")


if __name__ == "__main__":
    # Run showcase first
    run_showcase()
    
    print("\n" + "=" * 65)
    print("Running comprehensive tests...")
    
    # Run tests
    unittest.main(verbosity=2, exit=False)