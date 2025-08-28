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
AUTO_ADVANCE_DELAY = int(os.getenv("AUTO_ADVANCE_DELAY", "2"))

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