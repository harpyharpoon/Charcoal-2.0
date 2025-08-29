#!/usr/bin/env python3
"""
Charcoal 2.0 Enhanced Features Demo
Showcases all new character customization and gear synergy systems
"""

import random
import tempfile
import shutil
from character import CharacterManager
from gear_synergy import GearSynergyManager  
from permadeath_system import PermadeathManager
from flavor_config import FlavorTextManager, ConfigurableGameSettings
from items import ItemGenerator, Item, ItemType, ItemRarity, ItemStats


def demo_character_customization():
    """Demo the enhanced character creation system"""
    print("🎯 ENHANCED CHARACTER CUSTOMIZATION DEMO")
    print("=" * 50)
    
    char_manager = CharacterManager()
    
    # Show available options
    print("\n📋 Available Customization Options:")
    options = char_manager.get_character_customization_options("Warrior")
    print(f"   Classes: {len(options['classes'])}")
    print(f"   Backgrounds: {len(options['backgrounds'])}")
    print(f"   Personalities: {len(options['personalities'])}")
    print(f"   Traits: {len(options['traits']['all'])}")
    
    # Show trait categories
    print("\n🏷️  Trait Categories:")
    for category, traits in options['traits']['by_category'].items():
        print(f"   {category.title()}: {traits[:2]}...")  # Show first 2 traits
    
    # Create an enhanced character
    print("\n👤 Creating Enhanced Character...")
    character = char_manager.create_custom_character(
        name="Thorin Ironforge",
        character_class="Warrior", 
        background="Soldier",
        personality="brave",
        selected_traits=["Battle Hardened", "Weapon Master", "Natural Leader"],
        starting_gear_choice="Guardian's Arsenal",
        permadeath_enabled=True
    )
    
    print(f"✨ Character Created: {character.name}")
    print(f"   Class: {character.character_class}")
    print(f"   Background: {character.background}")
    print(f"   Personality: {character.personality}")
    print(f"   Traits: {', '.join(character.traits)}")
    print(f"   Permadeath: {'🔥 ENABLED' if character.permadeath_enabled else 'Disabled'}")
    print(f"   Stats: STR {character.stats.strength}, DEX {character.stats.dexterity}, INT {character.stats.intelligence}")
    
    # Show trait effects
    effects = character.apply_trait_effects(char_manager.trait_manager)
    if effects:
        print(f"   Trait Bonuses: {effects}")
    
    return character


def demo_gear_synergies():
    """Demo the gear synergy system"""
    print("\n\n⚔️  GEAR SYNERGY SYSTEM DEMO")
    print("=" * 40)
    
    synergy_manager = GearSynergyManager()
    item_generator = ItemGenerator()
    
    # Show available item sets
    print("\n🛡️  Available Item Sets:")
    for set_name, item_set in synergy_manager.item_sets.items():
        print(f"   {item_set.name}")
        print(f"     Theme: {item_set.theme.title()}")
        print(f"     Items: {len(item_set.items)}")
        print(f"     Bonus Tiers: {len(item_set.bonuses)}")
    
    # Demo Flameguard set
    print(f"\n🔥 Flameguard Arsenal Demo:")
    flameguard_items = [
        Item("Flameforge Hammer", "A massive hammer that burns with eternal flame", 
             ItemType.WEAPON, ItemRarity.RARE, ItemStats(attack=8)),
        Item("Dragon Scale Mail", "Armor crafted from ancient dragon scales",
             ItemType.ARMOR, ItemRarity.EPIC, ItemStats(defense=12)),
        # Missing third item to show progression
    ]
    
    print(f"   Equipped Items:")
    for item in flameguard_items:
        print(f"     • {item.get_display_name()}")
    
    # Analyze synergies
    synergies = synergy_manager.analyze_equipment_synergies(flameguard_items)
    recommendations = synergy_manager.get_synergy_recommendations(flameguard_items)
    
    print(f"\n🔮 Synergy Analysis:")
    if synergies["set_bonuses"]:
        for bonus in synergies["set_bonuses"]:
            print(f"   ✨ {bonus.name}: {bonus.description}")
            for stat, value in bonus.stat_bonuses.items():
                print(f"      +{value} {stat.replace('_', ' ').title()}")
    
    if recommendations:
        rec = recommendations[0]
        print(f"\n💡 Recommendation:")
        print(f"   Complete {rec['set_name']}")
        print(f"   Need {rec['needed_items']} more items")
        print(f"   Try: {rec['recommended_items'][:2]}")
    
    return flameguard_items


