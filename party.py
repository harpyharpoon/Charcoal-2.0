import json
import random
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from character import Character
from world import WorldManager, Area
from ai_dialogue import AIDialogueSystem
from items import Item
import config


@dataclass
class PartyLog:
    """Represents a log entry for party activities"""
    timestamp: str
    event_type: str  # "movement", "dialogue", "combat", "discovery", "narrative"
    description: str
    characters_involved: List[str]
    location: str


class Party:
    """Represents a party of AI characters exploring together"""
    
    def __init__(self, name: str, characters: List[Character]):
        self.name = name
        self.characters = characters
        self.log: List[PartyLog] = []
        self.current_hp = {char.name: char.hp for char in characters}
        self.inventory: List[Item] = []  # Changed from List[str] to List[Item]
        self.experience_gained = 0
        self.areas_discovered = []
        self.active = True
    
    def add_log_entry(self, event_type: str, description: str, 
                     characters_involved: List[str] = None, location: str = "Unknown"):
        """Add an entry to the party log"""
        if characters_involved is None:
            characters_involved = [char.name for char in self.characters]
        
        entry = PartyLog(
            timestamp=time.strftime("%H:%M:%S"),
            event_type=event_type,
            description=description,
            characters_involved=characters_involved,
            location=location
        )
        self.log.append(entry)
        
        # Keep log from getting too long
        if len(self.log) > config.SPECTATOR_LOG_LENGTH:
            self.log.pop(0)
    
    def get_recent_log(self, count: int = 10) -> List[PartyLog]:
        """Get recent log entries"""
        return self.log[-count:]
    
    def get_party_status(self) -> str:
        """Get current party status"""
        alive_count = sum(1 for hp in self.current_hp.values() if hp > 0)
        status = f"**{self.name}** ({alive_count}/{len(self.characters)} alive)\n"
        status += f"Areas discovered: {len(self.areas_discovered)}\n"
        status += f"Experience gained: {self.experience_gained}\n"
        if self.inventory:
            item_names = [item.get_display_name() for item in self.inventory[:3]]
            status += f"Inventory: {', '.join(item_names)}"
            if len(self.inventory) > 3:
                status += f" (+{len(self.inventory) - 3} more)"
        return status
    
    def is_alive(self) -> bool:
        """Check if party has any living members"""
        return any(hp > 0 for hp in self.current_hp.values())
    
    def to_dict(self) -> Dict:
        """Convert party to dictionary for serialization"""
        return {
            'name': self.name,
            'characters': [char.to_dict() for char in self.characters],
            'log': [asdict(entry) for entry in self.log],
            'current_hp': self.current_hp,
            'inventory': [item.name for item in self.inventory],  # Simplified for now
            'experience_gained': self.experience_gained,
            'areas_discovered': self.areas_discovered,
            'active': self.active
        }


