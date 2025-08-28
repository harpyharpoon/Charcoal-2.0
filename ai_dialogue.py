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
                             first_visit: bool = False) -> str:
        """Generate a character's reaction to entering an area"""
        
        situation = f"{'Entering' if first_visit else 'Looking around'} {area.name}: {area.description}"
        if area.enemies:
            situation += f" There might be {', '.join(area.enemies)} here."
        
        context = f"You are exploring a dungeon. Current location: {area.name}"
        
        return self.generate_character_response(character, context, situation)
    
    def generate_combat_dialogue(self, character: Character, enemy: str, 
                               action: str = "attack") -> str:
        """Generate dialogue during combat"""
        
        situation = f"In combat with {enemy}, performing action: {action}"
        context = "You are in battle, fighting for your life and your party"
        
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
        """Generate mock responses when AI is not available"""
        
        # Define response templates based on character class and personality
        templates = {
            "Warrior": {
                "brave": ["Let's charge forward!", "I'll protect the party!", "My sword is ready!"],
                "cautious": ["We should be careful here.", "Let me check for traps first.", "Stay close together."],
                "hot-headed": ["I've had enough of this!", "Let's fight!", "Come on then!"]
            },
            "Mage": {
                "wise": ["I sense magical energy here.", "Let me study this carefully.", "The arcane flows are strong."],
                "curious": ["Fascinating! What's that over there?", "I wonder what this does...", "How intriguing!"],
                "serious": ["Focus on the task at hand.", "We must proceed methodically.", "This requires concentration."]
            },
            "Rogue": {
                "mischievous": ["I'll check for traps... and treasure.", "Something doesn't feel right.", "Trust me on this one."],
                "cautious": ["Wait, let me scout ahead.", "I hear something...", "Better safe than sorry."],
                "independent": ["I'll handle this myself.", "Don't worry about me.", "I work better alone."]
            },
            "Cleric": {
                "loyal": ["I'll keep everyone safe.", "My faith will guide us.", "We're stronger together."],
                "wise": ["The gods watch over us.", "There is wisdom in patience.", "Let us pray for guidance."],
                "cheerful": ["Stay positive, friends!", "The light will see us through!", "We can do this!"]
            }
        }
        
        # Get appropriate responses
        class_templates = templates.get(character.character_class, {})
        personality_responses = class_templates.get(character.personality, [])
        
        # Fallback responses
        if not personality_responses:
            fallback_responses = [
                f"*{character.name} nods thoughtfully*",
                f"\"Interesting...\" says {character.name}.",
                f"{character.name} looks around carefully.",
                f"\"What do you think?\" asks {character.name}.",
                f"{character.name} adjusts their equipment."
            ]
            return random.choice(fallback_responses)
        
        return f"\"{random.choice(personality_responses)}\" says {character.name}."
    
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