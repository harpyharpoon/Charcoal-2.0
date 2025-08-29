import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Game Configuration
PARTY_SIZE = int(os.getenv("PARTY_SIZE", "4"))
DIALOGUE_FREQUENCY = int(os.getenv("DIALOGUE_FREQUENCY", "3"))
AUTO_ADVANCE_DELAY = int(os.getenv("AUTO_ADVANCE_DELAY", "8"))  # Increased for more suspense

# Timing Configuration for Human-like Pacing
DIALOGUE_DELAY = float(os.getenv("DIALOGUE_DELAY", "2.5"))  # Pause between dialogue lines
EVENT_BUILDUP_DELAY = float(os.getenv("EVENT_BUILDUP_DELAY", "3.0"))  # Dramatic pause before major events
DISCOVERY_SUSPENSE_DELAY = float(os.getenv("DISCOVERY_SUSPENSE_DELAY", "4.0"))  # Build tension before discoveries
COMBAT_TENSION_DELAY = float(os.getenv("COMBAT_TENSION_DELAY", "5.0"))  # Heighten combat anticipation

# Display Configuration
USE_COLORS = True
SPECTATOR_LOG_LENGTH = 50

# Character Classes
CHARACTER_CLASSES = [
    "Warrior", "Mage", "Rogue", "Cleric", "Archer", "Paladin", "Bard", "Druid"
]

# Character Backgrounds
CHARACTER_BACKGROUNDS = [
    "Noble", "Criminal", "Folk Hero", "Hermit", "Entertainer", "Guild Artisan",
    "Outlander", "Sage", "Soldier", "Charlatan"
]