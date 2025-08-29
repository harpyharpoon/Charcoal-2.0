#!/usr/bin/env python3
"""
Test the permadeath and flavor configuration systems
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from character import CharacterManager, Character
from permadeath_system import PermadeathManager, DeathType, RiskLevel
from flavor_config import FlavorTextManager, ConfigurableGameSettings


class TestPermadeathSystem(unittest.TestCase):
    """Test the permadeath and risk system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.char_manager = CharacterManager()
        self.permadeath_manager = PermadeathManager()
    
    def test_death_scenario_creation(self):
        """Test that death scenarios are created correctly"""
        scenarios = self.permadeath_manager.death_scenarios
        
        self.assertGreater(len(scenarios), 0)
        self.assertIn("overwhelming_odds", scenarios)
        self.assertIn("boss_encounter", scenarios)
        
        # Test scenario structure
        boss_scenario = scenarios["boss_encounter"]
        self.assertEqual(boss_scenario.death_type, DeathType.COMBAT)
        self.assertGreater(len(boss_scenario.warning_signs), 0)
        self.assertGreater(len(boss_scenario.possible_rewards), 0)
    
    def test_risk_evaluation(self):
        """Test situation risk evaluation"""
        # Test high-risk situation
        high_risk_situation = "A massive dragon blocks your path, its legendary power evident"
        risk_level, scenarios = self.permadeath_manager.evaluate_situation_risk(high_risk_situation)
        
        self.assertIn(risk_level, [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.EXTREME])
        self.assertGreater(len(scenarios), 0)
        
        # Test low-risk situation
        low_risk_situation = "A peaceful meadow with flowers"
        risk_level, scenarios = self.permadeath_manager.evaluate_situation_risk(low_risk_situation)
        
        self.assertIn(risk_level, [RiskLevel.MINIMAL, RiskLevel.LOW])
    
    def test_death_calculation(self):
        """Test death chance calculations"""
        character = self.char_manager.create_character(
            name="TestHero",
            character_class="Warrior",
            traits=["Battle Hardened"]  # Should reduce death chance
        )
        
        scenario = self.permadeath_manager.death_scenarios["boss_encounter"]
        
        # Test multiple rolls to ensure randomness
        results = []
        for _ in range(10):
            died, final_risk = self.permadeath_manager.roll_for_death(character, scenario)
            results.append((died, final_risk))
        
        # Should have some variation in results
        risks = [risk for _, risk in results]
        self.assertIsInstance(risks[0], float)
        self.assertGreaterEqual(min(risks), 0.0)
        self.assertLessEqual(max(risks), 1.0)
    
    def test_resurrection_system(self):
        """Test character resurrection mechanics"""
        character = self.char_manager.create_character("TestHero", "Warrior")
        scenario = self.permadeath_manager.death_scenarios["boss_encounter"]
        
        # Simulate a death
        death_event = self.permadeath_manager.handle_character_death(
            character, scenario, 0.5, "Test Location", ["Ally1", "Ally2"]
        )
        
        self.assertEqual(death_event.character_name, character.name)
        self.assertEqual(character.death_count, 1)
        
        # Test resurrection possibility
        can_res, cost, reason = self.permadeath_manager.can_resurrect(character.name)
        self.assertTrue(can_res)
        self.assertGreater(cost, 0)
        
        # Test successful resurrection
        success = self.permadeath_manager.resurrect_character(character, cost)
        self.assertTrue(success)
    
    def test_risk_assessment(self):
        """Test comprehensive risk assessment"""
        character = self.char_manager.create_character("RiskTest", "Mage", permadeath_enabled=True)
        
        assessment = self.permadeath_manager.get_risk_assessment(
            character, "A powerful demon lord blocks your path"
        )
        
        self.assertIn("risk_level", assessment)
        self.assertIn("scenarios", assessment)
        self.assertIn("character_survival_factors", assessment)
        self.assertIn("recommendations", assessment)
        
        self.assertGreater(len(assessment["scenarios"]), 0)
    
    def test_death_statistics(self):
        """Test death statistics tracking"""
        # Initially no deaths
        stats = self.permadeath_manager.get_death_statistics()
        self.assertEqual(stats["total_deaths"], 0)
        
        # Simulate some deaths
        character = self.char_manager.create_character("StatTest", "Rogue")
        scenario = self.permadeath_manager.death_scenarios["deadly_trap"]
        
        self.permadeath_manager.handle_character_death(
            character, scenario, 0.3, "Dungeon Level 1", []
        )
        
        stats = self.permadeath_manager.get_death_statistics()
        self.assertEqual(stats["total_deaths"], 1)
        self.assertIn("trap", stats["deaths_by_type"])
    
    def test_memorial_creation(self):
        """Test memorial text generation"""
        character = self.char_manager.create_character("Memorial", "Paladin")
        scenario = self.permadeath_manager.death_scenarios["heroic_sacrifice"]
        
        self.permadeath_manager.handle_character_death(
            character, scenario, 0.9, "Final Battle", ["Hero1", "Hero2"]
        )
        
        memorial = self.permadeath_manager.create_memorial(character.name)
        
        self.assertIn(character.name, memorial)
        self.assertIn("Heroic Sacrifice", memorial)
        self.assertIn("IN MEMORIAM", memorial)


