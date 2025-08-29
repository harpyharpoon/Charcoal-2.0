# Charcoal 2.0 REST API Design

## API Overview

This document defines the REST API endpoints for Charcoal 2.0, enabling a JavaScript frontend to interact with the Python backend for character creation, chat messaging, gear management, and quest board functionality.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: JWT Bearer tokens (for multi-user features)

**Content-Type**: `application/json`

## 1. Character Management

### Create Character
- **Endpoint**: `POST /characters`
- **Description**: Create a new character
- **Request Body**:
```json
{
  "name": "Aragorn",
  "character_class": "Ranger",
  "background": "Outlander",
  "personality": "brave"
}
```
- **Response** (201 Created):
```json
{
  "id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "name": "Aragorn",
  "character_class": "Ranger", 
  "background": "Outlander",
  "personality": "brave",
  "level": 1,
  "experience": 0,
  "stats": {
    "hp": 100,
    "max_hp": 100,
    "strength": 15,
    "dexterity": 12,
    "intelligence": 10
  },
  "inventory": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get All Characters
- **Endpoint**: `GET /characters`
- **Description**: Retrieve all characters
- **Query Parameters**:
  - `limit` (optional): Number of characters to return (default: 50)
  - `offset` (optional): Number of characters to skip (default: 0)
- **Response** (200 OK):
```json
{
  "characters": [
    {
      "id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Aragorn",
      "character_class": "Ranger",
      "personality": "brave",
      "level": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Get Character by ID
- **Endpoint**: `GET /characters/{character_id}`
- **Description**: Retrieve a specific character
- **Response** (200 OK): Same as Create Character response

### Update Character
- **Endpoint**: `PUT /characters/{character_id}`
- **Description**: Update character details
- **Request Body**: Same as Create Character (partial updates allowed)
- **Response** (200 OK): Updated character object

### Delete Character
- **Endpoint**: `DELETE /characters/{character_id}`
- **Description**: Remove a character
- **Response** (204 No Content)

## 2. Chat System

### Send Message
- **Endpoint**: `POST /chat/messages`
- **Description**: Send a chat message
- **Request Body**:
```json
{
  "character_id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message": "Greetings, fellow adventurers!",
  "chat_type": "pub"
}
```
- **Response** (201 Created):
```json
{
  "id": "msg_123e4567-e89b-12d3-a456-426614174000",
  "character_id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "character_name": "Aragorn",
  "message": "Greetings, fellow adventurers!",
  "chat_type": "pub",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Get Chat History
- **Endpoint**: `GET /chat/messages`
- **Description**: Retrieve chat message history
- **Query Parameters**:
  - `chat_type` (optional): Filter by chat type ("pub", "party", "whisper")
  - `character_id` (optional): Filter by character
  - `limit` (optional): Number of messages (default: 100)
  - `before` (optional): Messages before timestamp
- **Response** (200 OK):
```json
{
  "messages": [
    {
      "id": "msg_123e4567-e89b-12d3-a456-426614174000",
      "character_name": "Aragorn",
      "message": "Greetings, fellow adventurers!",
      "chat_type": "pub",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Generate AI Response
- **Endpoint**: `POST /chat/ai-response`
- **Description**: Generate AI response for character conversation
- **Request Body**:
```json
{
  "character_id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "context": "You are in a cozy pub. A patron greets you.",
  "prompt": "Hello there!",
  "conversation_type": "greeting"
}
```
- **Response** (200 OK):
```json
{
  "response": "Well met, friend! *raises mug* Come, sit by the fire and share your tales!",
  "character_name": "Aragorn"
}
```

## 3. Gear and Items

### Get Character Inventory
- **Endpoint**: `GET /characters/{character_id}/inventory`
- **Description**: Get character's current inventory
- **Response** (200 OK):
```json
{
  "character_id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "inventory": [
    {
      "id": "item_sword_123",
      "name": "Iron Sword",
      "type": "weapon",
      "rarity": "common",
      "stats": {
        "damage": 10,
        "durability": 100
      },
      "equipped": true,
      "quantity": 1
    }
  ],
  "total_items": 1,
  "carrying_capacity": "15/50"
}
```

### Equip Item
- **Endpoint**: `POST /characters/{character_id}/equip`
- **Description**: Equip an item to a character
- **Request Body**:
```json
{
  "item_id": "item_sword_123",
  "slot": "main_hand"
}
```
- **Response** (200 OK):
```json
{
  "success": true,
  "message": "Iron Sword equipped to main_hand",
  "previous_item": null
}
```

### Get Available Items
- **Endpoint**: `GET /items`
- **Description**: Get list of all available items
- **Query Parameters**:
  - `type` (optional): Filter by item type ("weapon", "armor", "consumable")
  - `rarity` (optional): Filter by rarity
- **Response** (200 OK):
```json
{
  "items": [
    {
      "id": "item_sword_123",
      "name": "Iron Sword",
      "type": "weapon",
      "rarity": "common",
      "description": "A sturdy iron blade, reliable in combat",
      "stats": {
        "damage": 10,
        "durability": 100
      },
      "requirements": {
        "level": 1,
        "class": ["Warrior", "Ranger"]
      }
    }
  ]
}
```

## 4. Quest Board Management

### Get Available Quests
- **Endpoint**: `GET /quests`
- **Description**: Get list of available quests
- **Query Parameters**:
  - `difficulty` (optional): Filter by difficulty ("easy", "medium", "hard")
  - `status` (optional): Filter by status ("available", "in_progress", "completed")
- **Response** (200 OK):
```json
{
  "quests": [
    {
      "id": "quest_ancient_temple",
      "title": "Explore the Ancient Temple",
      "description": "Venture into the mysterious temple ruins and uncover its secrets",
      "difficulty": "medium",
      "requirements": {
        "min_level": 3,
        "party_size": "3-4",
        "estimated_duration": "2-3 hours"
      },
      "rewards": {
        "experience": 500,
        "gold": 200,
        "items": ["Ancient Artifact"]
      },
      "location": "Ancient Temple Ruins",
      "status": "available",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Party for Quest
- **Endpoint**: `POST /parties`
- **Description**: Create a new party for a quest
- **Request Body**:
```json
{
  "name": "Temple Explorers",
  "quest_id": "quest_ancient_temple",
  "character_ids": [
    "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "char_987fbc97-4bed-5078-9f07-9141ba07c9f3"
  ],
  "leader_id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```
- **Response** (201 Created):
```json
{
  "id": "party_550e8400-e29b-41d4-a716-446655440000",
  "name": "Temple Explorers",
  "quest_id": "quest_ancient_temple",
  "characters": [
    {
      "id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Aragorn",
      "character_class": "Ranger",
      "role": "leader"
    }
  ],
  "status": "forming",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Start Adventure
- **Endpoint**: `POST /parties/{party_id}/start-adventure`
- **Description**: Begin the party's adventure
- **Response** (200 OK):
```json
{
  "success": true,
  "party_id": "party_550e8400-e29b-41d4-a716-446655440000",
  "current_location": "Temple Entrance",
  "status": "active",
  "adventure_log": [
    {
      "type": "narrative",
      "content": "The party approaches the ancient temple entrance...",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Party Status
- **Endpoint**: `GET /parties/{party_id}`
- **Description**: Get current party status and adventure progress
- **Response** (200 OK):
```json
{
  "id": "party_550e8400-e29b-41d4-a716-446655440000",
  "name": "Temple Explorers",
  "status": "active",
  "current_location": "Temple Chamber",
  "characters": [
    {
      "id": "char_f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Aragorn",
      "health": "85/100",
      "status": "alive"
    }
  ],
  "statistics": {
    "areas_discovered": 3,
    "experience_gained": 150,
    "items_found": 2,
    "encounters_faced": 1
  },
  "recent_events": [
    {
      "type": "dialogue",
      "character": "Aragorn",
      "content": "These halls hold ancient secrets...",
      "timestamp": "2024-01-01T00:01:00Z"
    }
  ]
}
```

## 5. WebSocket Events

For real-time features, use WebSocket connections to:

### Connection
- **URL**: `ws://localhost:8000/ws`
- **Authentication**: Send JWT token after connection

### Event Types

#### Chat Messages
```json
{
  "type": "chat_message",
  "data": {
    "character_name": "Aragorn",
    "message": "Hello everyone!",
    "chat_type": "pub",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### Adventure Events
```json
{
  "type": "adventure_event",
  "party_id": "party_550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "event_type": "encounter",
    "content": "A stone guardian blocks the path!",
    "location": "Temple Chamber",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### Party Updates
```json
{
  "type": "party_update",
  "party_id": "party_550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "status": "in_combat",
    "location": "Temple Chamber",
    "characters": [
      {
        "name": "Aragorn",
        "health": "80/100"
      }
    ]
  }
}
```

## 6. Error Responses

All endpoints return consistent error formats:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Character name is required",
    "details": {
      "field": "name",
      "issue": "missing_required_field"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request (validation error)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict (duplicate resource)
- `500`: Internal Server Error

## 7. Rate Limiting

- **Chat messages**: 10 per minute per character
- **Character creation**: 5 per hour per user
- **API calls**: 1000 per hour per user
- **WebSocket connections**: 5 concurrent per user