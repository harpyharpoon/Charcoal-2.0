#!/usr/bin/env python3
"""
Charcoal 2.0 - Text-based MMORPG with AI Characters
A living MMO-style simulation where AI characters roam, interact, and evolve.
"""

import sys
import os
from spectator import SpectatorInterface
from character import CharacterManager
from world import WorldManager
from party import PartyManager


def main():
    """Main entry point for Charcoal 2.0"""
    
    print("🔥 Starting Charcoal 2.0...")
    
    try:
        # Check if we're in demo mode (no OpenAI key)
        if not os.getenv("OPENAI_API_KEY"):
            print("🎭 No OpenAI API key detected - running in demo mode with mock AI")
            print("💡 To use real AI, set OPENAI_API_KEY in your .env file")
            print()
        
        # Start the spectator interface
        interface = SpectatorInterface()
        interface.start()
        
    except KeyboardInterrupt:
        print("\n👋 Thanks for watching Charcoal 2.0!")
    except Exception as e:
        print(f"❌ Error starting Charcoal 2.0: {e}")
        sys.exit(1)


def demo_mode():
    """Run a quick demonstration of the system"""
    print("🎭 Charcoal 2.0 Demo Mode")
    print("=" * 40)
    
    # Initialize systems
    char_manager = CharacterManager()
    world_manager = WorldManager()
    party_manager = PartyManager(char_manager, world_manager)
    
    # Create a demo party
    print("\n🛡️ Creating demo party...")
    party = party_manager.create_random_party("Demo Heroes")
    
    print(f"✅ Created party: {party.name}")
    print(f"Members: {', '.join([char.name for char in party.characters])}")
    
    # Show current location
    dungeon = world_manager.get_current_dungeon()
    area = dungeon.get_current_area()
    print(f"\n🏰 Current location: {dungeon.name} - {area.name}")
    print(f"📖 {area.description}")
    
    # Run a few adventure steps
    print("\n⚡ Running adventure steps...")
    for i in range(3):
        print(f"\n--- Step {i+1} ---")
        result = party_manager.advance_party_adventure(party.name)
        if result["success"]:
            for event in result["events"]:
                if event["type"] == "dialogue":
                    print(f"💬 {event.get('character', 'Someone')}: {event['content']}")
                elif event["type"] == "narrative":
                    print(f"📖 {event['content']}")
                elif event["type"] == "movement":
                    print(f"🚶 {event['content']}")
                elif event["type"] == "discovery":
                    print(f"✨ {event['content']}")
                else:
                    print(f"📝 {event['content']}")
        else:
            print(f"❌ {result['reason']}")
            break
    
    print(f"\n📊 Final party status:")
    print(party.get_party_status())
    print("\n🎭 Demo complete! Run 'python main.py' for the full interactive experience.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        main()