def demo_permadeath_system(character):
    """Demo the permadeath and risk system"""
    print("\n\n💀 PERMADEATH & RISK SYSTEM DEMO")
    print("=" * 45)
    
    permadeath_manager = PermadeathManager()
    
    # Test various scenarios
    test_scenarios = [
        ("Safe Exploration", "Walking through a peaceful meadow"),
        ("Moderate Danger", "Ancient tomb with hidden traps and guardians"),
        ("High Risk", "Lair of an ancient red dragon guarding legendary treasure"),
        ("Extreme Peril", "Facing an overwhelming horde of demons in cursed lands")
    ]
    
    print(f"\n🎲 Risk Assessment for {character.name}:")
    print(f"   Constitution: {character.stats.constitution}")
    print(f"   Survival Traits: {[t for t in character.traits if 'death' in t.lower() or 'battle' in t.lower()]}")
    print(f"   Risk Tolerance: {int(character.get_risk_tolerance() * 100)}%")
    
    for scenario_name, description in test_scenarios:
        assessment = permadeath_manager.get_risk_assessment(character, description)
        
        print(f"\n📍 {scenario_name}:")
        print(f"   Scenario: {description}")
        print(f"   Risk Level: {assessment['risk_level'].upper()}")
        
        if assessment['scenarios']:
            primary = assessment['scenarios'][0]
            death_chance = int(primary['final_risk'] * 100)
            print(f"   Death Chance: {death_chance}%")
            print(f"   Primary Threat: {primary['name']}")
            
            if death_chance > 25:
                print(f"   ⚠️  WARNING: Significant death risk!")
                if primary['mitigation_strategies']:
                    print(f"   💡 Strategy: {primary['mitigation_strategies'][0]}")
    
    # Demo death scenario (simulation)
    print(f"\n🎭 Death Scenario Simulation:")
    high_risk_scenario = permadeath_manager.death_scenarios["boss_encounter"]
    died, final_risk = permadeath_manager.roll_for_death(character, high_risk_scenario)
    
    print(f"   Scenario: {high_risk_scenario.name}")
    print(f"   Final Risk: {int(final_risk * 100)}%")
    print(f"   Outcome: {'💀 DEATH' if died else '✅ SURVIVED'}")
    
    if died:
        # Simulate death handling
        death_event = permadeath_manager.handle_character_death(
            character, high_risk_scenario, final_risk, 
            "Dragon's Lair", ["Ally1", "Ally2"]
        )
        print(f"   Death recorded: {death_event.timestamp}")
        
        # Check resurrection
        can_res, cost, reason = permadeath_manager.can_resurrect(character.name)
        if can_res:
            print(f"   Resurrection Cost: {cost} gold")
        else:
            print(f"   Resurrection: {reason}")


def demo_flavor_system():
    """Demo the flavor text and configuration system"""
    print("\n\n🎭 FLAVOR TEXT & CONFIGURATION DEMO")
    print("=" * 50)
    
    test_dir = tempfile.mkdtemp()
    
    try:
        flavor_manager = FlavorTextManager(config_directory=test_dir)
        settings_manager = ConfigurableGameSettings(
            config_file=f"{test_dir}/demo_settings.json"
        )
        
        print(f"\n📚 Flavor Text Examples:")
        
        # Character descriptions
        warrior_desc = flavor_manager.get_character_description("Warrior", "Soldier", "brave")
        mage_desc = flavor_manager.get_character_description("Mage", "Sage", "wise")
        rogue_desc = flavor_manager.get_character_description("Rogue", "Criminal", "mischievous")
        
        print(f"   Brave Warrior: {warrior_desc}")
        print(f"   Wise Mage: {mage_desc}")
        print(f"   Mischievous Rogue: {rogue_desc}")
        
        # Item descriptions
        print(f"\n🗡️  Item Descriptions:")
        common_weapon = flavor_manager.get_item_description("weapon", "Iron Sword", "common")
        legendary_armor = flavor_manager.get_item_description("armor", "Dragon Mail", "legendary")
        
        print(f"   Common Weapon: {common_weapon}")
        print(f"   Legendary Armor: {legendary_armor}")
        
        # Location descriptions
        print(f"\n🏛️  Location Descriptions:")
        chamber_desc = flavor_manager.get_location_description("chamber")
        treasure_desc = flavor_manager.get_location_description("treasure_room")
        
        print(f"   Chamber: {chamber_desc}")
        print(f"   Treasure Room: {treasure_desc}")
        
        # Configuration demo
        print(f"\n⚙️  Configuration Settings:")
        print(f"   Current Theme: {flavor_manager.current_theme}")
        print(f"   Available Themes: {flavor_manager.get_available_themes()}")
        
        # Game settings
        print(f"\n🎛️  Game Settings:")
        print(f"   Permadeath Default: {settings_manager.get_setting('permadeath.enabled_by_default')}")
        print(f"   Focus on Synergies: {settings_manager.get_setting('engagement.focus_on_synergies')}")
        print(f"   Enemy Strength: {settings_manager.get_setting('difficulty.base_enemy_strength')}x")
        
        # Modify settings demo
        settings_manager.set_setting("difficulty.base_enemy_strength", 1.5)
        settings_manager.set_setting("permadeath.enabled_by_default", True)
        
        print(f"\n🔧 Modified Settings:")
        print(f"   Enemy Strength: {settings_manager.get_setting('difficulty.base_enemy_strength')}x")
        print(f"   Permadeath Default: {settings_manager.get_setting('permadeath.enabled_by_default')}")
        
    finally:
        shutil.rmtree(test_dir)


