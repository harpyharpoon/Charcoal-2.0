# Incremental Migration Plan

## Overview

This document outlines a step-by-step migration plan to convert Charcoal 2.0 from a monolithic Python terminal application into a modern Python backend with JavaScript frontend architecture, prioritizing minimal downtime and incremental refactoring.

## Migration Principles

- **Zero Downtime**: Existing functionality remains available throughout migration
- **Incremental Value**: Each phase delivers working features 
- **Backward Compatible**: Old terminal interface coexists with new web interface
- **Risk Mitigation**: Small, testable changes with easy rollback
- **User Choice**: Users can choose between terminal and web interfaces

## Phase 1: Foundation Setup (Week 1-2)

### Objectives
- Set up development infrastructure
- Create API backbone without disrupting existing functionality
- Establish database layer
- Basic deployment pipeline

### Tasks

#### 1.1 Project Structure Setup
```
charcoal-2.0/
├── backend/           # New API server
│   ├── api/
│   ├── models/
│   ├── services/
│   └── main.py
├── frontend/          # New React app  
│   ├── src/
│   ├── public/
│   └── package.json
├── shared/            # Common configuration
├── docs/             # Architecture docs
└── legacy/           # Current terminal app (renamed)
    ├── main.py
    ├── character.py
    └── ...
```

**Implementation Steps**:
1. Create `backend/` directory structure
2. Move existing files to `legacy/` folder
3. Set up FastAPI project with basic structure
4. Create `frontend/` with Vite + React
5. Add Docker configuration for both services

#### 1.2 Database Layer
**Goal**: Replace JSON file storage with proper database

```python
# backend/models/database.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    character_class = Column(String, nullable=False)
    background = Column(String, nullable=False)
    personality = Column(String, nullable=False)
    # ... other fields
```

**Migration Script**:
```python
# scripts/migrate_data.py
def migrate_characters_from_json():
    """Migrate existing characters.json to database"""
    with open('legacy/characters.json') as f:
        characters = json.load(f)
    
    for char_data in characters:
        character = Character(**char_data)
        session.add(character)
    session.commit()
```

#### 1.3 Basic API Server
**Goal**: Create minimal API that can serve existing data

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Charcoal 2.0 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/characters")
async def get_characters():
    # Return data from database
    pass
```

**Validation Criteria**:
- [ ] API server starts successfully
- [ ] Database connection established
- [ ] Character data migrated from JSON
- [ ] Basic endpoints return expected data
- [ ] CORS configured for frontend development

**Rollback Plan**: 
- Keep `legacy/` folder functional
- Database migration is additive only
- API server can be stopped without affecting terminal app

---

## Phase 2: Character Management API (Week 3)

### Objectives
- Implement complete character CRUD API
- Create basic frontend components
- Establish API testing patterns

### Tasks

#### 2.1 Character API Implementation
```python
# backend/api/characters.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/characters")

class CharacterCreate(BaseModel):
    name: str
    character_class: str
    background: str
    personality: str

class CharacterResponse(BaseModel):
    id: str
    name: str
    character_class: str
    background: str
    personality: str
    created_at: datetime

@router.post("/", response_model=CharacterResponse)
async def create_character(character: CharacterCreate):
    # Reuse existing CharacterManager logic
    from legacy.character import CharacterManager
    manager = CharacterManager()
    char = manager.create_character(
        character.name,
        character.character_class, 
        character.background,
        character.personality
    )
    # Save to database and return
```

#### 2.2 Frontend Character Components
```typescript
// frontend/src/components/CharacterCreator.tsx
import { useState } from 'react';
import { api } from '../services/api';

interface CharacterForm {
  name: string;
  characterClass: string;
  background: string;
  personality: string;
}

