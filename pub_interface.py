import time
import random
from typing import Dict, List, Optional
from colorama import init, Fore, Back, Style
from character import CharacterManager, Character
from world import WorldManager
from party import PartyManager, Party
from ai_dialogue import AIDialogueSystem
import config

# Initialize colorama for cross-platform colored output
init()


class PubInterface:
    """Interactive interface for 'The Pub' - character creation, quest board, and chat"""
    
    def __init__(self):
        self.character_manager = CharacterManager()
        self.world_manager = WorldManager()
        self.party_manager = PartyManager(self.character_manager, self.world_manager)
        self.ai_dialogue = AIDialogueSystem()
        self.running = False
        self.current_user_character = None
        
    def start(self):
        """Start The Pub interface"""
        self.running = True
        self._print_welcome()
        self._main_menu()
    
    def stop(self):
        """Stop The Pub interface"""
        self.running = False
    
    def _clear_screen(self):
        """Clear the screen (basic implementation)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_welcome(self):
        """Print welcome message to The Pub"""
        self._clear_screen()
        
        print(f"{Fore.YELLOW}{'═' * 80}")
        print(f"{Fore.RED}🍺 WELCOME TO THE PUB 🍺")
        print(f"{Fore.YELLOW}{'═' * 80}")
        print(f"{Fore.WHITE}")
        print("Greetings, adventurer! Welcome to The Pub, the heart of our community.")
        print("Here you can create your character, check the quest board, and chat")
        print("with fellow adventurers before embarking on your next adventure!")
        print()
        print(f"{Fore.CYAN}🔥 The tavern fire crackles warmly...")
        print(f"{Fore.LIGHTBLACK_EX}🍺 Patrons chat quietly over their ales...")
        print(f"{Fore.YELLOW}📜 The quest board is covered with notices...")
        print(f"{Style.RESET_ALL}")
    
    def _main_menu(self):
        """Main menu loop for The Pub"""
        while self.running:
            try:
                print(f"\n{Fore.GREEN}═══ THE PUB MENU ═══{Style.RESET_ALL}")
                print(f"{Fore.WHITE}1. {Fore.CYAN}Create Character{Style.RESET_ALL}")
                print(f"{Fore.WHITE}2. {Fore.YELLOW}View Quest Board{Style.RESET_ALL}")
                print(f"{Fore.WHITE}3. {Fore.MAGENTA}Chat with Patrons{Style.RESET_ALL}")
                print(f"{Fore.WHITE}4. {Fore.LIGHTBLUE_EX}View Characters in Pub{Style.RESET_ALL}")
                print(f"{Fore.WHITE}5. {Fore.GREEN}Switch to Spectator Mode{Style.RESET_ALL}")
                print(f"{Fore.WHITE}6. {Fore.RED}Leave The Pub{Style.RESET_ALL}")
                
                choice = input(f"\n{Fore.CYAN}What would you like to do? {Style.RESET_ALL}").strip()
                
                if choice == "1":
                    self._character_creation_menu()
                elif choice == "2":
                    self._quest_board()
                elif choice == "3":
                    self._chat_with_patrons()
                elif choice == "4":
                    self._view_characters()
                elif choice == "5":
                    self._switch_to_spectator()
                    break
                elif choice == "6":
                    print(f"\n{Fore.YELLOW}🍺 Safe travels, adventurer! The Pub will always welcome you back.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}🍺 Farewell, adventurer!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    def _character_creation_menu(self):
        """Interactive character creation"""
        print(f"\n{Fore.CYAN}{'═' * 50}")
        print(f"{Fore.YELLOW}⚔️ CHARACTER CREATION ⚔️")
        print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}The barkeep looks up from polishing a mug...")
        print(f'"{Fore.YELLOW}Ah, a new face! What shall I call you, friend?{Fore.WHITE}"{Style.RESET_ALL}')
        
        # Get character name
        while True:
            name = input(f"\n{Fore.CYAN}Enter your character's name: {Style.RESET_ALL}").strip()
            if name:
                # Check if name already exists
                if self.character_manager.get_character(name):
                    print(f"{Fore.RED}❌ A character with that name already exists in The Pub!{Style.RESET_ALL}")
                    continue
                break
            else:
                print(f"{Fore.RED}❌ Please enter a valid name.{Style.RESET_ALL}")
        
        # Choose character class
        print(f"\n{Fore.WHITE}The barkeep nods approvingly...")
        print(f'"{Fore.YELLOW}{name}! What\'s your calling in life?{Fore.WHITE}"{Style.RESET_ALL}')
        print(f"\n{Fore.GREEN}Available Classes:{Style.RESET_ALL}")
        
        for i, char_class in enumerate(config.CHARACTER_CLASSES, 1):
            print(f"{Fore.WHITE}{i}. {Fore.CYAN}{char_class}{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Choose your class (1-{len(config.CHARACTER_CLASSES)}): {Style.RESET_ALL}").strip()
                class_idx = int(choice) - 1
                if 0 <= class_idx < len(config.CHARACTER_CLASSES):
                    character_class = config.CHARACTER_CLASSES[class_idx]
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please choose 1-{len(config.CHARACTER_CLASSES)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a number.{Style.RESET_ALL}")
        
        # Choose background
        print(f"\n{Fore.WHITE}The barkeep strokes their beard thoughtfully...")
        print(f'"{Fore.YELLOW}And what\'s your story? Where do you come from?{Fore.WHITE}"{Style.RESET_ALL}')
        print(f"\n{Fore.GREEN}Available Backgrounds:{Style.RESET_ALL}")
        
        for i, background in enumerate(config.CHARACTER_BACKGROUNDS, 1):
            print(f"{Fore.WHITE}{i}. {Fore.CYAN}{background}{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Choose your background (1-{len(config.CHARACTER_BACKGROUNDS)}): {Style.RESET_ALL}").strip()
                bg_idx = int(choice) - 1
                if 0 <= bg_idx < len(config.CHARACTER_BACKGROUNDS):
                    background = config.CHARACTER_BACKGROUNDS[bg_idx]
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please choose 1-{len(config.CHARACTER_BACKGROUNDS)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a number.{Style.RESET_ALL}")
        
        # Choose personality
        personalities = ["brave", "cautious", "curious", "hot-headed", "wise", "mischievous",
                        "loyal", "independent", "cheerful", "serious", "witty", "stoic"]
        
        print(f"\n{Fore.WHITE}The barkeep leans in closer...")
        print(f'"{Fore.YELLOW}And what kind of person are you, {name}?{Fore.WHITE}"{Style.RESET_ALL}')
        print(f"\n{Fore.GREEN}Personality Traits:{Style.RESET_ALL}")
        
        for i, personality in enumerate(personalities, 1):
            print(f"{Fore.WHITE}{i}. {Fore.CYAN}{personality.title()}{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Choose your personality (1-{len(personalities)}): {Style.RESET_ALL}").strip()
                pers_idx = int(choice) - 1
                if 0 <= pers_idx < len(personalities):
                    personality = personalities[pers_idx]
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please choose 1-{len(personalities)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a number.{Style.RESET_ALL}")
        
        # Create the character
        character = self.character_manager.create_character(name, character_class, background, personality)
        self.current_user_character = character
        
        # Success message
        print(f"\n{Fore.GREEN}✅ Character created successfully!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{'═' * 50}")
        print(f"{Fore.YELLOW}📋 CHARACTER SHEET 📋")
        print(f"{Fore.CYAN}{'═' * 50}")
        print(f"{Fore.WHITE}Name: {Fore.YELLOW}{character.name}")
        print(f"{Fore.WHITE}Class: {Fore.CYAN}{character.character_class}")
        print(f"{Fore.WHITE}Background: {Fore.MAGENTA}{character.background}")
        print(f"{Fore.WHITE}Personality: {Fore.GREEN}{character.personality.title()}")
        print(f"{Fore.WHITE}Description: {Fore.LIGHTBLACK_EX}{character.description}")
        print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
        
        print(f"\n{Fore.WHITE}The barkeep smiles warmly...")
        print(f'"{Fore.YELLOW}Welcome to The Pub, {name}! Your tale begins here.{Fore.WHITE}"{Style.RESET_ALL}')
        
        input(f"\n{Fore.LIGHTBLACK_EX}Press Enter to continue...{Style.RESET_ALL}")
    
    def _quest_board(self):
        """Display the quest board with available adventures"""
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.YELLOW}📜 THE QUEST BOARD 📜")
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}You approach the quest board, covered with notices and adventures...")
        print()
        
        # Show active parties
        parties = self.party_manager.list_parties()
        if parties:
            print(f"{Fore.GREEN}🎭 Active Adventuring Parties:{Style.RESET_ALL}")
            for i, party_name in enumerate(parties, 1):
                party = self.party_manager.get_party(party_name)
                alive_count = sum(1 for hp in party.current_hp.values() if hp > 0)
                status_color = Fore.GREEN if alive_count == len(party.characters) else Fore.YELLOW if alive_count > 0 else Fore.RED
                print(f"{Fore.WHITE}{i}. {status_color}{party_name}{Style.RESET_ALL}")
                print(f"   {Fore.LIGHTBLACK_EX}Members: {', '.join([char.name for char in party.characters])}")
                print(f"   Status: {status_color}{alive_count}/{len(party.characters)} alive{Style.RESET_ALL}")
                print(f"   Experience: {Fore.CYAN}{party.experience} XP{Style.RESET_ALL}")
                print()
        else:
            print(f"{Fore.YELLOW}📝 No active parties found.{Style.RESET_ALL}")
        
        # Show available characters for new parties
        available_chars = [char for char in self.character_manager.list_characters() 
                          if not any(char in party.characters for party in 
                                   [self.party_manager.get_party(name) for name in parties])]
        
        if available_chars:
            print(f"{Fore.GREEN}🛡️ Available Characters for New Adventures:{Style.RESET_ALL}")
            for char in available_chars:
                print(f"   {Fore.CYAN}{char.name}{Style.RESET_ALL} - {Fore.WHITE}{char.character_class} ({char.personality}){Style.RESET_ALL}")
        
        # Show dungeons
        print(f"\n{Fore.GREEN}🏰 Available Adventure Locations:{Style.RESET_ALL}")
        dungeons = self.world_manager.list_dungeons()
        current = self.world_manager.current_dungeon
        for dungeon_name in dungeons:
            dungeon = self.world_manager.dungeons[dungeon_name]
            marker = "📍" if dungeon_name == current else "🏰"
            print(f"   {marker} {Fore.YELLOW}{dungeon.name}{Style.RESET_ALL} - {Fore.LIGHTBLACK_EX}{dungeon.theme}{Style.RESET_ALL}")
        
        print(f"\n{Fore.LIGHTBLACK_EX}💡 Tip: Create a party using 'Create Character' or watch existing parties in Spectator Mode!{Style.RESET_ALL}")
        input(f"\n{Fore.LIGHTBLACK_EX}Press Enter to return to menu...{Style.RESET_ALL}")
    
    def _chat_with_patrons(self):
        """Chat interface with AI-powered pub patrons"""
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.YELLOW}💬 CHAT WITH PATRONS 💬")
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}You look around The Pub and see several patrons you could talk to...")
        print()
        
        # Get some characters to chat with (excluding user's character if they have one)
        all_chars = self.character_manager.list_characters()
        chat_chars = [char for char in all_chars if char != self.current_user_character]
        
        if not chat_chars:
            print(f"{Fore.YELLOW}🤷 The Pub is quiet tonight. No one to chat with.{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}Create some characters first!{Style.RESET_ALL}")
            input(f"\n{Fore.LIGHTBLACK_EX}Press Enter to return to menu...{Style.RESET_ALL}")
            return
        
        # Show available characters to chat with
        print(f"{Fore.GREEN}Available Patrons:{Style.RESET_ALL}")
        for i, char in enumerate(chat_chars[:5], 1):  # Show max 5 characters
            print(f"{Fore.WHITE}{i}. {Fore.CYAN}{char.name}{Style.RESET_ALL} - {Fore.LIGHTBLACK_EX}{char.character_class}, sitting by the {random.choice(['fire', 'bar', 'window', 'corner table'])}{Style.RESET_ALL}")
        
        print(f"{Fore.WHITE}6. {Fore.RED}Return to menu{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Who would you like to chat with? {Style.RESET_ALL}").strip()
                if choice == "6":
                    return
                
                chat_idx = int(choice) - 1
                if 0 <= chat_idx < len(chat_chars[:5]):
                    selected_char = chat_chars[chat_idx]
                    self._start_conversation(selected_char)
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a number.{Style.RESET_ALL}")
    
    def _start_conversation(self, character: Character):
        """Start a conversation with a character"""
        print(f"\n{Fore.CYAN}{'─' * 50}")
        print(f"{Fore.YELLOW}💬 Chatting with {character.name}")
        print(f"{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}You approach {character.name}, who looks up from their drink...")
        print()
        
        # Generate initial greeting
        greeting_context = f"You are in a cozy pub called 'The Pub'. A patron approaches you for conversation."
        greeting = self.ai_dialogue.generate_character_response(
            character, greeting_context, "greeting", []
        )
        print(f"{Fore.CYAN}{character.name}: {Fore.WHITE}{greeting}{Style.RESET_ALL}")
        
        conversation_count = 0
        max_conversations = 5
        
        while conversation_count < max_conversations:
            print(f"\n{Fore.GREEN}What do you say?{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}(Type 'quit' to end conversation){Style.RESET_ALL}")
            
            user_input = input(f"{Fore.YELLOW}You: {Style.RESET_ALL}").strip()
            
            if user_input.lower() in ['quit', 'exit', 'leave']:
                print(f"\n{Fore.CYAN}{character.name}: {Fore.WHITE}Farewell! Enjoy your stay at The Pub!{Style.RESET_ALL}")
                break
            
            if not user_input:
                continue
            
            # Generate response
            context = f"You are chatting with a patron in The Pub. They just said: '{user_input}'"
            response = self.ai_dialogue.generate_character_response(
                character, context, "conversation", []
            )
            
            print(f"\n{Fore.CYAN}{character.name}: {Fore.WHITE}{response}{Style.RESET_ALL}")
            conversation_count += 1
            
            time.sleep(1)  # Brief pause for natural flow
        
        if conversation_count >= max_conversations:
            print(f"\n{Fore.LIGHTBLACK_EX}{character.name} looks like they need to get back to their drink...{Style.RESET_ALL}")
        
        input(f"\n{Fore.LIGHTBLACK_EX}Press Enter to continue...{Style.RESET_ALL}")
    
    def _view_characters(self):
        """View all characters currently in The Pub"""
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.YELLOW}👥 CHARACTERS IN THE PUB 👥")
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
        
        characters = self.character_manager.list_characters()
        if not characters:
            print(f"{Fore.YELLOW}🤷 The Pub is empty tonight. Create some characters to liven it up!{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}The following adventurers are currently in The Pub:{Style.RESET_ALL}")
            print()
            
            for i, char in enumerate(characters, 1):
                user_marker = " 👤" if char == self.current_user_character else ""
                print(f"{Fore.WHITE}{i}. {Fore.CYAN}{char.name}{user_marker}{Style.RESET_ALL}")
                print(f"   {Fore.LIGHTBLACK_EX}Class: {char.character_class} | Background: {char.background}")
                print(f"   Personality: {char.personality.title()} | Level: {char.level}{Style.RESET_ALL}")
                print(f"   {Fore.WHITE}{char.description}{Style.RESET_ALL}")
                print()
        
        input(f"\n{Fore.LIGHTBLACK_EX}Press Enter to return to menu...{Style.RESET_ALL}")
    
    def _switch_to_spectator(self):
        """Switch to spectator mode"""
        print(f"\n{Fore.YELLOW}🔄 Switching to Spectator Mode...{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}You'll now be able to watch ongoing adventures!{Style.RESET_ALL}")
        time.sleep(1)
        
        # Import and start spectator interface
        from spectator import SpectatorInterface
        spectator = SpectatorInterface()
        spectator.start()