class TestFlavorSystem(unittest.TestCase):
    """Test the flavor text and configuration system"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.flavor_manager = FlavorTextManager(config_directory=self.test_dir)
        self.settings_manager = ConfigurableGameSettings(
            config_file=os.path.join(self.test_dir, "test_settings.json")
        )
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_flavor_text_generation(self):
        """Test that flavor text is generated correctly"""
        # Test character description
        desc = self.flavor_manager.get_character_description("Warrior", "Soldier", "brave")
        self.assertIsInstance(desc, str)
        self.assertGreater(len(desc), 10)
        
        # Test item description
        item_desc = self.flavor_manager.get_item_description("weapon", "Iron Sword", "common")
        self.assertIsInstance(item_desc, str)
        
        # Test location description
        loc_desc = self.flavor_manager.get_location_description("chamber")
        self.assertIsInstance(loc_desc, str)
    
    def test_theme_switching(self):
        """Test switching between flavor themes"""
        # Should start with default theme
        self.assertEqual(self.flavor_manager.current_theme, "default")
        
        # Test getting available themes
        themes = self.flavor_manager.get_available_themes()
        self.assertIn("default", themes)
        
        # Test theme export
        exported = self.flavor_manager.export_theme_template()
        self.assertIn("name", exported)
        self.assertIn("character_descriptions", exported)
    
    def test_game_settings_management(self):
        """Test game settings configuration"""
        # Test default settings
        permadeath_default = self.settings_manager.get_setting("permadeath.enabled_by_default")
        self.assertIsInstance(permadeath_default, bool)
        
        # Test setting modification
        self.settings_manager.set_setting("permadeath.enabled_by_default", True)
        new_value = self.settings_manager.get_setting("permadeath.enabled_by_default")
        self.assertTrue(new_value)
        
        # Test nested settings
        self.settings_manager.set_setting("difficulty.base_enemy_strength", 1.5)
        strength = self.settings_manager.get_setting("difficulty.base_enemy_strength")
        self.assertEqual(strength, 1.5)
    
    def test_settings_persistence(self):
        """Test that settings are saved and loaded correctly"""
        # Modify a setting
        self.settings_manager.set_setting("engagement.focus_on_synergies", False)
        
        # Create new settings manager with same file
        new_manager = ConfigurableGameSettings(
            config_file=os.path.join(self.test_dir, "test_settings.json")
        )
        
        # Should load the modified setting
        focus_synergies = new_manager.get_setting("engagement.focus_on_synergies")
        self.assertFalse(focus_synergies)
    
    def test_settings_export_import(self):
        """Test settings export and import functionality"""
        # Modify some settings
        self.settings_manager.set_setting("permadeath.enabled_by_default", True)
        self.settings_manager.set_setting("difficulty.base_enemy_strength", 2.0)
        
        # Export settings
        exported = self.settings_manager.export_settings()
        self.assertIn("permadeath", exported)
        self.assertIn("difficulty", exported)
        
        # Reset and import
        self.settings_manager.reset_to_defaults()
        self.settings_manager.import_settings(exported)
        
        # Should have imported values
        self.assertTrue(self.settings_manager.get_setting("permadeath.enabled_by_default"))
        self.assertEqual(self.settings_manager.get_setting("difficulty.base_enemy_strength"), 2.0)


def run_permadeath_showcase():
    """Run a showcase of the permadeath system"""
    print("\n💀 Permadeath & Risk System Showcase")
    print("=" * 45)
    
    char_manager = CharacterManager()
    permadeath_manager = PermadeathManager()
    
    # Create a character
    character = char_manager.create_character(
        name="Daredevil",
        character_class="Rogue",
        personality="hot-headed",
        traits=["Death Defiant", "Lucky"],
        permadeath_enabled=True
    )
    
    print(f"\n👤 Character: {character.name}")
    print(f"   Class: {character.character_class}")
    print(f"   Death Count: {character.death_count}")
    print(f"   Risk Tolerance: {character.get_risk_tolerance():.2f}")
    
    # Test various scenarios
    scenarios = [
        "A massive dragon guards an ancient treasure",
        "You hear clicking sounds - traps ahead",
        "Overwhelming horde of goblins surrounds you"
    ]
    
    print("\n🎲 Risk Assessments:")
    for i, situation in enumerate(scenarios, 1):
        print(f"\n  Scenario {i}: {situation}")
        assessment = permadeath_manager.get_risk_assessment(character, situation)
        print(f"    Risk Level: {assessment['risk_level'].upper()}")
        print(f"    Scenarios: {len(assessment['scenarios'])}")
        if assessment['scenarios']:
            primary = assessment['scenarios'][0]
            print(f"    Primary Risk: {primary['name']} ({int(primary['final_risk'] * 100)}% death chance)")
    
    # Show available scenarios
    print(f"\n💀 Available Death Scenarios: {len(permadeath_manager.death_scenarios)}")
    for name, scenario in list(permadeath_manager.death_scenarios.items())[:3]:
        print(f"   • {scenario.name} ({scenario.death_type.value})")
        print(f"     Base Risk: {int(scenario.base_risk * 100)}%")
    
    print("\n✅ Permadeath system ready for high-stakes adventure!")


def run_flavor_showcase():
    """Run a showcase of the flavor system"""
    print("\n🎭 Flavor Text & Configuration Showcase")
    print("=" * 45)
    
    import tempfile
    test_dir = tempfile.mkdtemp()
    
    try:
        flavor_manager = FlavorTextManager(config_directory=test_dir)
        settings_manager = ConfigurableGameSettings(
            config_file=os.path.join(test_dir, "showcase_settings.json")
        )
        
        print(f"\n📚 Available Themes: {flavor_manager.get_available_themes()}")
        print(f"   Current Theme: {flavor_manager.current_theme}")
        
        # Show flavor text examples
        print("\n📝 Flavor Text Examples:")
        print("   Character Descriptions:")
        char_desc = flavor_manager.get_character_description("Warrior", "Soldier", "brave")
        print(f"     • Brave Warrior: {char_desc}")
        
        print("\n   Item Descriptions:")
        item_desc = flavor_manager.get_item_description("weapon", "Legendary Sword", "legendary")
        print(f"     • Legendary Weapon: {item_desc}")
        
        print("\n   Location Descriptions:")
        loc_desc = flavor_manager.get_location_description("treasure_room")
        print(f"     • Treasure Room: {loc_desc}")
        
        # Show settings
        print("\n⚙️  Game Settings:")
        focus_synergies = settings_manager.get_setting("engagement.focus_on_synergies")
        permadeath_default = settings_manager.get_setting("permadeath.enabled_by_default")
        enemy_strength = settings_manager.get_setting("difficulty.base_enemy_strength")
        
        print(f"   Focus on Synergies: {focus_synergies}")
        print(f"   Permadeath Default: {permadeath_default}")
        print(f"   Enemy Strength: {enemy_strength}x")
        
        print("\n✅ Configuration system ready for easy customization!")
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    # Run showcases first
    run_permadeath_showcase()
    run_flavor_showcase()
    
    print("\n" + "=" * 65)
    print("Running comprehensive tests...")
    
    # Run tests
    unittest.main(verbosity=2, exit=False)