export const CharacterCreator = () => {
  const [form, setForm] = useState<CharacterForm>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const character = await api.characters.create(form);
      // Handle success
    } catch (error) {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

#### 2.3 Integration Bridge
**Goal**: Allow terminal app to use new API during transition

```python
# legacy/api_bridge.py
import requests
from typing import Optional

class APIBridge:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.fallback_to_local = True

    def create_character(self, name, character_class, background, personality):
        try:
            response = requests.post(f"{self.base_url}/api/v1/characters", json={
                "name": name,
                "character_class": character_class,
                "background": background,
                "personality": personality
            })
            return response.json()
        except requests.RequestException:
            if self.fallback_to_local:
                # Fall back to original CharacterManager
                from character import CharacterManager
                manager = CharacterManager()
                return manager.create_character(name, character_class, background, personality)
            raise
```

**Validation Criteria**:
- [ ] All character CRUD operations work via API
- [ ] Frontend can create and display characters
- [ ] Terminal app can optionally use API
- [ ] Data consistency between database and legacy JSON
- [ ] API documentation auto-generated with FastAPI

**Risk Mitigation**:
- API bridge allows graceful fallback to local storage
- Terminal app continues to work independently
- Database migrations are reversible

---

## Phase 3: Chat System (Week 4)

### Objectives  
- Implement real-time chat with WebSocket
- Convert pub chat interface to web
- Establish AI dialogue API integration

### Tasks

#### 3.1 WebSocket Infrastructure
```python
# backend/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_websocket_message(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### 3.2 Chat API Endpoints
```python
# backend/api/chat.py
@router.post("/messages")
async def send_message(message: ChatMessage):
    # Save to database
    saved_message = await save_chat_message(message)
    
    # Broadcast to all connected clients
    await manager.broadcast({
        "type": "chat_message",
        "data": {
            "character_name": saved_message.character_name,
            "message": saved_message.content,
            "timestamp": saved_message.timestamp.isoformat()
        }
    })
    return saved_message

@router.post("/ai-response")
async def generate_ai_response(request: AIResponseRequest):
    # Reuse existing AI dialogue system
    from legacy.ai_dialogue import DialogueSystem
    dialogue_system = DialogueSystem()
    
    response = dialogue_system.generate_character_response(
        request.character,
        request.context,
        request.response_type,
        []
    )
    return {"response": response}
```

#### 3.3 Real-time Chat Frontend
```typescript
// frontend/src/components/ChatInterface.tsx
import { useWebSocket } from '../hooks/useWebSocket';

export const ChatInterface = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const { sendMessage, connected } = useWebSocket('ws://localhost:8000/ws');

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const message = JSON.parse(event.data);
      if (message.type === 'chat_message') {
        setMessages(prev => [...prev, message.data]);
      }
    };

    if (connected) {
      // WebSocket message handling
    }
  }, [connected]);

  const sendChatMessage = async () => {
    await api.chat.sendMessage({
      character_id: selectedCharacter.id,
      message: currentMessage,
      chat_type: 'pub'
    });
    setCurrentMessage('');
  };

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map(msg => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>
      <ChatInput onSend={sendChatMessage} />
    </div>
  );
};
```

**Validation Criteria**:
- [ ] Real-time chat works between multiple browser tabs
- [ ] AI responses integrate seamlessly
- [ ] Chat history persists in database
- [ ] Terminal chat can interoperate with web chat
- [ ] WebSocket connections handle disconnects gracefully

---

## Phase 4: Quest Board & Party System (Week 5-6)

### Objectives
- Convert quest board to interactive web interface
- Implement party creation and management
- Add real-time party status updates

### Tasks

#### 4.1 Quest and Party APIs
```python
# backend/api/quests.py
@router.get("/")
async def get_available_quests():
    # Use existing world system
    from legacy.world import WorldManager
    world_manager = WorldManager()
    dungeons = world_manager.list_dungeons()
    
    quests = []
    for dungeon_name in dungeons:
        dungeon = world_manager.dungeons[dungeon_name]
        quest = {
            "id": f"quest_{dungeon_name.lower().replace(' ', '_')}",
            "title": f"Explore {dungeon.name}",
            "description": f"Adventure through {dungeon.theme}",
            "location": dungeon.name,
            "difficulty": "medium"
        }
        quests.append(quest)
    return {"quests": quests}

@router.post("/parties")
async def create_party(party_request: PartyCreate):
    # Integrate with existing PartyManager
    from legacy.party import PartyManager
    from legacy.character import CharacterManager
    from legacy.world import WorldManager
    
    party_manager = PartyManager(
        CharacterManager(), 
        WorldManager()
    )
    
    # Create party with selected characters
    party = party_manager.create_party(
        party_request.name,
        party_request.character_ids
    )
    
    return {"party": party.to_dict()}
```

#### 4.2 Interactive Quest Board
```typescript
// frontend/src/components/QuestBoard.tsx
export const QuestBoard = () => {
  const [quests, setQuests] = useState<Quest[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedQuest, setSelectedQuest] = useState<Quest>();
  const [partyMembers, setPartyMembers] = useState<string[]>([]);

  const createParty = async () => {
    const party = await api.parties.create({
      name: `${selectedQuest.title} Party`,
      quest_id: selectedQuest.id,
      character_ids: partyMembers
    });
    
    // Navigate to party view or start adventure
    navigate(`/parties/${party.id}`);
  };

  return (
    <div className="quest-board">
      <QuestList 
        quests={quests}
        selectedQuest={selectedQuest}
        onSelectQuest={setSelectedQuest}
      />
      <CharacterSelector
        characters={characters}
        selectedCharacters={partyMembers}
        onSelectionChange={setPartyMembers}
      />
      <PartyCreator
        quest={selectedQuest}
        members={partyMembers}
        onCreateParty={createParty}
      />
    </div>
  );
};
```

**Validation Criteria**:
- [ ] Quest board displays available adventures
- [ ] Party creation works with character selection
- [ ] Quest requirements validation
- [ ] Seamless transition from terminal quest system

---

## Phase 5: Spectator Mode (Week 7)

### Objectives
- Real-time adventure viewing in web interface
- Multiple spectators can watch same party
- Enhanced visualization compared to terminal

### Tasks

#### 5.1 Adventure Event Streaming
```python
# backend/api/spectator.py
@router.get("/parties/{party_id}/events")
async def get_adventure_events(party_id: str, last_event_id: Optional[str] = None):
    # Get events since last_event_id
    events = await get_party_events(party_id, since=last_event_id)
    return {"events": events}

