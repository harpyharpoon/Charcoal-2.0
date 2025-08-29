import time
import threading
from typing import Dict, List, Optional
from character import CharacterManager
from world import WorldManager
from party import PartyManager, Party
import config
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()


class SpectatorInterface:
    """Text-based interface for watching party adventures"""
    
    def __init__(self):
        self.character_manager = CharacterManager()
        self.world_manager = WorldManager()
        self.party_manager = PartyManager(self.character_manager, self.world_manager)
        self.running = False
        self.current_party = None
        self.auto_advance = False
        
    def start(self):
        """Start the spectator interface"""
        self.running = True
        self._print_welcome()
        self._main_loop()
    
    def stop(self):
        """Stop the spectator interface"""
        self.running = False
    
    def _print_welcome(self):
        """Print welcome message and instructions"""
        self._clear_screen()
        
        print(f"{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.YELLOW}🔥 CHARCOAL 2.0 - SPECTATOR MODE 🔥")
        print(f"{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.WHITE}")
        print("Welcome to the AI Adventure Spectator!")
        print("Watch as AI characters form parties and explore dungeons.")
        print()
        print(f"{Fore.GREEN}Commands:")
        print(f"{Fore.WHITE}  create party - Create a new random party")
        print(f"  watch <party> - Watch a specific party")
        print(f"  list parties - Show all active parties")
        print(f"  list chars   - Show all available characters")
        print(f"  list dungeons - Show available dungeons")
        print(f"  change dungeon <name> - Switch to different dungeon")
        print(f"  step         - Advance current party one step")
        print(f"  auto         - Toggle auto-advance mode")
        print(f"  status       - Show current status")
        print(f"  help         - Show this help")
        print(f"  quit         - Exit the program")
        print(f"{Fore.CYAN}{'=' * 60}")
        print(f"{Style.RESET_ALL}")
    
    def _main_loop(self):
        """Main interaction loop"""
        while self.running:
            try:
                if self.auto_advance and self.current_party:
                    self._auto_advance_step()
                    time.sleep(config.AUTO_ADVANCE_DELAY)
                else:
                    command = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip().lower()
                    self._handle_command(command)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    def _handle_command(self, command: str):
        """Handle user commands"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0]
        
        if cmd == "create" and len(parts) > 1 and parts[1] == "party":
            self._create_party()
        elif cmd == "watch" and len(parts) > 1:
            party_name = " ".join(parts[1:])
            self._watch_party(party_name)
        elif cmd == "list":
            if len(parts) > 1:
                if parts[1] == "parties":
                    self._list_parties()
                elif parts[1] == "chars":
                    self._list_characters()
                elif parts[1] == "dungeons":
                    self._list_dungeons()
                else:
                    print(f"{Fore.RED}Unknown list command. Try 'parties', 'chars', or 'dungeons'{Style.RESET_ALL}")
            else:
                self._list_parties()
        elif cmd == "change" and len(parts) > 2 and parts[1] == "dungeon":
            dungeon_name = parts[2]
            self._change_dungeon(dungeon_name)
        elif cmd == "step":
            self._advance_step()
        elif cmd == "auto":
            self._toggle_auto()
        elif cmd == "status":
            self._show_status()
        elif cmd == "help":
            self._print_welcome()
        elif cmd == "quit" or cmd == "exit":
            self.running = False
        else:
            print(f"{Fore.RED}Unknown command. Type 'help' for available commands.{Style.RESET_ALL}")
    
    def _create_party(self):
        """Create a new random party"""
        party = self.party_manager.create_random_party()
        print(f"{Fore.GREEN}✅ Created party: {party.name}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Members: {', '.join([char.name for char in party.characters])}{Style.RESET_ALL}")
        
        if not self.current_party:
            self.current_party = party.name
            print(f"{Fore.YELLOW}👁️ Now watching: {party.name}{Style.RESET_ALL}")
    
    def _watch_party(self, party_name: str):
        """Switch to watching a specific party"""
        party = self.party_manager.get_party(party_name)
        if party:
            self.current_party = party_name
            print(f"{Fore.YELLOW}👁️ Now watching: {party_name}{Style.RESET_ALL}")
            self._display_party_status(party)
        else:
            print(f"{Fore.RED}❌ Party '{party_name}' not found{Style.RESET_ALL}")
    
    def _list_parties(self):
        """List all active parties"""
        parties = self.party_manager.list_parties()
        if parties:
            print(f"{Fore.CYAN}🎭 Active Parties:{Style.RESET_ALL}")
            for party_name in parties:
                party = self.party_manager.get_party(party_name)
                status = "👁️ " if party_name == self.current_party else "   "
                alive_count = sum(1 for hp in party.current_hp.values() if hp > 0)
                print(f"{status}{Fore.WHITE}{party_name} ({alive_count}/{len(party.characters)} alive){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No active parties. Create one with 'create party'{Style.RESET_ALL}")
    
    def _list_characters(self):
        """List all available characters"""
        characters = self.character_manager.list_characters()
        print(f"{Fore.CYAN}🛡️ Available Characters:{Style.RESET_ALL}")
        for char in characters:
            print(f"  {Fore.WHITE}{char.name} - {char.character_class} ({char.background}){Style.RESET_ALL}")
            print(f"    {Fore.LIGHTBLACK_EX}Personality: {char.personality}{Style.RESET_ALL}")
    
    def _list_dungeons(self):
        """List available dungeons"""
        dungeons = self.world_manager.list_dungeons()
        current = self.world_manager.current_dungeon
        print(f"{Fore.CYAN}🏰 Available Dungeons:{Style.RESET_ALL}")
        for dungeon_name in dungeons:
            dungeon = self.world_manager.dungeons[dungeon_name]
            marker = "👁️ " if dungeon_name == current else "   "
            print(f"{marker}{Fore.WHITE}{dungeon.name} ({dungeon.theme}){Style.RESET_ALL}")
    
    def _change_dungeon(self, dungeon_name: str):
        """Change to a different dungeon"""
        if self.world_manager.change_dungeon(dungeon_name):
            dungeon = self.world_manager.get_current_dungeon()
            print(f"{Fore.GREEN}✅ Switched to: {dungeon.name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Dungeon '{dungeon_name}' not found{Style.RESET_ALL}")
    
    def _advance_step(self):
        """Advance the current party one step"""
        if not self.current_party:
            print(f"{Fore.RED}❌ No party selected. Use 'watch <party>' or 'create party'{Style.RESET_ALL}")
            return
        
        result = self.party_manager.advance_party_adventure(self.current_party)
        if result["success"]:
            self._display_adventure_events(result["events"])
        else:
            print(f"{Fore.RED}❌ {result['reason']}{Style.RESET_ALL}")
    
    def _auto_advance_step(self):
        """Auto-advance the current party"""
        if self.current_party:
            result = self.party_manager.advance_party_adventure(self.current_party)
            if result["success"]:
                self._display_adventure_events(result["events"])
            else:
                print(f"{Fore.RED}❌ Auto-advance stopped: {result['reason']}{Style.RESET_ALL}")
                self.auto_advance = False
    
    def _toggle_auto(self):
        """Toggle auto-advance mode"""
        self.auto_advance = not self.auto_advance
        if self.auto_advance:
            if self.current_party:
                print(f"{Fore.GREEN}🔄 Auto-advance enabled for {self.current_party}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Press Ctrl+C to stop auto-advance{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ No party selected for auto-advance{Style.RESET_ALL}")
                self.auto_advance = False
        else:
            print(f"{Fore.YELLOW}⏸️ Auto-advance disabled{Style.RESET_ALL}")
    
    def _show_status(self):
        """Show current system status"""
        print(f"{Fore.CYAN}📊 System Status:{Style.RESET_ALL}")
        
        # World status
        world_status = self.world_manager.get_world_status()
        print(f"{Fore.WHITE}World: {world_status}{Style.RESET_ALL}")
        
        # Current party status
        if self.current_party:
            party = self.party_manager.get_party(self.current_party)
            print(f"{Fore.WHITE}Watching: {party.get_party_status()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No party currently being watched{Style.RESET_ALL}")
        
        # Auto-advance status
        auto_status = "ON" if self.auto_advance else "OFF"
        print(f"{Fore.WHITE}Auto-advance: {auto_status}{Style.RESET_ALL}")
    
    def _display_party_status(self, party: Party):
        """Display detailed party status"""
        print(f"\n{Fore.CYAN}{'─' * 50}")
        print(f"{Fore.YELLOW}Party Status: {party.name}")
        print(f"{Fore.CYAN}{'─' * 50}")
        
        # Character status
        for char in party.characters:
            hp = party.current_hp[char.name]
            hp_color = Fore.GREEN if hp > 50 else Fore.YELLOW if hp > 20 else Fore.RED
            print(f"{Fore.WHITE}{char.name} ({char.character_class}): {hp_color}{hp}/100 HP{Style.RESET_ALL}")
        
        # Recent log
        recent_log = party.get_recent_log(5)
        if recent_log:
            print(f"\n{Fore.CYAN}Recent Events:{Style.RESET_ALL}")
            for entry in recent_log:
                self._display_log_entry(entry)
        
        print(f"{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}\n")
    
    def _display_adventure_events(self, events: List[Dict]):
        """Display adventure events in real-time"""
        for event in events:
            self._display_event(event)
            time.sleep(0.5)  # Pause between events for readability
    
    def _display_event(self, event: Dict):
        """Display a single adventure event"""
        event_type = event["type"]
        
        if event_type == "narrative":
            print(f"{Fore.CYAN}📖 {event['content']}{Style.RESET_ALL}")
        elif event_type == "dialogue":
            char_name = event.get("character", "Unknown")
            print(f"{Fore.YELLOW}💬 {char_name}: {Fore.WHITE}{event['content']}{Style.RESET_ALL}")
        elif event_type == "movement":
            print(f"{Fore.GREEN}🚶 {event['content']}{Style.RESET_ALL}")
        elif event_type == "discovery":
            print(f"{Fore.MAGENTA}✨ {event['content']}{Style.RESET_ALL}")
        elif event_type == "encounter":
            print(f"{Fore.RED}⚔️ {event['content']}{Style.RESET_ALL}")
        elif event_type == "combat":
            print(f"{Fore.RED}🗡️ {event['content']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}📝 {event['content']}{Style.RESET_ALL}")
    
    def _display_log_entry(self, entry):
        """Display a log entry"""
        timestamp = entry.timestamp
        
        if entry.event_type == "dialogue":
            print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.YELLOW}💬 {entry.description}{Style.RESET_ALL}")
        elif entry.event_type == "movement":
            print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.GREEN}🚶 {entry.description}{Style.RESET_ALL}")
        elif entry.event_type == "discovery":
            print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.MAGENTA}✨ {entry.description}{Style.RESET_ALL}")
        elif entry.event_type == "encounter":
            print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.RED}⚔️ {entry.description}{Style.RESET_ALL}")
        elif entry.event_type == "combat":
            print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.RED}🗡️ {entry.description}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.WHITE}📝 {entry.description}{Style.RESET_ALL}")
    
    def _clear_screen(self):
        """Clear the screen (basic implementation)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main function to start the spectator interface"""
    try:
        interface = SpectatorInterface()
        interface.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()