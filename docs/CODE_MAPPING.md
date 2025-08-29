# Code Conversion Mapping

## Overview

This document analyzes the current Charcoal 2.0 codebase and identifies which logic should remain in the Python backend versus what should be moved to the JavaScript frontend for the architecture separation.

## Current Code Analysis

### Backend-Only Logic (Keep in Python)

#### 1. Core Game Logic (`party.py`)
**Location**: `PartyManager` class and related functions

**Why Backend**: 
- Game state must be authoritative server-side
- AI decision making requires OpenAI API access
- Adventure progression needs to be consistent across multiple spectators
- Security: Prevent client-side manipulation of game outcomes

**Code to Keep**:
```python
class PartyManager:
    def create_random_party(self, name: str) -> Party
    def advance_party_adventure(self, party_name: str) -> Dict
    def _handle_movement(self, party: Party, area: Area, dungeon) -> List[Dict]
    def _handle_encounter(self, party: Party, area: Area) -> List[Dict]
    def _handle_discovery(self, party: Party, area: Area) -> List[Dict]
```

**API Endpoints Needed**:
- `POST /parties` - Create party
- `POST /parties/{id}/advance` - Progress adventure
- `GET /parties/{id}/status` - Get current state
- `WebSocket` - Real-time adventure events

#### 2. AI Dialogue System (`ai_dialogue.py`)
**Location**: `DialogueSystem` class

**Why Backend**:
- OpenAI API key security
- Consistent character personality across sessions
- Rate limiting and cost control
- Context management for better responses

**Code to Keep**:
```python
class DialogueSystem:
    def generate_character_response(self, character, context, response_type, other_characters)
    def generate_group_dialogue(self, characters, context, situation_type)
    def generate_area_reaction(self, character, area, is_first_visit)
```

**API Endpoints Needed**:
- `POST /chat/ai-response` - Generate AI responses
- `POST /dialogue/group` - Group conversations
- `POST /dialogue/area-reaction` - Location-based reactions

#### 3. World and Dungeon System (`world.py`)
**Location**: `WorldManager`, `Dungeon`, `Area` classes

**Why Backend**:
- Procedural generation needs to be consistent
- Area connections and navigation logic
- Encounter spawn rates and balancing
- World state persistence

**Code to Keep**:
```python
class WorldManager:
    def get_current_dungeon(self) -> Dungeon
    def change_dungeon(self, dungeon_name: str) -> bool
    def list_dungeons(self) -> List[str]

class Dungeon:
    def get_available_moves(self) -> List[str]
    def move_to_area(self, area_name: str) -> bool
    def get_current_area(self) -> Area
```

**API Endpoints Needed**:
- `GET /world/dungeons` - List available dungeons
- `GET /world/dungeons/{id}/areas` - Get dungeon layout
- `GET /world/current-location` - Current party location

#### 4. Character Management Core (`character.py`)
**Location**: `CharacterManager` persistence and validation

**Why Backend**:
- Data validation and business rules
- Character uniqueness constraints
- Stat calculations and leveling
- Inventory management with validation

**Code to Keep**:
```python
class CharacterManager:
    def create_character(self, name, character_class, background, personality) -> Character
    def save_characters(self)
    def load_characters(self)
    def _validate_character_data(self, data) -> bool  # New validation method
```

**Refactor Needed**:
- Extract validation logic into separate methods
- Add database persistence layer
- Create REST API endpoints

#### 5. Items and Equipment (`items.py`)
**Location**: All item generation and management logic

**Why Backend**:
- Item generation algorithms
- Equipment stat calculations
- Inventory management validation
- Drop rate calculations

**Code to Keep**: Entire file, but refactor for API access

### Frontend Logic (Move to JavaScript)

#### 1. User Interface (`pub_interface.py`, `spectator.py`, `main.py`)
**Current Location**: All UI-related classes

**Why Frontend**:
- Better user experience with rich UI
- Real-time updates and interactivity
- Input validation and form handling
- State management for UI flows

**Code to Convert**:

##### Character Creation UI
```python
# Current: pub_interface.py _character_creation_menu()
def _character_creation_menu(self):
    # Input collection logic
    # Class/background selection
    # Personality selection
```

**Convert to**: React component with form validation
```typescript
// New: CharacterCreator.tsx
interface CharacterForm {
  name: string;
  characterClass: string;
  background: string;
  personality: string;
}

const CharacterCreator: React.FC = () => {
  const [form, setForm] = useState<CharacterForm>({});
  const [errors, setErrors] = useState({});
  
  const handleSubmit = async (data: CharacterForm) => {
    const response = await api.post('/characters', data);
    // Handle response
  };
};
```

##### Chat Interface
```python
# Current: pub_interface.py _chat_with_patrons()
def _chat_with_patrons(self):
    # Character selection
    # Conversation flow
    # AI response display
```