@router.post("/parties/{party_id}/advance")
async def advance_adventure(party_id: str):
    # Use existing adventure logic
    from legacy.party import PartyManager
    party_manager = PartyManager()
    
    result = party_manager.advance_party_adventure(party_id)
    
    # Broadcast events to spectators
    for event in result.get("events", []):
        await manager.broadcast({
            "type": "adventure_event",
            "party_id": party_id,
            "data": event
        })
    
    return result
```

#### 5.2 Real-time Spectator Interface
```typescript
// frontend/src/components/SpectatorView.tsx
export const SpectatorView = () => {
  const { partyId } = useParams();
  const [adventureLog, setAdventureLog] = useState<AdventureEvent[]>([]);
  const [partyStatus, setPartyStatus] = useState<PartyStatus>();
  const { sendMessage } = useWebSocket('ws://localhost:8000/ws');

  useEffect(() => {
    const handleAdventureEvent = (event: AdventureEvent) => {
      if (event.party_id === partyId) {
        setAdventureLog(prev => [...prev, event.data]);
        updatePartyStatus(event.data);
      }
    };

    // Subscribe to adventure events
    sendMessage({
      type: 'subscribe',
      party_id: partyId
    });
  }, [partyId]);

  const advanceAdventure = async () => {
    await api.parties.advance(partyId);
  };

  return (
    <div className="spectator-view">
      <PartyStatusPanel party={partyStatus} />
      <AdventureLog events={adventureLog} />
      <SpectatorControls onAdvance={advanceAdventure} />
    </div>
  );
};
```

**Validation Criteria**:
- [ ] Multiple users can spectate same party simultaneously
- [ ] Real-time adventure events display correctly
- [ ] Spectator controls work (advance, auto-mode)
- [ ] Adventure log shows rich formatting

---

## Phase 6: Polish & Performance (Week 8)

### Objectives
- Performance optimization
- Error handling and edge cases
- Production deployment preparation
- Documentation completion

### Tasks

#### 6.1 Performance Optimization
- Database query optimization
- WebSocket connection pooling
- Frontend code splitting
- Caching strategy for static data

#### 6.2 Error Handling
```python
# backend/middleware/error_handling.py
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": exc.errors()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

#### 6.3 Production Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
  
  database:
    image: postgres:14
    environment:
      - POSTGRES_DB=charcoal
      - POSTGRES_USER=charcoal
      - POSTGRES_PASSWORD=${DB_PASSWORD}
```

**Validation Criteria**:
- [ ] All features work in production environment
- [ ] Performance meets target metrics
- [ ] Comprehensive error handling
- [ ] Monitoring and logging in place

---

## Potential Pitfalls & Mitigation

### 1. Data Consistency Issues
**Risk**: Discrepancies between terminal and web interfaces
**Mitigation**:
- Single source of truth (database)
- API bridge ensures both interfaces use same data
- Automated tests for data consistency

### 2. WebSocket Connection Management
**Risk**: Dropped connections, memory leaks
**Mitigation**:
- Robust reconnection logic
- Connection cleanup on client disconnect
- Rate limiting and abuse prevention

### 3. AI API Costs
**Risk**: Uncontrolled OpenAI API usage
**Mitigation**:
- Rate limiting per user/character
- Fallback to mock responses
- Usage monitoring and alerts

### 4. Backward Compatibility
**Risk**: Breaking existing terminal interface
**Mitigation**:
- Keep legacy code functional throughout migration
- Gradual deprecation with user communication
- Easy rollback to previous version

### 5. Performance Under Load
**Risk**: System slowdown with multiple users
**Mitigation**:
- Load testing during development
- Database optimization and indexing
- Horizontal scaling preparation

## Success Metrics

### Technical Metrics
- [ ] API response time < 200ms for 95% of requests
- [ ] WebSocket connection uptime > 99%
- [ ] Database query performance optimized
- [ ] Zero data loss during migration

### User Experience Metrics  
- [ ] Feature parity between terminal and web interfaces
- [ ] Real-time updates with < 1 second latency
- [ ] Intuitive UI with minimal learning curve
- [ ] Mobile-responsive design

### Business Metrics
- [ ] Multiple concurrent users supported
- [ ] Scalable architecture for future growth
- [ ] Comprehensive API documentation
- [ ] Easy deployment and maintenance

This migration plan ensures a smooth transition from monolithic to modern architecture while maintaining the core Charcoal 2.0 experience and adding powerful new web capabilities.