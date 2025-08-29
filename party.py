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
        """Handle area exploration with building suspense"""
        events = []
        
        # Add tension level based on adventure progress
        tension_level = min(self.adventure_step_count // 3, 3)  # Escalates every 3 steps
        
        # Generate suspenseful exploration narrative based on area and tension
        if tension_level == 0:
            narratives = [
                f"The party cautiously steps into {area.name}, their footsteps echoing ominously...",
                f"As they enter {area.name}, a chill runs down their spines...",
                f"The shadows in {area.name} seem to shift and watch their every move...",
                f"Something feels wrong about {area.name}, but the party presses forward..."
            ]
        elif tension_level == 1:
            narratives = [
                f"The oppressive atmosphere of {area.name} weighs heavily on the party's minds...",
                f"Strange whispers seem to emanate from the very walls of {area.name}...",
                f"The party's torchlight flickers nervously as they explore {area.name}...",
                f"An unsettling presence watches from the darkness of {area.name}..."
            ]
        elif tension_level == 2:
            narratives = [
                f"Terror grips the party as they venture deeper into {area.name}...",
                f"The very air in {area.name} crackles with malevolent energy...",
                f"Ancient evils stir as the party disturbs the sanctity of {area.name}...",
                f"Death itself seems to lurk in every shadow of {area.name}..."
            ]
        else:  # Maximum tension
            narratives = [
                f"THE DARKNESS OF {area.name.upper()} CONSUMES ALL HOPE...",
                f"FATE ITSELF TREMBLES AS THE PARTY FACES {area.name.upper()}...",
                f"THE FINAL HOUR APPROACHES IN THE CURSED REALM OF {area.name.upper()}...",
                f"LEGENDS WILL BE BORN OR DIE IN {area.name.upper()}..."
            ]
        
        narrative = random.choice(narratives)
        party.add_log_entry(
            "narrative", narrative, location=area.name
        )
        events.append({"type": "narrative", "content": narrative, "tension": tension_level})
        
        # Character reaction shows rising fear/determination
        reactor = random.choice(party.characters)
        reaction = self.dialogue_system.generate_area_reaction(reactor, area, tension_level)
        
        party.add_log_entry(
            "dialogue", f"{reactor.name}: {reaction}", 
            [reactor.name], area.name
        )
        events.append({"type": "dialogue", "character": reactor.name, "content": reaction, "tension": tension_level})
        
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
        """Handle encounters with enemies or NPCs with dramatic tension"""
        events = []
        
        if not area.enemies:
            return self._handle_discovery(party, area)
        
        enemy = random.choice(area.enemies)
        tension_level = min(self.adventure_step_count // 3, 3)
        
        # Build suspense before revealing the encounter
        buildup_events = [
            "The party suddenly freezes... something is watching them.",
            "A low growl echoes through the shadows ahead...",
            "The temperature drops as an ancient evil stirs...",
            "Footsteps that aren't their own echo behind them...",
            "The very air seems to thicken with malevolent presence..."
        ]
        
        buildup = random.choice(buildup_events)
        party.add_log_entry("narrative", buildup, location=area.name)
        events.append({"type": "narrative", "content": buildup, "suspense": True})
        
        # Dramatic encounter reveal based on tension level
        if tension_level <= 1:
            narrative = f"From the shadows emerges... {enemy}!"
        elif tension_level == 2:
            narrative = f"TERROR INCARNATE! A fearsome {enemy} blocks their path!"
        else:
            narrative = f"💀 THE ULTIMATE TRIAL! A legendary {enemy} appears, thirsting for blood!"
        
        party.add_log_entry("encounter", narrative, location=area.name)
        events.append({"type": "encounter", "content": narrative, "tension": tension_level})
        
        # Generate intense combat dialogue
        fighter = random.choice(party.characters)
        combat_dialogue = self.dialogue_system.generate_combat_dialogue(fighter, enemy, tension_level)
        party.add_log_entry("dialogue", f"{fighter.name}: {combat_dialogue}", [fighter.name], area.name)
        events.append({"type": "dialogue", "character": fighter.name, "content": combat_dialogue})
        
        # Enhanced combat resolution with higher stakes
        base_success_rate = 0.7 - (tension_level * 0.1)  # Harder as tension rises
        success = random.random() < base_success_rate
        
        if success:
            exp_gain = random.randint(15, 40) + (tension_level * 10)
            party.experience_gained += exp_gain
            victory_messages = [
                f"Against all odds, the party triumphs over the {enemy}!",
                f"Victory! The {enemy} falls before their united strength!",
                f"Through courage and skill, they defeat the {enemy}!",
                f"🏆 LEGENDARY VICTORY! The {enemy} is vanquished!"
            ]
            result_text = random.choice(victory_messages)
        else:
            # Dramatic injury/failure
            injured = random.choice(party.characters)
            damage = random.randint(15, 35) + (tension_level * 5)
            party.current_hp[injured.name] = max(0, party.current_hp[injured.name] - damage)
            
            injury_messages = [
                f"💔 {injured.name} cries out in pain as the {enemy} strikes! ({damage} damage)",
                f"🩸 The {enemy} lands a devastating blow on {injured.name}! ({damage} damage)",
                f"⚡ {injured.name} staggers from the {enemy}'s brutal attack! ({damage} damage)",
                f"💀 CRITICAL HIT! {injured.name} barely survives the {enemy}'s assault! ({damage} damage)"
            ]
            result_text = random.choice(injury_messages)
        
        party.add_log_entry("combat", result_text, location=area.name)
        events.append({"type": "combat", "content": result_text, "success": success})
        
        return events
    
    def _handle_discovery(self, party: Party, area: Area) -> List[Dict]:
        """Handle treasure or item discovery with suspenseful buildup"""
        events = []
        
        if area.treasures:
            treasure = random.choice(area.treasures)
            tension_level = min(self.adventure_step_count // 3, 3)
            
            # Build suspense before the discovery
            mystery_events = [
                "Something glimmers in the shadows...",
                "A faint light emanates from a hidden alcove...",
                "The party notices something peculiar about this place...",
                "Ancient magic pulses through the air...",
                "A secret waits to be uncovered..."
            ]
            
            buildup = random.choice(mystery_events)
            party.add_log_entry("narrative", buildup, location=area.name)
            events.append({"type": "narrative", "content": buildup, "suspense": True})
            
            # Dramatic discovery reveal
            rarity_emojis = {"Common": "⭐", "Uncommon": "✨", "Rare": "💎", "Legendary": "🏆", "Mythic": "🌟"}
            rarity = getattr(treasure, 'rarity', 'Common')
            emoji = rarity_emojis.get(rarity, "✨")
            
            if tension_level == 0:
                discovery_text = f"The party discovers: {treasure.get_display_name()} {emoji}!"
            elif tension_level == 1:
                discovery_text = f"🔮 INCREDIBLE FIND! The party uncovers: {treasure.get_display_name()} {emoji}!"
            elif tension_level == 2:
                discovery_text = f"✨ LEGENDARY DISCOVERY! Hidden for ages: {treasure.get_display_name()} {emoji}!"
            else:
                discovery_text = f"🌟 MYTHIC TREASURE! The gods smile upon them: {treasure.get_display_name()} {emoji}!"
            
            party.inventory.append(treasure)
            party.add_log_entry("discovery", discovery_text, location=area.name)
            events.append({"type": "discovery", "content": discovery_text, "tension": tension_level})
            
            # Enhanced character reactions
            reactor = random.choice(party.characters)
            excitement_reactions = [
                f"\"By the gods! Look at this treasure!\" gasps {reactor.name}.",
                f"\"This will serve us well in our quest!\" exclaims {reactor.name}.",
                f"\"Fortune favors the bold!\" cheers {reactor.name}.",
                f"\"Our luck is changing!\" says {reactor.name} with excitement.",
                f"\"The ancestors guide our steps!\" whispers {reactor.name} in awe."
            ]
            
            reaction = random.choice(excitement_reactions)
            party.add_log_entry("dialogue", f"{reactor.name}: {reaction}", [reactor.name], area.name)
            events.append({"type": "dialogue", "character": reactor.name, "content": reaction})
            
            # Remove the treasure from the area so it can't be found again
            area.treasures.remove(treasure)
        else:
            # No treasure found - add atmosphere
            empty_searches = [
                "The party searches thoroughly but finds nothing of value...",
                "Their hopes are dashed as the search yields nothing...",
                "The shadows mock their efforts with empty silence...",
                "Only dust and disappointment await them here..."
            ]
            
            empty_result = random.choice(empty_searches)
            party.add_log_entry("narrative", empty_result, location=area.name)
            events.append({"type": "narrative", "content": empty_result})
        
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