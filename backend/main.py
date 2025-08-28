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

# In-memory storage for chat messages (in production, use database)
chat_messages: List[Dict] = []

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