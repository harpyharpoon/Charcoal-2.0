#!/usr/bin/env python3
"""
Charcoal 2.0 - Text-based MMORPG with AI Characters
A living MMO-style simulation where AI characters roam, interact, and evolve.
"""

import sys
import os
from colorama import init, Fore, Style
from spectator import SpectatorInterface
from pub_interface import PubInterface
from character import CharacterManager
from world import WorldManager
from party import PartyManager

# Initialize colorama
init()


def main():
    """Main entry point for Charcoal 2.0"""
    
    print("🔥 Starting Charcoal 2.0...")
    
    try:
        # Check if we're in demo mode (no OpenAI key)
        if not os.getenv("OPENAI_API_KEY"):
            print("🎭 No OpenAI API key detected - running in demo mode with mock AI")
            print("💡 To use real AI, set OPENAI_API_KEY in your .env file")
            print()
        
        # Show main menu
        show_main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Thanks for visiting Charcoal 2.0!")
    except Exception as e:
        print(f"❌ Error starting Charcoal 2.0: {e}")
        sys.exit(1)


def show_main_menu():
    """Show the main menu to choose between Pub and Spectator modes"""
    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.YELLOW}🔥 CHARCOAL 2.0 - MAIN MENU 🔥")
    print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Welcome to the world of AI-powered adventures!")
    print()
    print(f"{Fore.GREEN}Choose your experience:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. {Fore.RED}🍺 Enter The Pub{Style.RESET_ALL} - Create characters, check quests, and chat")
    print(f"{Fore.WHITE}2. {Fore.CYAN}👁️  Spectator Mode{Style.RESET_ALL} - Watch ongoing adventures")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}🎭 Demo Mode{Style.RESET_ALL} - Quick demonstration")
    print(f"{Fore.WHITE}4. {Fore.RED}❌ Exit{Style.RESET_ALL}")
    
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (1-4): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                print(f"{Fore.YELLOW}🍺 Welcome to The Pub!{Style.RESET_ALL}")
                interface = PubInterface()
                interface.start()
                break
            elif choice == "2":
                print(f"{Fore.CYAN}👁️  Starting Spectator Mode...{Style.RESET_ALL}")
                interface = SpectatorInterface()
                interface.start()
                break
            elif choice == "3":
                demo_mode()
                break
            elif choice == "4":
                print(f"{Fore.YELLOW}👋 Farewell, adventurer!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1, 2, 3, or 4.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Farewell, adventurer!{Style.RESET_ALL}")
            break


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