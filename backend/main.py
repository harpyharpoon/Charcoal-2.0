import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime
import asyncio

# Import from legacy code
from character import CharacterManager
from ai_dialogue import AIDialogueSystem
from items import ItemGenerator, Item, ItemType, ItemRarity

app = FastAPI(title="Charcoal 2.0 API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
character_manager = CharacterManager()
dialogue_system = AIDialogueSystem()
item_generator = ItemGenerator()

# In-memory storage for chat messages (in production, use database)
chat_messages: List[Dict] = []

# In-memory character inventories (in production, use database)
character_inventories: Dict[str, List[Dict]] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if self.active_connections:
            print(f"Broadcasting to {len(self.active_connections)} connections: {message['type']}")
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Failed to send message to connection: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

# Pydantic models
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
    created_at: str

class ChatMessage(BaseModel):
    character_id: str
    message: str
    chat_type: str = "pub"

class ChatMessageResponse(BaseModel):
    id: str
    character_id: str
    character_name: str
    message: str
    chat_type: str
    timestamp: str

class AIResponseRequest(BaseModel):
    character_id: str
    context: str
    prompt: str
    conversation_type: str = "conversation"

class InventoryItem(BaseModel):
    id: str
    name: str
    description: str
    item_type: str
    rarity: str
    stats: Dict
    value: int
    equipped: bool = False
    quantity: int = 1

# API Routes
@app.get("/")
async def root():
    return {"message": "Charcoal 2.0 API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Character Management
@app.post("/api/v1/characters", response_model=CharacterResponse)
async def create_character(character: CharacterCreate):
    try:
        char = character_manager.create_character(
            character.name,
            character.character_class,
            character.background,
            character.personality
        )
        
        response = CharacterResponse(
            id=str(uuid.uuid4()),
            name=char.name,
            character_class=char.character_class,
            background=char.background,
            personality=char.personality,
            created_at=datetime.utcnow().isoformat()
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/characters")
async def get_characters():
    try:
        characters = character_manager.list_characters()
        return {
            "characters": [
                {
                    "id": str(uuid.uuid4()),
                    "name": char.name,
                    "character_class": char.character_class,
                    "background": char.background,
                    "personality": char.personality,
                    "created_at": datetime.utcnow().isoformat()
                }
                for char in characters
            ],
            "total": len(characters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat System
@app.post("/api/v1/chat/messages", response_model=ChatMessageResponse)
async def send_message(message: ChatMessage):
    try:
        # Find character
        characters = character_manager.list_characters()
        character = None
        for char in characters:
            if str(char.name) == message.character_id or char.name == message.character_id:
                character = char
                break
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Create message record
        message_record = {
            "id": str(uuid.uuid4()),
            "character_id": message.character_id,
            "character_name": character.name,
            "message": message.message,
            "chat_type": message.chat_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store message
        chat_messages.append(message_record)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "chat_message",
            "data": message_record
        })
        
        return ChatMessageResponse(**message_record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/chat/messages")
async def get_chat_history(limit: int = 50, chat_type: Optional[str] = None):
    try:
        filtered_messages = chat_messages
        if chat_type:
            filtered_messages = [msg for msg in chat_messages if msg["chat_type"] == chat_type]
        
        # Return most recent messages
        recent_messages = filtered_messages[-limit:] if limit else filtered_messages
        
        return {
            "messages": recent_messages,
            "total": len(recent_messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/ai-response")
async def generate_ai_response(request: AIResponseRequest):
    try:
        # Find character
        characters = character_manager.list_characters()
        character = None
        for char in characters:
            if str(char.name) == request.character_id or char.name == request.character_id:
                character = char
                break
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Generate AI response
        response = dialogue_system.generate_character_response(
            character,
            request.context,
            request.conversation_type,
            []
        )
        
        return {
            "response": response,
            "character_name": character.name,
            "character_id": request.character_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inventory Management
@app.get("/api/v1/characters/{character_id}/inventory")
async def get_character_inventory(character_id: str):
    try:
        # Find character
        characters = character_manager.list_characters()
        character = None
        for char in characters:
            if str(char.name) == character_id or char.name == character_id:
                character = char
                break
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get or create inventory
        if character_id not in character_inventories:
            # Create starter inventory
            starter_items = []
            # Add a basic weapon based on class
            if character.character_class.lower() in ["warrior", "paladin"]:
                item = item_generator.generate_item(ItemType.WEAPON, ItemRarity.COMMON)
            elif character.character_class.lower() in ["mage", "druid"]:
                item = item_generator.generate_item(ItemType.WEAPON, ItemRarity.COMMON)  # Staff
            else:
                item = item_generator.generate_item(ItemType.WEAPON, ItemRarity.COMMON)
            
            starter_items.append({
                "id": str(uuid.uuid4()),
                "name": item.name,
                "description": item.description,
                "item_type": item.item_type.value,
                "rarity": item.rarity.value,
                "stats": {
                    "attack": item.stats.attack,
                    "defense": item.stats.defense,
                    "magic_power": item.stats.magic_power,
                    "health": item.stats.health,
                    "special_effect": item.stats.special_effect
                },
                "value": item.value,
                "equipped": True,
                "quantity": 1
            })
            
            # Add some basic armor
            armor = item_generator.generate_item(ItemType.ARMOR, ItemRarity.COMMON)
            starter_items.append({
                "id": str(uuid.uuid4()),
                "name": armor.name,
                "description": armor.description,
                "item_type": armor.item_type.value,
                "rarity": armor.rarity.value,
                "stats": {
                    "attack": armor.stats.attack,
                    "defense": armor.stats.defense,
                    "magic_power": armor.stats.magic_power,
                    "health": armor.stats.health,
                    "special_effect": armor.stats.special_effect
                },
                "value": armor.value,
                "equipped": True,
                "quantity": 1
            })
            
            character_inventories[character_id] = starter_items
        
        inventory = character_inventories.get(character_id, [])
        
        return {
            "character_id": character_id,
            "character_name": character.name,
            "inventory": inventory,
            "total_items": len(inventory),
            "carrying_capacity": f"{len(inventory)}/50"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/characters/{character_id}/inventory/equip")
async def equip_item(character_id: str, request: dict):
    try:
        item_id = request.get("item_id")
        if not item_id:
            raise HTTPException(status_code=400, detail="item_id is required")
        
        inventory = character_inventories.get(character_id, [])
        
        # Find the item
        item_to_equip = None
        for item in inventory:
            if item["id"] == item_id:
                item_to_equip = item
                break
        
        if not item_to_equip:
            raise HTTPException(status_code=404, detail="Item not found in inventory")
        
        # Unequip other items of the same type (simplified equipment system)
        item_type = item_to_equip["item_type"]
        for item in inventory:
            if item["item_type"] == item_type and item["id"] != item_id:
                item["equipped"] = False
        
        # Equip the item
        item_to_equip["equipped"] = True
        
        return {
            "success": True,
            "message": f"{item_to_equip['name']} equipped",
            "item": item_to_equip
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/characters/{character_id}/stats")
async def get_character_stats(character_id: str):
    try:
        # Find character
        characters = character_manager.list_characters()
        character = None
        for char in characters:
            if str(char.name) == character_id or char.name == character_id:
                character = char
                break
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Calculate stats including equipment bonuses
        base_stats = {
            "hp": character.hp,
            "max_hp": 100,
            "level": character.level,
            "experience": character.experience,
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "constitution": 10
        }
        
        # Add equipment bonuses
        inventory = character_inventories.get(character_id, [])
        equipment_bonuses = {
            "attack": 0,
            "defense": 0,
            "magic_power": 0,
            "health": 0
        }
        
        equipped_items = []
        for item in inventory:
            if item.get("equipped", False):
                equipped_items.append(item)
                stats = item.get("stats", {})
                equipment_bonuses["attack"] += stats.get("attack", 0)
                equipment_bonuses["defense"] += stats.get("defense", 0)
                equipment_bonuses["magic_power"] += stats.get("magic_power", 0)
                equipment_bonuses["health"] += stats.get("health", 0)
        
        return {
            "character_id": character_id,
            "character_name": character.name,
            "character_class": character.character_class,
            "background": character.background,
            "personality": character.personality,
            "base_stats": base_stats,
            "equipment_bonuses": equipment_bonuses,
            "equipped_items": equipped_items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                print(f"Received WebSocket message: {message}")
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "chat_message":
                    # Handle chat message via WebSocket
                    chat_data = message.get("data", {})
                    chat_message = ChatMessage(**chat_data)
                    response = await send_message(chat_message)
                    # Response already broadcasted in send_message
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "message": "Invalid JSON"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "message": str(e)
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)