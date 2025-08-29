import openai
import random
import time
from typing import List, Dict, Optional
from character import Character
from world import Area, Dungeon
import config


class AIDialogueSystem:
    """Handles AI-powered conversations between characters"""
    
    def __init__(self):
        self.client = None
        self.mock_mode = True  # Use mock responses if no API key
        
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY.strip():
            try:
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
                self.mock_mode = False
                print("✅ OpenAI API initialized")
            except Exception as e:
                print(f"⚠️ OpenAI API failed to initialize: {e}")
                print("🎭 Using mock dialogue system")
        else:
            print("🎭 No OpenAI API key found, using mock dialogue system")
    
    def generate_character_response(self, character: Character, context: str, 
                                  situation: str, other_characters: List[Character] = None) -> str:
        """Generate a response from a character based on context and situation"""
        
        if self.mock_mode:
            return self._generate_mock_response(character, situation)
        
        try:
            # Build the prompt
            prompt = self._build_character_prompt(character, context, situation, other_characters)
            
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are roleplaying as a character in a text-based fantasy adventure. Respond in character with dialogue and actions. Keep responses concise (1-3 sentences)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return self._generate_mock_response(character, situation)
    
    def generate_group_conversation(self, characters: List[Character], context: str,
                                   topic: str = None) -> List[Dict[str, str]]:
        """Generate a conversation between multiple characters"""
        
        if not characters:
            return []
        
        conversation = []
        num_exchanges = random.randint(2, 4)
        
        for i in range(num_exchanges):
            speaker = random.choice(characters)
            
            # Build situation context
            if i == 0:
                situation = f"Starting a conversation about {topic or 'the current situation'}"
            else:
                # Include previous dialogue for context
                recent_dialogue = " ".join([f"{entry['character']}: {entry['dialogue']}" 
                                          for entry in conversation[-2:]])
                situation = f"Responding to recent conversation: {recent_dialogue}"
            
            dialogue = self.generate_character_response(
                speaker, context, situation, 
                [c for c in characters if c != speaker]
            )
            
            conversation.append({
                'character': speaker.name,
                'dialogue': dialogue,
                'character_class': speaker.character_class
            })
            
            # Add small delay for realism
            time.sleep(0.5)
        
        return conversation
    
    def generate_area_reaction(self, character: Character, area: Area, 
                             tension_level: int = 0, first_visit: bool = False) -> str:
        """Generate a character's reaction to entering an area with tension awareness"""
        
        # Enhanced situation description based on tension level
        if tension_level == 0:
            situation = f"{'Cautiously entering' if first_visit else 'Nervously looking around'} {area.name}: {area.description}"
        elif tension_level == 1:
            situation = f"{'Fearfully stepping into' if first_visit else 'Anxiously scanning'} {area.name}: {area.description}. The danger is escalating."
        elif tension_level == 2:
            situation = f"{'Desperately entering' if first_visit else 'Frantically searching'} {area.name}: {area.description}. Terror grips your heart."
        else:
            situation = f"{'FACING THE ULTIMATE TRIAL in' if first_visit else 'CONFRONTING DESTINY in'} {area.name}: {area.description}. This is the moment of truth."
        
        if area.enemies:
            situation += f" There might be {', '.join(area.enemies)} here."
        
        context = f"You are exploring a dangerous dungeon. Current location: {area.name}. Tension level: {tension_level}/3"
        
        return self.generate_character_response(character, context, situation)
    
    def generate_combat_dialogue(self, character: Character, enemy: str, 
                               tension_level: int = 0, action: str = "attack") -> str:
        """Generate dialogue during combat with escalating intensity"""
        
        if tension_level == 0:
            situation = f"Engaging in combat with {enemy}, performing action: {action}"
            context = "You are in battle, fighting alongside your trusted companions"
        elif tension_level == 1:
            situation = f"Locked in desperate combat with the fearsome {enemy}, performing action: {action}"
            context = "You are in a dangerous battle, your life and your friends' lives hang in the balance"
        elif tension_level == 2:
            situation = f"Fighting for your very soul against the terrifying {enemy}, performing action: {action}"
            context = "You are in a life-or-death battle, facing overwhelming odds with courage"
        else:
            situation = f"CONFRONTING DESTINY against the legendary {enemy}, performing action: {action}"
            context = "You are in the ultimate battle, where legends are born and heroes are made or destroyed"
        
        return self.generate_character_response(character, context, situation)
    
    def _build_character_prompt(self, character: Character, context: str, 
                              situation: str, other_characters: List[Character] = None) -> str:
        """Build a detailed prompt for character response generation"""
        
        prompt = f"{character.get_prompt_context()}\n\n"
        prompt += f"Current context: {context}\n"
        prompt += f"Situation: {situation}\n"
        
        if other_characters:
            companions = ", ".join([f"{c.name} the {c.character_class}" for c in other_characters])
            prompt += f"Your companions: {companions}\n"
        
        prompt += "\nRespond in character with appropriate dialogue and/or actions:"
        
        return prompt
    
    def _generate_mock_response(self, character: Character, situation: str) -> str:
        """Generate mock responses when AI is not available with emotional depth"""
        
        # Detect tension level from situation context
        tension_level = 0
        if "TRIAL" in situation or "DESTINY" in situation:
            tension_level = 3
        elif "terror" in situation.lower() or "desperate" in situation.lower():
            tension_level = 2
        elif "fear" in situation.lower() or "danger" in situation.lower():
            tension_level = 1
        
        # Enhanced response templates based on character class, personality, and tension
        templates = {
            "Warrior": {
                "brave": {
                    0: ["Let's move forward with purpose!", "I'll keep us safe.", "My blade is ready."],
                    1: ["This danger doesn't intimidate me!", "Fear cannot touch a true warrior!", "I'll face whatever comes!"],
                    2: ["By my honor, I will not falter!", "Let them come! I've faced worse!", "We fight together or die together!"],
                    3: ["FOR GLORY AND LEGEND! This is our moment!", "DEATH BEFORE DISHONOR!", "TODAY WE MAKE HISTORY!"]
                },
                "cautious": {
                    0: ["We should proceed carefully.", "Let me assess the situation.", "Stay alert, everyone."],
                    1: ["Something feels wrong here... be ready.", "My instincts are screaming danger.", "We must be extremely careful."],
                    2: ["I fear we're walking into a trap!", "Every fiber of my being says flee!", "This could be our end..."],
                    3: ["THE VERY AIR REEKS OF DEATH! But we must press on!", "GODS PRESERVE US!", "This is beyond anything I've faced!"]
                },
                "hot-headed": {
                    0: ["Let's just get this over with!", "Enough talking, more action!", "I'm ready to fight!"],
                    1: ["Bring on whatever dares to challenge us!", "I'm itching for a real battle!", "Fear just makes me angry!"],
                    2: ["COME AND FACE ME, COWARDS!", "I'LL TEAR THEM APART!", "MY RAGE BURNS HOTTER THAN THEIR EVIL!"],
                    3: ["NOTHING CAN STOP MY FURY! NOTHING!", "I AM WRATH INCARNATE!", "LET THE WORLD TREMBLE!"]
                }
            },
            "Mage": {
                "wise": {
                    0: ["I sense arcane energies here.", "Let me study the magical flows.", "The weave speaks of secrets."],
                    1: ["Dark magic permeates this place...", "The magical balance is disturbed here.", "I feel ancient evils stirring."],
                    2: ["The very fabric of reality screams in pain!", "Such corruption of the arcane arts!", "This darkness defies all natural law!"],
                    3: ["THE ULTIMATE MAGIC AWAKENS! We witness the impossible!", "REALITY ITSELF BENDS TO THIS POWER!", "By the stars... what have we found?"]
                },
                "curious": {
                    0: ["How fascinating! What secrets hide here?", "I wonder what mysteries await.", "Every corner holds new knowledge."],
                    1: ["Despite the danger, I must learn more!", "My curiosity burns brighter than my fear!", "What wonders and terrors might we discover?"],
                    2: ["Even in terror, the pursuit of knowledge calls!", "I must understand, no matter the cost!", "Such dark mysteries demand investigation!"],
                    3: ["THIS IS THE DISCOVERY OF A LIFETIME! Fear be damned!", "ULTIMATE KNOWLEDGE AWAITS!", "History will remember this moment!"]
                }
            },
            "Rogue": {
                "mischievous": {
                    0: ["Heh, wonder what treasures they're hiding.", "Time to see what 'secrets' lurk about.", "Something valuable always hides in dark places."],
                    1: ["Even scared, I can smell opportunity.", "Danger means better loot, right?", "My hands are steady despite the fear."],
                    2: ["Terror just makes the prize sweeter!", "I've stolen from dragons before!", "Fear sharpens the mind and fingers!"],
                    3: ["THE ULTIMATE HEIST AWAITS! Let's take everything!", "LEGENDARY TREASURES FOR LEGENDARY THIEVES!", "This is what legends are made of!"]
                },
                "cautious": {
                    0: ["Something doesn't feel right... stay sharp.", "I'll scout ahead, quietly.", "Trust your instincts, they rarely lie."],
                    1: ["Every shadow could hide death...", "My skin crawls with warning.", "We're being hunted, I can feel it."],
                    2: ["We're walking into certain doom!", "Every step could be our last!", "I've never felt dread like this!"],
                    3: ["THE ULTIMATE TRAP SPRINGS! But maybe... just maybe we can escape!", "THIS IS BEYOND MORTAL COMPREHENSION!", "Gods help us all..."]
                }
            },
            "Cleric": {
                "loyal": {
                    0: ["My faith will protect us all.", "Together, we are stronger.", "The divine light guides our path."],
                    1: ["Though darkness gathers, I stand with you.", "My prayers grow more fervent.", "The light burns brighter in shadow."],
                    2: ["In our darkest hour, faith endures!", "The gods test us, but I will not waver!", "Light shall pierce this evil!"],
                    3: ["BY THE DIVINE LIGHT, WE SHALL TRIUMPH!", "THE GODS THEMSELVES WATCH THIS BATTLE!", "ULTIMATE FAITH FOR THE ULTIMATE TRIAL!"]
                },
                "wise": {
                    0: ["The divine guides those who listen.", "Patience and wisdom light our way.", "All things serve a greater purpose."],
                    1: ["Even in danger, there is divine purpose.", "The gods work in mysterious ways.", "Wisdom tells us to be cautious but brave."],
                    2: ["This trial tests our very souls!", "The gods demand courage in darkness!", "Ancient wisdom speaks of such trials!"],
                    3: ["THIS IS THE DIVINE PLAN UNFOLDING! We are chosen!", "ULTIMATE WISDOM FOR ULTIMATE SACRIFICE!", "THE GODS WRITE LEGEND THROUGH US!"]
                }
            }
        }
        
        # Get character-specific responses
        class_templates = templates.get(character.character_class, {})
        personality_dict = class_templates.get(character.personality, {})
        tension_responses = personality_dict.get(tension_level, [])
        
        # Fallback to lower tension if no responses available
        if not tension_responses:
            for fallback_tension in range(tension_level - 1, -1, -1):
                tension_responses = personality_dict.get(fallback_tension, [])
                if tension_responses:
                    break
        
        # Ultimate fallback responses based on tension
        if not tension_responses:
            if tension_level == 0:
                fallback_responses = [
                    f"*{character.name} nods thoughtfully*",
                    f"\"Interesting...\" says {character.name}.",
                    f"{character.name} looks around carefully."
                ]
            elif tension_level == 1:
                fallback_responses = [
                    f"*{character.name} grips their weapon tighter*",
                    f"\"I don't like this...\" whispers {character.name}.",
                    f"{character.name} scans the shadows nervously."
                ]
            elif tension_level == 2:
                fallback_responses = [
                    f"*{character.name} trembles but stands firm*",
                    f"\"We... we can do this...\" {character.name} says shakily.",
                    f"{character.name} breathes deeply to steady their nerves."
                ]
            else:
                fallback_responses = [
                    f"*{character.name} steels themselves for the ultimate trial*",
                    f"\"THIS IS IT! FOR EVERYTHING WE HOLD DEAR!\" shouts {character.name}.",
                    f"{character.name} radiates determination in the face of legend."
                ]
            return random.choice(fallback_responses)
        
        return f"\"{random.choice(tension_responses)}\" says {character.name}."
    
    def generate_narrative_description(self, situation: str, characters: List[Character],
                                     area: Area = None) -> str:
        """Generate narrative descriptions of events"""
        
        if self.mock_mode:
            return self._generate_mock_narrative(situation, characters, area)
        
        try:
            character_list = ", ".join([f"{c.name} the {c.character_class}" for c in characters])
            location = f" in {area.name}" if area else ""
            
            prompt = f"Write a brief narrative description (1-2 sentences) of: {situation}. "
            prompt += f"Characters involved: {character_list}{location}. "
            prompt += "Write in third person, fantasy adventure style."
            
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a fantasy adventure narrator. Write vivid but concise descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating narrative: {e}")
            return self._generate_mock_narrative(situation, characters, area)
    
    def _generate_mock_narrative(self, situation: str, characters: List[Character], 
                               area: Area = None) -> str:
        """Generate mock narrative descriptions"""
        
        character_names = [c.name for c in characters]
        party_ref = f"{', '.join(character_names[:-1])} and {character_names[-1]}" if len(character_names) > 1 else character_names[0]
        
        location_ref = f" in the {area.name}" if area else ""
        
        templates = [
            f"The party {situation}{location_ref}, their footsteps echoing in the silence.",
            f"{party_ref} {situation}{location_ref}, weapons at the ready.",
            f"As {party_ref} {situation}{location_ref}, the air grows thick with anticipation.",
            f"The adventurers {situation}{location_ref}, their torches casting dancing shadows.",
            f"{party_ref} carefully {situation}{location_ref}, alert for any signs of danger."
        ]
        
        return random.choice(templates)