class PartyManager:
    """Manages party creation and adventures"""
    
    def __init__(self, character_manager, world_manager):
        self.character_manager = character_manager
        self.world_manager = world_manager
        self.dialogue_system = AIDialogueSystem()
        self.active_parties: Dict[str, Party] = {}
        self.adventure_step_count = 0
    
    def create_party(self, party_name: str, character_names: List[str]) -> Optional[Party]:
        """Create a new party with specified characters"""
        characters = []
        for name in character_names:
            char = self.character_manager.get_character(name)
            if char:
                characters.append(char)
            else:
                print(f"Warning: Character '{name}' not found")
        
        if len(characters) < 2:
            print("Need at least 2 characters to form a party")
            return None
        
        party = Party(party_name, characters)
        self.active_parties[party_name] = party
        
        # Log party formation
        char_list = ", ".join([char.name for char in characters])
        party.add_log_entry(
            "formation", 
            f"Party '{party_name}' formed with members: {char_list}",
            location="Tavern"
        )
        
        return party
    
    def create_random_party(self, party_name: str = None) -> Party:
        """Create a random party from available characters"""
        if party_name is None:
            party_name = f"Party {len(self.active_parties) + 1}"
        
        available_chars = self.character_manager.list_characters()
        party_size = min(config.PARTY_SIZE, len(available_chars))
        selected_chars = random.sample(available_chars, party_size)
        
        return self.create_party(party_name, [char.name for char in selected_chars])
    
    def advance_party_adventure(self, party_name: str) -> Dict[str, any]:
        """Advance a party's adventure by one step"""
        party = self.active_parties.get(party_name)
        if not party or not party.active or not party.is_alive():
            return {"success": False, "reason": "Party not available for adventure"}
        
        dungeon = self.world_manager.get_current_dungeon()
        if not dungeon:
            return {"success": False, "reason": "No active dungeon"}
        
        current_area = dungeon.get_current_area()
        self.adventure_step_count += 1
        
        # Determine what happens this step
        action_type = self._determine_action_type(current_area, party)
        
        result = {"success": True, "action_type": action_type, "events": []}
        
        if action_type == "explore":
            result["events"].extend(self._handle_exploration(party, current_area, dungeon))
        elif action_type == "dialogue":
            result["events"].extend(self._handle_party_dialogue(party, current_area))
        elif action_type == "move":
            result["events"].extend(self._handle_movement(party, current_area, dungeon))
        elif action_type == "encounter":
            result["events"].extend(self._handle_encounter(party, current_area))
        elif action_type == "discovery":
            result["events"].extend(self._handle_discovery(party, current_area))
        
        return result
    
    def _determine_action_type(self, area: Area, party: Party) -> str:
        """Determine what type of action should happen this step"""
        # Simple logic for now - could be much more sophisticated
        
        # Regular dialogue every few steps
        if self.adventure_step_count % config.DIALOGUE_FREQUENCY == 0:
            return "dialogue"
        
        # Chance-based actions
        roll = random.random()
        
        if roll < 0.3:
            return "explore"
        elif roll < 0.5:
            return "move"
        elif roll < 0.7:
            return "encounter"
        elif roll < 0.9:
            return "discovery"
        else:
            return "dialogue"
    
    def _handle_exploration(self, party: Party, area: Area, dungeon) -> List[Dict]:
        """Handle area exploration"""
        events = []
        
        # Generate narrative
        narrative = self.dialogue_system.generate_narrative_description(
            "explore the area carefully", party.characters, area
        )
        
        party.add_log_entry(
            "narrative", narrative, location=area.name
        )
        events.append({"type": "narrative", "content": narrative})
        
        # Random character reaction
        reactor = random.choice(party.characters)
        reaction = self.dialogue_system.generate_area_reaction(reactor, area)
        
        party.add_log_entry(
            "dialogue", f"{reactor.name}: {reaction}", 
            [reactor.name], area.name
        )
        events.append({"type": "dialogue", "character": reactor.name, "content": reaction})
        
        return events
    
    def _handle_party_dialogue(self, party: Party, area: Area) -> List[Dict]:
        """Handle dialogue between party members"""
        events = []
        
        # Generate a conversation
        topics = [
            "the current situation", "the dangers ahead", "their past adventures",
            "the mysteries of this place", "their hopes and fears", "strategy"
        ]
        topic = random.choice(topics)
        
        conversation = self.dialogue_system.generate_group_conversation(
            party.characters, f"Currently in {area.name}", topic
        )
        
        for exchange in conversation:
            party.add_log_entry(
                "dialogue", 
                f"{exchange['character']}: {exchange['dialogue']}",
                [exchange['character']], area.name
            )
            events.append({
                "type": "dialogue", 
                "character": exchange['character'],
                "content": exchange['dialogue']
            })
        
        return events
    
    def _handle_movement(self, party: Party, area: Area, dungeon) -> List[Dict]:
        """Handle party movement to new area"""
        events = []
        
        available_exits = dungeon.get_available_moves()
        if not available_exits:
            # Generate dialogue about being stuck
            speaker = random.choice(party.characters)
            dialogue = f"\"It looks like we've reached a dead end...\" says {speaker.name}."
            party.add_log_entry("dialogue", dialogue, [speaker.name], area.name)
            events.append({"type": "dialogue", "character": speaker.name, "content": dialogue})
            return events
        
        # Choose where to go
        next_area = random.choice(available_exits)
        
        if dungeon.move_to_area(next_area):
            new_area = dungeon.get_current_area()
            
            # Generate movement narrative
            narrative = f"The party moves from {area.name} to {new_area.name}."
            party.add_log_entry("movement", narrative, location=new_area.name)
            events.append({"type": "movement", "content": narrative})
            
            # Track discovery
            if new_area.name not in party.areas_discovered:
                party.areas_discovered.append(new_area.name)
                discovery_text = f"**New area discovered: {new_area.name}**"
                party.add_log_entry("discovery", discovery_text, location=new_area.name)
                events.append({"type": "discovery", "content": discovery_text})
            
            # Generate character reaction to new area
            reactor = random.choice(party.characters)
            reaction = self.dialogue_system.generate_area_reaction(
                reactor, new_area, new_area.name not in party.areas_discovered
            )
            party.add_log_entry("dialogue", f"{reactor.name}: {reaction}", [reactor.name], new_area.name)
            events.append({"type": "dialogue", "character": reactor.name, "content": reaction})
        
        return events
    
    def _handle_encounter(self, party: Party, area: Area) -> List[Dict]:
        """Handle encounters with enemies or NPCs"""
        events = []
        
        if not area.enemies:
            return self._handle_discovery(party, area)
        
        enemy = random.choice(area.enemies)
        
        # Generate encounter narrative
        narrative = f"The party encounters {enemy}!"
        party.add_log_entry("encounter", narrative, location=area.name)
        events.append({"type": "encounter", "content": narrative})
        
        # Generate combat dialogue
        fighter = random.choice(party.characters)
        combat_dialogue = self.dialogue_system.generate_combat_dialogue(fighter, enemy)
        party.add_log_entry("dialogue", f"{fighter.name}: {combat_dialogue}", [fighter.name], area.name)
        events.append({"type": "dialogue", "character": fighter.name, "content": combat_dialogue})
        
        # Simple combat resolution
        success = random.random() > 0.3  # 70% success rate
        
        if success:
            party.experience_gained += random.randint(10, 30)
            result_text = f"The party defeats the {enemy}!"
        else:
            # Party takes damage
            injured = random.choice(party.characters)
            damage = random.randint(10, 25)
            party.current_hp[injured.name] = max(0, party.current_hp[injured.name] - damage)
            result_text = f"The {enemy} injures {injured.name}! ({damage} damage)"
        
        party.add_log_entry("combat", result_text, location=area.name)
        events.append({"type": "combat", "content": result_text})
        
        return events
    
    def _handle_discovery(self, party: Party, area: Area) -> List[Dict]:
        """Handle treasure or item discovery"""
        events = []
        
        if area.treasures:
            treasure = random.choice(area.treasures)
            party.inventory.append(treasure)
            
            discovery_text = f"The party discovers: {treasure.get_display_name()}!"
            party.add_log_entry("discovery", discovery_text, location=area.name)
            events.append({"type": "discovery", "content": discovery_text})
            
            # Generate reaction
            reactor = random.choice(party.characters)
            reaction = f"\"Excellent find!\" exclaims {reactor.name}."
            party.add_log_entry("dialogue", f"{reactor.name}: {reaction}", [reactor.name], area.name)
            events.append({"type": "dialogue", "character": reactor.name, "content": reaction})
            
            # Remove the treasure from the area so it can't be found again
            area.treasures.remove(treasure)
        
        return events
    
    def get_party(self, party_name: str) -> Optional[Party]:
        """Get a party by name"""
        return self.active_parties.get(party_name)
    
    def list_parties(self) -> List[str]:
        """Get list of active party names"""
        return list(self.active_parties.keys())
    
    def save_parties(self):
        """Save parties to file"""
        try:
            with open('parties.json', 'w') as f:
                json.dump({name: party.to_dict() for name, party in self.active_parties.items()}, f, indent=2)
        except Exception as e:
            print(f"Error saving parties: {e}")
    
    def load_parties(self):
        """Load parties from file"""
        try:
            with open('parties.json', 'r') as f:
                data = json.load(f)
                # Note: This is a simplified load - in a full implementation,
                # we'd need to properly reconstruct Character objects
                print(f"Found {len(data)} saved parties")
        except FileNotFoundError:
            pass  # No saved parties
        except Exception as e:
            print(f"Error loading parties: {e}")