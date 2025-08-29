# Charcoal 2.0 Architecture Separation Plan

## 1. High-Level Architecture

### Current State (Monolithic)
```
┌─────────────────────────────────────┐
│           Python Application        │
├─────────────────────────────────────┤
│ Terminal UI (colorama)              │
│ ├─ main.py (menu system)           │
│ ├─ pub_interface.py (character UI)  │
│ └─ spectator.py (adventure viewer)  │
├─────────────────────────────────────┤
│ Game Logic                          │
│ ├─ character.py (management)        │
│ ├─ party.py (adventure logic)       │
│ ├─ world.py (dungeons/areas)        │
│ ├─ ai_dialogue.py (AI system)       │
│ └─ items.py (equipment)             │
├─────────────────────────────────────┤
│ Data Layer                          │
│ ├─ characters.json                  │
│ └─ In-memory state                  │
└─────────────────────────────────────┘
```

### Target State (Separated)
```
┌─────────────────────┐     ┌─────────────────────┐
│  JavaScript Frontend│     │   Python Backend    │
├─────────────────────┤     ├─────────────────────┤
│ React/Vue.js App    │     │ FastAPI/Flask API   │
│ ├─ Character Creator│     │ ├─ Character Mgmt   │
│ ├─ Chat Interface   │◄────┤ ├─ Chat System      │
│ ├─ Quest Board      │     │ ├─ Quest Logic      │
│ ├─ Spectator View   │     │ ├─ Party Adventures │
│ └─ Real-time Updates│     │ └─ AI Dialogue      │
├─────────────────────┤     ├─────────────────────┤
│ HTTP Client         │     │ RESTful API         │
│ WebSocket Client    │     │ WebSocket Server    │
└─────────────────────┘     └─────────────────────┘
                                      │
                            ┌─────────────────────┐
                            │   Data Layer        │
                            ├─────────────────────┤
                            │ PostgreSQL/SQLite   │
                            │ Redis (sessions)    │
                            │ File Storage        │
                            └─────────────────────┘
```

## 2. Recommended Technology Stack

### Backend (Python)
- **API Framework**: FastAPI (modern, async, auto-docs)
- **WebSocket**: FastAPI WebSocket support for real-time updates
- **Database**: SQLite (development) → PostgreSQL (production)
- **Cache**: Redis for session management and real-time data
- **AI Integration**: Keep existing OpenAI integration
- **Authentication**: JWT tokens for session management

### Frontend (JavaScript)
- **Framework**: React with Vite (fast development, component-based)
- **State Management**: Zustand or Redux Toolkit
- **HTTP Client**: Axios or Fetch API
- **WebSocket**: Native WebSocket API or Socket.io client
- **UI Library**: Tailwind CSS + Headless UI for styling
- **Real-time**: WebSocket for live adventure updates

### Communication Patterns
- **REST API**: For CRUD operations (characters, quests, items)
- **WebSocket**: For real-time features (chat, live adventures, spectator mode)
- **HTTP Polling**: Fallback for environments without WebSocket support

## 3. Data Exchange Patterns

### Character Creation
```typescript
// Frontend Request
POST /api/characters
{
  "name": "Aragorn",
  "class": "Ranger",
  "background": "Outlander", 
  "personality": "brave"
}

// Backend Response
{
  "id": "char-123",
  "name": "Aragorn",
  "class": "Ranger",
  "background": "Outlander",
  "personality": "brave",
  "stats": { "hp": 100, "level": 1 },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Chat Messaging
```typescript
// WebSocket Message (Pub Chat)
{
  "type": "chat_message",
  "data": {
    "character_id": "char-123",
    "character_name": "Aragorn", 
    "message": "Greetings, fellow adventurers!",
    "timestamp": "2024-01-01T00:00:00Z",
    "chat_type": "pub"
  }
}
```

### Quest Board Updates
```typescript
// REST API
GET /api/quests/available
{
  "quests": [
    {
      "id": "quest-456",
      "title": "Explore Ancient Temple",
      "description": "Venture into the mysterious temple ruins",
      "difficulty": "medium",
      "party_size": "3-4",
      "estimated_duration": "2-3 hours"
    }
  ]
}
```

### Real-time Adventure Events
```typescript
// WebSocket Stream
{
  "type": "adventure_event",
  "party_id": "party-789", 
  "data": {
    "event_type": "dialogue",
    "character": "Legolas",
    "content": "I sense something ancient in these halls...",
    "location": "Temple Entrance",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## 4. Key Architectural Benefits

### Scalability
- Backend can handle multiple concurrent users
- Frontend can be deployed to CDN
- Database can be optimized independently
- WebSocket server can be horizontally scaled

### Development
- Frontend and backend teams can work independently
- Hot reload and fast iteration on UI
- API-first development enables mobile apps later
- Easier testing with separated concerns

### User Experience
- Rich interactive UI instead of terminal interface
- Real-time updates without polling
- Multiple simultaneous users can spectate
- Responsive design for different screen sizes

### Deployment
- Frontend: Static files → CDN/Netlify/Vercel
- Backend: Container → Cloud Run/Heroku/AWS
- Database: Managed service (PostgreSQL)
- Separate scaling of frontend vs backend

## 5. Migration Considerations

### Backward Compatibility
- Keep existing terminal interface during transition
- Gradual feature migration to web interface
- API can serve both old CLI and new web frontend

### Data Migration
- Export existing character.json to database
- Preserve existing game state and progress
- Maintain AI dialogue system compatibility

### Feature Parity
- Ensure all terminal features work in web UI
- Maintain the core game experience
- Add enhanced features (real-time spectating, multi-user)

### Rollout Strategy
1. Build API alongside existing code
2. Create web frontend with basic features
3. Migrate features one by one
4. Add real-time and multi-user capabilities
5. Eventually deprecate terminal interface