**Convert to**: Real-time chat component
```typescript
// New: ChatInterface.tsx
const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character>();
  
  useEffect(() => {
    // WebSocket connection for real-time messages
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'chat_message') {
        setMessages(prev => [...prev, message.data]);
      }
    };
  }, []);
};
```

##### Quest Board Display
```python
# Current: pub_interface.py _quest_board()
def _quest_board(self):
    # Display available characters
    # Show dungeons
    # Party creation
```

**Convert to**: Interactive quest board
```typescript
// New: QuestBoard.tsx
const QuestBoard: React.FC = () => {
  const [quests, setQuests] = useState<Quest[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedQuest, setSelectedQuest] = useState<Quest>();
  
  const createParty = async (questId: string, characterIds: string[]) => {
    const response = await api.post('/parties', {
      quest_id: questId,
      character_ids: characterIds
    });
  };
};
```

##### Spectator Interface
```python
# Current: spectator.py SpectatorInterface
class SpectatorInterface:
    def _watch_party(self, party_name: str)
    def _display_log_entry(self, entry)
    def _handle_command(self, command: str)
```

**Convert to**: Real-time spectator dashboard
```typescript
// New: SpectatorView.tsx
const SpectatorView: React.FC = () => {
  const [parties, setParties] = useState<Party[]>([]);
  const [selectedParty, setSelectedParty] = useState<Party>();
  const [adventureLog, setAdventureLog] = useState<LogEntry[]>([]);
  
  useEffect(() => {
    // WebSocket for real-time adventure events
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'adventure_event') {
        setAdventureLog(prev => [...prev, message.data]);
      }
    };
  }, [selectedParty]);
};
```

### Shared/Converted Logic

#### 1. Data Models (Convert to TypeScript)
**Current**: Python dataclasses and Pydantic models
**New**: TypeScript interfaces and Zod schemas

```python
# Current: character.py
@dataclass
class Character:
    name: str
    character_class: str
    background: str
    personality: str
```

```typescript
// New: types/Character.ts
export interface Character {
  id: string;
  name: string;
  characterClass: string;
  background: string;
  personality: string;
  level: number;
  experience: number;
  stats: CharacterStats;
  inventory: Item[];
  createdAt: string;
  updatedAt: string;
}

// Validation schema
import { z } from 'zod';
export const CharacterSchema = z.object({
  name: z.string().min(1).max(50),
  characterClass: z.enum(['Warrior', 'Mage', 'Rogue', 'Cleric']),
  background: z.string(),
  personality: z.string()
});
```

#### 2. Configuration (Share between systems)
**Current**: `config.py` with Python constants
**New**: JSON config file consumed by both frontend and backend

```python
# Current: config.py
CHARACTER_CLASSES = ["Warrior", "Mage", "Rogue", "Cleric", "Paladin", "Archer", "Bard", "Druid"]
CHARACTER_BACKGROUNDS = ["Noble", "Criminal", "Folk Hero", "Sage", "Soldier", "Hermit", "Entertainer", "Outlander"]
```

```json
// New: shared/config.json
{
  "characterClasses": [
    {
      "id": "warrior",
      "name": "Warrior", 
      "description": "A master of weapons and armor",
      "primaryStat": "strength"
    }
  ],
  "characterBackgrounds": [
    {
      "id": "noble",
      "name": "Noble",
      "description": "Born to privilege and power"
    }
  ]
}
```

## Migration Strategy

### Phase 1: API Foundation
1. **Create FastAPI backend** with core endpoints
2. **Keep existing terminal interface** functional
3. **Add database layer** for persistence
4. **Implement WebSocket** for real-time features

### Phase 2: Frontend Components
1. **Build React app** with basic routing
2. **Create character creation** component
3. **Implement chat interface** with WebSocket
4. **Add quest board** display

### Phase 3: Advanced Features
1. **Real-time spectator mode** with live updates
2. **Party management** interface
3. **Inventory and equipment** management
4. **Adventure progression** visualization

### Phase 4: Full Migration
1. **Feature parity** between terminal and web UI
2. **Performance optimization** and caching
3. **Testing and validation** of all features
4. **Gradual deprecation** of terminal interface

## Refactoring Guidelines

### Backend Refactoring
1. **Separate business logic** from UI code
2. **Add input validation** for all public methods
3. **Create service layer** for complex operations
4. **Implement proper error handling** with meaningful messages
5. **Add logging** for debugging and monitoring

### Frontend Architecture
1. **Component-based design** with clear separation of concerns
2. **State management** with Zustand or Redux
3. **API client layer** with error handling and retries
4. **Real-time updates** with WebSocket management
5. **Responsive design** for multiple screen sizes

### Data Flow
1. **Frontend sends requests** to REST API
2. **Backend processes** and validates data
3. **WebSocket events** for real-time updates
4. **State synchronization** between multiple clients
5. **Optimistic updates** for better UX

This mapping ensures a clean separation of concerns while maintaining the core game experience and adding modern web capabilities.