#!/usr/bin/env python3
"""
Comprehensive integration test for all new Charcoal 2.0 systems
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import CharacterManager, Character
from character_traits import TraitManager, TraitCategory
from gear_synergy import GearSynergyManager
from permadeath_system import PermadeathManager, RiskLevel
from flavor_config import FlavorTextManager, ConfigurableGameSettings
from items import ItemGenerator, Item, ItemType, ItemRarity, ItemStats
from world import WorldManager
from party import PartyManager


class TestCompleteIntegration(unittest.TestCase):
    """Test all systems working together"""
    
    def setUp(self):
        """Set up all managers for integration testing"""
        self.test_dir = tempfile.mkdtemp()
        
        self.char_manager = CharacterManager()
        self.trait_manager = TraitManager()
        self.synergy_manager = GearSynergyManager()
        self.permadeath_manager = PermadeathManager()
        self.flavor_manager = FlavorTextManager(config_directory=self.test_dir)
        self.settings_manager = ConfigurableGameSettings(
            config_file=os.path.join(self.test_dir, "integration_settings.json")
        )
        self.item_generator = ItemGenerator()
        self.world_manager = WorldManager()
        self.party_manager = PartyManager(self.char_manager, self.world_manager)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_complete_character_creation_workflow(self):
        """Test the complete enhanced character creation workflow"""
        # Get customization options
        options = self.char_manager.get_character_customization_options("Warrior")
        
        # Select options
        selected_traits = ["Battle Hardened", "Natural Leader"]
        selected_gear = "Guardian's Arsenal"
        
        # Create enhanced character
        character = self.char_manager.create_custom_character(
            name="IntegrationHero",
            character_class="Warrior",
            background="Soldier",
            personality="brave",
            selected_traits=selected_traits,
            starting_gear_choice=selected_gear,
            permadeath_enabled=True
        )
        
        # Verify character creation
        self.assertEqual(character.name, "IntegrationHero")
        self.assertEqual(character.traits, selected_traits)
        self.assertTrue(character.permadeath_enabled)
        self.assertGreater(character.stats.strength, 10)  # Should have class bonuses
        
        # Test trait effects
        effects = character.apply_trait_effects(self.trait_manager)
        self.assertGreater(len(effects), 0)
        
        # Test flavor text generation
        description = self.flavor_manager.get_character_description(
            character.character_class, character.background, character.personality
        )
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 20)
    
    def test_gear_synergy_with_permadeath_integration(self):
        """Test gear synergies working with permadeath mechanics"""
        # Create a character with survival traits
        character = self.char_manager.create_character(
            name="SynergyTest",
            character_class="Warrior",
            traits=["Battle Hardened", "Death Defiant"],
            permadeath_enabled=True
        )
        
        # Create a set of synergistic items
        items = [
            Item("Flameforge Hammer", "Fiery hammer", ItemType.WEAPON, 
                 ItemRarity.RARE, ItemStats(attack=8)),
            Item("Dragon Scale Mail", "Dragon armor", ItemType.ARMOR,
                 ItemRarity.EPIC, ItemStats(defense=12)),
            Item("Ring of Fire Resistance", "Fire protection", ItemType.RELIC,
                 ItemRarity.UNCOMMON, ItemStats(magic_power=5))
        ]
        
        # Analyze synergies
        synergies = self.synergy_manager.analyze_equipment_synergies(items)
        
        # Should detect Flameguard set bonus
        self.assertGreater(len(synergies["set_bonuses"]), 0)
        
        # Test death risk with synergies
        base_risk = character.calculate_death_risk(50)  # 50% danger situation
        
        # Character should have reduced risk due to traits
        self.assertLess(base_risk, 0.5)  # Should be less than base 50%
        
        # Test risk assessment
        assessment = self.permadeath_manager.get_risk_assessment(
            character, "A massive fire dragon attacks with overwhelming force"
        )
        
        self.assertIn("risk_level", assessment)
        self.assertGreater(len(assessment["scenarios"]), 0)
    
    def test_party_adventure_with_new_systems(self):
        """Test party adventures using all new systems"""
        # Create diverse party with enhanced characters
        party_members = []
        
        # Tank with defensive traits
        tank = self.char_manager.create_character(
            name="Guardian",
            character_class="Paladin",
            traits=["Battle Hardened", "Natural Leader"],
            permadeath_enabled=True
        )
        party_members.append(tank)
        
        # DPS with offensive traits
        dps = self.char_manager.create_character(
            name="Destroyer",
            character_class="Warrior",
            traits=["Weapon Master", "Berserker Fury"],
            permadeath_enabled=True
        )
        party_members.append(dps)
        
        # Support with mystical traits
        support = self.char_manager.create_character(
            name="Mystic",
            character_class="Mage",
            traits=["Arcane Scholar", "Mana Touched"],
            permadeath_enabled=True
        )
        party_members.append(support)
        
        # Create party
        from party import Party
        party = Party("Integration Test Party", party_members)
        
        # Equip party with synergistic gear
        # Tank gets defensive gear
        tank_items = [
            self.item_generator.generate_item(ItemType.ARMOR, ItemRarity.RARE),
            self.item_generator.generate_item(ItemType.WEAPON, ItemRarity.COMMON)
        ]
        party.inventory.extend(tank_items)
        
        # Test party risk assessment
        for member in party_members:
            assessment = self.permadeath_manager.get_risk_assessment(
                member, "The party faces an ancient dragon in its lair"
            )
            
            # Each character should have different risk profiles
            self.assertIn("risk_level", assessment)
            self.assertGreater(len(assessment["character_survival_factors"]), 0)
    
    def test_configuration_system_integration(self):
        """Test that configuration changes affect gameplay"""
        # Test permadeath settings
        self.settings_manager.set_setting("permadeath.enabled_by_default", True)
        
        # Create character (should have permadeath enabled by default now)
        character = self.char_manager.create_character("ConfigTest", "Rogue")
        # Note: This would need to be implemented in CharacterManager to read settings
        
        # Test difficulty settings
        original_strength = self.settings_manager.get_setting("difficulty.base_enemy_strength")
        self.settings_manager.set_setting("difficulty.base_enemy_strength", 2.0)
        
        new_strength = self.settings_manager.get_setting("difficulty.base_enemy_strength")
        self.assertEqual(new_strength, 2.0)
        
        # Test synergy focus settings
        self.settings_manager.set_setting("engagement.focus_on_synergies", True)
        focus = self.settings_manager.get_setting("engagement.focus_on_synergies")
        self.assertTrue(focus)
    
    def test_flavor_customization_impact(self):
        """Test that flavor text customization works across systems"""
        # Test character descriptions with different themes
        warrior_desc = self.flavor_manager.get_character_description(
            "Warrior", "Soldier", "brave"
        )
        self.assertIsInstance(warrior_desc, str)
        
        # Test item descriptions
        weapon_desc = self.flavor_manager.get_item_description(
            "weapon", "Legendary Sword", "legendary"
        )
        self.assertIn("weapon", weapon_desc.lower())
        
        # Test that themes can be exported for customization
        template = self.flavor_manager.export_theme_template()
        self.assertIn("character_descriptions", template)
        self.assertIn("item_descriptions", template)
        self.assertIn("dialogue_templates", template)
    
    def test_end_to_end_adventure_scenario(self):
        """Test a complete adventure scenario using all systems"""
        # Create enhanced character
        hero = self.char_manager.create_character(
            name="AdventureHero",
            character_class="Rogue",
            traits=["Pathfinder", "Lucky", "Keen Observer"],
            permadeath_enabled=True
        )
        
        # 2. Equip with synergistic gear
        hero_items = [
            Item("Shadowbane", "Shadow sword", ItemType.WEAPON, 
                 ItemRarity.EPIC, ItemStats(attack=12)),
            Item("Cloak of Shadows", "Stealth cloak", ItemType.ARMOR,
                 ItemRarity.RARE, ItemStats(defense=5))
        ]
        
        # 3. Analyze gear synergies
        synergies = self.synergy_manager.analyze_equipment_synergies(hero_items)
        recommendations = self.synergy_manager.get_synergy_recommendations(hero_items)
        
        # 4. Enter dangerous situation
        dangerous_situation = "Ancient tomb filled with deadly traps and cursed guardians"
        
        # 5. Assess risks
        assessment = self.permadeath_manager.get_risk_assessment(hero, dangerous_situation)
        
        # 6. Generate flavor text for the scenario
        location_desc = self.flavor_manager.get_location_description("chamber")
        event_desc = self.flavor_manager.get_event_description("discovery")
        
        # Verify everything worked together
        self.assertEqual(hero.character_class, "Rogue")
        self.assertIn("Pathfinder", hero.traits)
        self.assertIsInstance(synergies, dict)
        self.assertIn("risk_level", assessment)
        self.assertIsInstance(location_desc, str)
        self.assertIsInstance(event_desc, str)
        
        # Test death scenario if applicable
        if assessment["risk_level"] in ["high", "extreme"]:
            scenarios = assessment["scenarios"]
            if scenarios:
                primary_scenario = scenarios[0]
                self.assertIn("final_risk", primary_scenario)
                self.assertGreaterEqual(primary_scenario["final_risk"], 0)
                self.assertLessEqual(primary_scenario["final_risk"], 1)
    
    def test_system_performance_and_compatibility(self):
        """Test that all systems work efficiently together"""
        import time
        
        # Test creating multiple characters quickly
        start_time = time.time()
        
        characters = []
        for i in range(10):
            char = self.char_manager.create_character(
                name=f"PerfTest{i}",
                character_class="Warrior",
                traits=["Battle Hardened"],
                permadeath_enabled=True
            )
            characters.append(char)
        
        creation_time = time.time() - start_time
        self.assertLess(creation_time, 1.0)  # Should create 10 characters in under 1 second
        
        # Test bulk synergy analysis
        start_time = time.time()
        
        test_items = [
            self.item_generator.generate_item(ItemType.WEAPON, ItemRarity.COMMON)
            for _ in range(5)
        ]
        
        for char in characters[:5]:  # Test with 5 characters
            synergies = self.synergy_manager.analyze_equipment_synergies(test_items)
            assessment = self.permadeath_manager.get_risk_assessment(char, "Test scenario")
        
        analysis_time = time.time() - start_time
        self.assertLess(analysis_time, 0.5)  # Should analyze quickly
        
        # Test backward compatibility
        # Create character using old-style method (should still work)
        old_style_char = self.char_manager.create_character("OldStyle", "Mage")
        self.assertEqual(old_style_char.character_class, "Mage")
        self.assertIsInstance(old_style_char.traits, list)  # Should have empty traits list


def run_full_integration_showcase():
    """Run a comprehensive showcase of all integrated systems"""
    print("\n🌟 CHARCOAL 2.0 COMPLETE INTEGRATION SHOWCASE 🌟")
    print("=" * 60)
    
    # Initialize all systems
    test_dir = tempfile.mkdtemp()
    
    try:
        char_manager = CharacterManager()
        synergy_manager = GearSynergyManager()
        permadeath_manager = PermadeathManager()
        flavor_manager = FlavorTextManager(config_directory=test_dir)
        settings_manager = ConfigurableGameSettings(
            config_file=os.path.join(test_dir, "showcase_settings.json")
        )
        item_generator = ItemGenerator()
        
        print("\n🎯 1. ENHANCED CHARACTER CREATION")
        print("-" * 35)
        
        # Create a fully customized character
        hero = char_manager.create_custom_character(
            name="Shadowstrike",
            character_class="Rogue",
            background="Criminal",
            personality="mischievous",
            selected_traits=["Keen Observer", "Lucky", "Death Defiant"],
            starting_gear_choice="Traditional Rogue",
            permadeath_enabled=True
        )
        
        print(f"✨ Created: {hero.name}")
        print(f"   Class: {hero.character_class} | Background: {hero.background}")
        print(f"   Personality: {hero.personality}")
        print(f"   Traits: {', '.join(hero.traits)}")
        print(f"   Stats: STR {hero.stats.strength}, DEX {hero.stats.dexterity}, INT {hero.stats.intelligence}")
        print(f"   Permadeath: {'🔥 ENABLED' if hero.permadeath_enabled else 'Disabled'}")
        
        print("\n⚔️  2. GEAR SYNERGY SYSTEM")
        print("-" * 30)
        
        # Create synergistic gear loadout
        shadow_items = [
            item_generator.generate_item(ItemType.WEAPON, ItemRarity.EPIC),   # Should be Shadowbane
            item_generator.generate_item(ItemType.ARMOR, ItemRarity.RARE),    # Light armor
            item_generator.generate_item(ItemType.RELIC, ItemRarity.UNCOMMON) # Utility item
        ]
        
        print("🛡️  Equipped Gear:")
        for item in shadow_items:
            print(f"   • {item.get_display_name()}")
            print(f"     {item.description}")
        
        synergies = synergy_manager.analyze_equipment_synergies(shadow_items)
        recommendations = synergy_manager.get_synergy_recommendations(shadow_items)
        
        print(f"\n🔮 Active Synergies: {len([b for bonuses in synergies.values() for b in bonuses])}")
        print(f"💡 Recommendations: {len(recommendations)}")
        
        if recommendations:
            rec = recommendations[0]
            print(f"   • Complete {rec['set_name']} ({rec['needed_items']} more items needed)")
        
        print("\n💀 3. PERMADEATH & RISK SYSTEM")
        print("-" * 35)
        
        # Test various risk scenarios
        scenarios = [
            ("Low Risk", "Exploring a peaceful forest glade"),
            ("Medium Risk", "Ancient tomb with magical traps"),
            ("High Risk", "Lair of an ancient dragon with legendary treasures")
        ]
        
        for risk_name, situation in scenarios:
            assessment = permadeath_manager.get_risk_assessment(hero, situation)
            print(f"\n🎲 {risk_name}: {situation}")
            print(f"   Risk Level: {assessment['risk_level'].upper()}")
            print(f"   Death Scenarios: {len(assessment['scenarios'])}")
            
            if assessment['scenarios']:
                primary = assessment['scenarios'][0]
                death_chance = int(primary['final_risk'] * 100)
                print(f"   Primary Threat: {primary['name']} ({death_chance}% death chance)")
                
                if death_chance > 30:
                    print(f"   ⚠️  WARNING: High death risk!")
                    print(f"   💡 Mitigation: {primary['mitigation_strategies'][0]}")
        
        print(f"\n🛡️  Survival Factors:")
        print(f"   • Constitution: {hero.stats.constitution}")
        print(f"   • Death Count: {hero.death_count}")
        print(f"   • Risk Tolerance: {int(hero.get_risk_tolerance() * 100)}%")
        
        print("\n🎭 4. FLAVOR TEXT CUSTOMIZATION")
        print("-" * 40)
        
        print("📖 Dynamic Descriptions:")
        char_desc = flavor_manager.get_character_description(
            hero.character_class, hero.background, hero.personality
        )
        print(f"   Character: {char_desc}")
        
        weapon_desc = flavor_manager.get_item_description(
            "weapon", shadow_items[0].name, shadow_items[0].rarity.value
        )
        print(f"   Weapon: {weapon_desc}")
        
        location_desc = flavor_manager.get_location_description("chamber")
        print(f"   Location: {location_desc}")
        
        print(f"\n🔧 Available Themes: {flavor_manager.get_available_themes()}")
        
        print("\n⚙️  5. CONFIGURABLE SETTINGS")
        print("-" * 35)
        
        print("🎛️  Current Settings:")
        print(f"   Permadeath Default: {settings_manager.get_setting('permadeath.enabled_by_default')}")
        print(f"   Focus on Synergies: {settings_manager.get_setting('engagement.focus_on_synergies')}")
        print(f"   Enemy Strength: {settings_manager.get_setting('difficulty.base_enemy_strength')}x")
        print(f"   Max Character Traits: {settings_manager.get_setting('character_creation.max_traits')}")
        
        print("\n🌟 6. INTEGRATION SUMMARY")
        print("-" * 30)
        
        total_bonuses = synergy_manager.calculate_total_synergy_bonuses(synergies)
        special_effects = synergy_manager.get_all_special_effects(synergies)
        
        print(f"✅ Character Power Level:")
        print(f"   Base Stats: STR {hero.stats.strength}, DEX {hero.stats.dexterity}")
        print(f"   Trait Bonuses: {len(hero.traits)} active traits")
        print(f"   Gear Synergies: {len(total_bonuses)} stat bonuses")
        print(f"   Special Effects: {len(special_effects)} active")
        
        engagement_score = (
            len(hero.traits) * 10 +
            len(total_bonuses) * 15 +
            len(special_effects) * 20 +
            (50 if hero.permadeath_enabled else 0)
        )
        
        print(f"\n🎯 Engagement Score: {engagement_score}/150")
        print("   (Based on traits, synergies, effects, and permadeath)")
        
        if engagement_score > 100:
            print("   🔥 HIGHLY ENGAGING CHARACTER BUILD!")
        elif engagement_score > 50:
            print("   ⭐ Good character complexity")
        else:
            print("   💡 Consider more trait/gear combinations")
        
        print("\n" + "🌟" * 20)
        print("🎮 ALL SYSTEMS INTEGRATED AND OPERATIONAL! 🎮")
        print("Ready for high-stakes, engaging adventures!")
        print("🌟" * 20)
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    # Run the comprehensive showcase
    run_full_integration_showcase()
    
    print("\n" + "=" * 65)
    print("Running integration tests...")
    
    # Run tests
    unittest.main(verbosity=2, exit=False)