def demo_complete_adventure():
    """Demo a complete adventure using all systems"""
    print("\n\n🌟 COMPLETE ADVENTURE DEMO")
    print("=" * 35)
    
    char_manager = CharacterManager()
    synergy_manager = GearSynergyManager()
    permadeath_manager = PermadeathManager()
    
    # Create party of diverse characters
    print(f"\n🏰 Assembling Adventure Party:")
    
    party = []
    
    # Tank
    tank = char_manager.create_character(
        "Sir Gareth", "Paladin",
        traits=["Battle Hardened", "Natural Leader"],
        permadeath_enabled=True
    )
    party.append(tank)
    print(f"   🛡️  Tank: {tank.name} ({tank.character_class})")
    
    # DPS
    dps = char_manager.create_character(
        "Zara Swiftblade", "Rogue", 
        traits=["Weapon Master", "Lucky"],
        permadeath_enabled=True
    )
    party.append(dps)
    print(f"   ⚔️  DPS: {dps.name} ({dps.character_class})")
    
    # Support
    support = char_manager.create_character(
        "Lyra Starweaver", "Mage",
        traits=["Arcane Scholar", "Mana Touched"],
        permadeath_enabled=True
    )
    party.append(support)
    print(f"   ✨ Support: {support.name} ({support.character_class})")
    
    # Adventure scenario
    adventure_scenario = "The party enters the Shadowspire Tower, a legendary dungeon filled with ancient traps, cursed guardians, and a powerful lich lord at the top. Rumors speak of the Orb of Infinite Wisdom hidden in the highest chamber."
    
    print(f"\n📖 Adventure Scenario:")
    print(f"   {adventure_scenario}")
    
    # Assess risks for each party member
    print(f"\n💀 Risk Assessment:")
    total_risk = 0
    for member in party:
        assessment = permadeath_manager.get_risk_assessment(member, adventure_scenario)
        risk_level = assessment['risk_level']
        
        if assessment['scenarios']:
            death_chance = int(assessment['scenarios'][0]['final_risk'] * 100)
            total_risk += death_chance
        else:
            death_chance = 0
        
        print(f"   {member.name}: {risk_level.upper()} ({death_chance}% death chance)")
    
    avg_risk = total_risk / len(party)
    print(f"\n📊 Party Survival Outlook:")
    print(f"   Average Death Risk: {avg_risk:.0f}%")
    
    if avg_risk > 40:
        print(f"   ⚠️  DANGEROUS MISSION - High casualty risk!")
        print(f"   💡 Recommendation: Better equipment and preparation needed")
    elif avg_risk > 20:
        print(f"   ⚡ CHALLENGING MISSION - Moderate risk")
        print(f"   💡 Recommendation: Proceed with caution")
    else:
        print(f"   ✅ MANAGEABLE MISSION - Low risk")
        print(f"   💡 Recommendation: Good chance of success")
    
    # Calculate engagement score
    total_traits = sum(len(member.traits) for member in party)
    permadeath_members = sum(1 for member in party if member.permadeath_enabled)
    
    engagement_score = (
        total_traits * 10 +
        permadeath_members * 30 +
        (20 if avg_risk > 20 else 10)  # Risk bonus
    )
    
    print(f"\n🎯 Adventure Engagement Score: {engagement_score}/150")
    print(f"   Factors: {total_traits} traits, {permadeath_members} permadeath characters, {avg_risk:.0f}% risk")
    
    if engagement_score > 100:
        print(f"   🔥 HIGHLY ENGAGING ADVENTURE!")
    elif engagement_score > 60:
        print(f"   ⭐ Good adventure setup")
    else:
        print(f"   💡 Consider adding more traits or enabling permadeath")


def main():
    """Run the complete demo"""
    print("🎮 CHARCOAL 2.0 ENHANCED FEATURES DEMO")
    print("🔥" * 40)
    print("Showcasing character customization, gear synergies,")
    print("permadeath mechanics, and configuration systems!")
    print("🔥" * 40)
    
    # Run all demos
    character = demo_character_customization()
    items = demo_gear_synergies()
    demo_permadeath_system(character)
    demo_flavor_system()
    demo_complete_adventure()
    
    print("\n\n🌟" * 20)
    print("🎯 DEMO COMPLETE!")
    print("✨ All enhanced systems demonstrated!")
    print("🎮 Ready for engaging, high-stakes adventures!")
    print("🌟" * 20)


if __name__ == "__main__":
    main()