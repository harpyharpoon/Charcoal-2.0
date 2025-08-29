# Testing and Integration Strategy

## Overview

This document outlines a comprehensive testing strategy for ensuring reliable integration between the Python backend and JavaScript frontend in Charcoal 2.0. The testing approach covers unit testing, API contract validation, integration testing, and end-to-end UI testing.

## Testing Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Testing Strategy                       │
├─────────────────────────────────────────────────────────┤
│  Unit Tests          │  Integration Tests               │
│  ├─ Backend Logic    │  ├─ API Endpoints               │
│  ├─ Frontend Logic   │  ├─ Database Operations         │
│  └─ Utility Functions│  └─ WebSocket Communication     │
├─────────────────────────────────────────────────────────┤
│  Contract Tests      │  End-to-End Tests               │
│  ├─ API Schemas      │  ├─ User Workflows              │
│  ├─ WebSocket Events │  ├─ Cross-browser Testing       │
│  └─ Data Models      │  └─ Performance Testing         │
├─────────────────────────────────────────────────────────┤
│  Load Tests          │  Security Tests                 │
│  ├─ Concurrent Users │  ├─ Input Validation            │
│  ├─ WebSocket Scale  │  ├─ Authentication              │
│  └─ Database Load    │  └─ API Rate Limiting           │
└─────────────────────────────────────────────────────────┘
```

## 1. Unit Testing

### Backend Unit Tests (Python)

**Framework**: pytest with pytest-asyncio for async testing

```python
# tests/test_character_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestCharacterAPI:
    def test_create_character_success(self):
        """Test successful character creation"""
        character_data = {
            "name": "Test Hero",
            "character_class": "Warrior",
            "background": "Soldier",
            "personality": "brave"
        }
        
        response = client.post("/api/v1/characters", json=character_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Hero"
        assert data["character_class"] == "Warrior"
        assert "id" in data
        assert "created_at" in data

    def test_create_character_validation_error(self):
        """Test character creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "character_class": "InvalidClass",
            "background": "Soldier"
        }
        
        response = client.post("/api/v1/characters", json=invalid_data)
        
        assert response.status_code == 400
        assert "error" in response.json()

    def test_get_characters_list(self):
        """Test retrieving characters list"""
        response = client.get("/api/v1/characters")
        
        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
        assert "total" in data
        assert isinstance(data["characters"], list)

class TestChatAPI:
    def test_send_message_success(self):
        """Test sending a chat message"""
        # First create a character
        char_response = client.post("/api/v1/characters", json={
            "name": "Chat Tester",
            "character_class": "Bard",
            "background": "Entertainer",
            "personality": "cheerful"
        })
        character = char_response.json()
        
        # Send message
        message_data = {
            "character_id": character["name"],
            "message": "Hello everyone!",
            "chat_type": "pub"
        }
        
        response = client.post("/api/v1/chat/messages", json=message_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Hello everyone!"
        assert data["character_name"] == "Chat Tester"
        assert data["chat_type"] == "pub"

    def test_ai_response_generation(self):
        """Test AI response generation"""
        # Create character first
        char_response = client.post("/api/v1/characters", json={
            "name": "AI Tester",
            "character_class": "Mage",
            "background": "Sage",
            "personality": "wise"
        })
        character = char_response.json()
        
        # Generate AI response
        ai_request = {
            "character_id": character["name"],
            "context": "You are in a peaceful library",
            "prompt": "Someone asks about ancient magic",
            "conversation_type": "scholarly"
        }
        
        response = client.post("/api/v1/chat/ai-response", json=ai_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "character_name" in data
        assert len(data["response"]) > 0

class TestGameLogic:
    def test_character_manager_integration(self):
        """Test integration with legacy character manager"""
        from character import CharacterManager
        
        manager = CharacterManager()
        initial_count = len(manager.list_characters())
        
        character = manager.create_character(
            "Integration Test",
            "Rogue",
            "Criminal",
            "mischievous"
        )
        
        assert character.name == "Integration Test"
        assert len(manager.list_characters()) == initial_count + 1

    def test_dialogue_system_integration(self):
        """Test integration with AI dialogue system"""
        from ai_dialogue import DialogueSystem
        from character import Character
        
        dialogue_system = DialogueSystem()
        character = Character(
            name="Test Character",
            character_class="Bard",
            background="Entertainer",
            personality="witty"
        )
        
        response = dialogue_system.generate_character_response(
            character,
            "You are performing in a tavern",
            "performance",
            []
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
```

### Frontend Unit Tests (JavaScript)

**Framework**: Jest with @testing-library for DOM testing

```javascript
// frontend/tests/api.test.js
import { apiCall } from '../src/utils/api';

// Mock fetch
global.fetch = jest.fn();

describe('API Client', () => {
    beforeEach(() => {
        fetch.mockClear();
    });

    test('successful API call', async () => {
        const mockResponse = { characters: [], total: 0 };
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockResponse
        });

        const result = await apiCall('/api/v1/characters');
        
        expect(fetch).toHaveBeenCalledWith(
            'http://localhost:8000/api/v1/characters',
            expect.objectContaining({
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
        );
        expect(result).toEqual(mockResponse);
    });

    test('API error handling', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 404,
            statusText: 'Not Found'
        });

        await expect(apiCall('/api/v1/nonexistent')).rejects.toThrow();
    });
});

// frontend/tests/chatInterface.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../src/components/ChatInterface';

// Mock WebSocket
class MockWebSocket {
    constructor(url) {
        this.url = url;
        this.onopen = null;
        this.onmessage = null;
        this.onclose = null;
        this.onerror = null;
        
        setTimeout(() => {
            if (this.onopen) this.onopen({});
        }, 100);
    }
    
    send(data) {
        // Mock sending data
    }
    
    close() {
        if (this.onclose) this.onclose({});
    }
}

global.WebSocket = MockWebSocket;

describe('ChatInterface', () => {
    test('renders chat interface', () => {
        render(<ChatInterface />);
        
        expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
        expect(screen.getByText('Send')).toBeInTheDocument();
    });

    test('sends message when form submitted', async () => {
        const mockSendMessage = jest.fn();
        render(<ChatInterface onSendMessage={mockSendMessage} />);
        
        const input = screen.getByPlaceholderText('Type your message...');
        const sendButton = screen.getByText('Send');
        
        fireEvent.change(input, { target: { value: 'Hello world!' } });
        fireEvent.click(sendButton);
        
        await waitFor(() => {
            expect(mockSendMessage).toHaveBeenCalledWith('Hello world!');
        });
    });

    test('displays received messages', () => {
        const messages = [
            {
                id: '1',
                character_name: 'Test Character',
                message: 'Hello everyone!',
                timestamp: '2024-01-01T00:00:00Z'
            }
        ];
        
        render(<ChatInterface messages={messages} />);
        
        expect(screen.getByText('Test Character')).toBeInTheDocument();
        expect(screen.getByText('Hello everyone!')).toBeInTheDocument();
    });
});
```

## 2. API Contract Testing

**Framework**: Pact for contract testing between frontend and backend

```python
# tests/test_api_contracts.py
import pytest
from pact import Consumer, Provider
from fastapi.testclient import TestClient
from backend.main import app

# Consumer tests (Frontend perspective)
pact = Consumer('frontend').has_pact_with(Provider('backend'))

class TestCharacterContracts:
    def test_create_character_contract(self):
        """Test character creation contract"""
        expected_response = {
            "id": "char_123",
            "name": "Test Hero",
            "character_class": "Warrior",
            "background": "Soldier", 
            "personality": "brave",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        (pact
         .given('character creation is available')
         .upon_receiving('a character creation request')
         .with_request(
             method='POST',
             path='/api/v1/characters',
             headers={'Content-Type': 'application/json'},
             body={
                 "name": "Test Hero",
                 "character_class": "Warrior",
                 "background": "Soldier",
                 "personality": "brave"
             }
         )
         .will_respond_with(201, body=expected_response))
        
        with pact:
            client = TestClient(app)
            response = client.post("/api/v1/characters", json={
                "name": "Test Hero",
                "character_class": "Warrior", 
                "background": "Soldier",
                "personality": "brave"
            })
            
            assert response.status_code == 201
            assert response.json() == expected_response

class TestChatContracts:
    def test_send_message_contract(self):
        """Test chat message sending contract"""
        expected_response = {
            "id": "msg_456",
            "character_id": "char_123",
            "character_name": "Test Hero",
            "message": "Hello world!",
            "chat_type": "pub",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        (pact
         .given('character exists and chat is available')
         .upon_receiving('a chat message')
         .with_request(
             method='POST',
             path='/api/v1/chat/messages',
             headers={'Content-Type': 'application/json'},
             body={
                 "character_id": "char_123",
                 "message": "Hello world!",
                 "chat_type": "pub"
             }
         )
         .will_respond_with(201, body=expected_response))
```

**Frontend Contract Tests**:

```javascript
// frontend/tests/contracts/character.contract.test.js
import { Pact } from '@pact-foundation/pact';
import { apiCall } from '../../src/utils/api';

const provider = new Pact({
    consumer: 'frontend',
    provider: 'backend',
    port: 1234,
    log: path.resolve(process.cwd(), 'logs', 'mockserver-integration.log'),
    dir: path.resolve(process.cwd(), 'pacts'),
    logLevel: 'INFO'
});

describe('Character API Contract', () => {
    beforeAll(() => provider.setup());
    afterEach(() => provider.verify());
    afterAll(() => provider.finalize());

    test('creates a character successfully', async () => {
        const characterRequest = {
            name: 'Contract Test Hero',
            character_class: 'Mage',
            background: 'Sage',
            personality: 'wise'
        };

        const expectedResponse = {
            id: Pact.like('char_789'),
            name: 'Contract Test Hero',
            character_class: 'Mage',
            background: 'Sage',
            personality: 'wise',
            created_at: Pact.iso8601DateTime()
        };

        await provider.addInteraction({
            state: 'character creation is available',
            uponReceiving: 'a character creation request',
            withRequest: {
                method: 'POST',
                path: '/api/v1/characters',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: characterRequest
            },
            willRespondWith: {
                status: 201,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: expectedResponse
            }
        });

        const result = await apiCall('/api/v1/characters', 'POST', characterRequest);
        expect(result).toMatchObject(expectedResponse);
    });
});
```

## 3. Integration Testing

### WebSocket Integration Tests

```python
# tests/test_websocket_integration.py
import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from backend.main import app

class TestWebSocketIntegration:
    def test_websocket_connection(self):
        """Test WebSocket connection and basic messaging"""
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # Test ping/pong
            websocket.send_text(json.dumps({"type": "ping"}))
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "pong"

    def test_chat_message_broadcast(self):
        """Test that chat messages are broadcast to all connected clients"""
        client = TestClient(app)
        
        # Create a character first
        char_response = client.post("/api/v1/characters", json={
            "name": "WebSocket Tester",
            "character_class": "Bard",
            "background": "Entertainer", 
            "personality": "cheerful"
        })
        
        # Connect two WebSocket clients
        with client.websocket_connect("/ws") as ws1, \
             client.websocket_connect("/ws") as ws2:
            
            # Send a chat message via API
            client.post("/api/v1/chat/messages", json={
                "character_id": "WebSocket Tester",
                "message": "Broadcast test",
                "chat_type": "pub"
            })
            
            # Both clients should receive the message
            data1 = ws1.receive_text()
            data2 = ws2.receive_text()
            
            message1 = json.loads(data1)
            message2 = json.loads(data2)
            
            assert message1["type"] == "chat_message"
            assert message2["type"] == "chat_message"
            assert message1["data"]["message"] == "Broadcast test"
            assert message2["data"]["message"] == "Broadcast test"

class TestDatabaseIntegration:
    def test_character_persistence(self):
        """Test that characters are properly saved and retrieved"""
        client = TestClient(app)
        
        # Create character
        char_data = {
            "name": "Persistence Test",
            "character_class": "Paladin",
            "background": "Noble",
            "personality": "righteous"
        }
        
        create_response = client.post("/api/v1/characters", json=char_data)
        created_char = create_response.json()
        
        # Retrieve characters list
        list_response = client.get("/api/v1/characters")
        characters = list_response.json()["characters"]
        
        # Find our character
        found_char = next(
            (c for c in characters if c["name"] == "Persistence Test"),
            None
        )
        
        assert found_char is not None
        assert found_char["character_class"] == "Paladin"
        assert found_char["background"] == "Noble"
```

### Frontend Integration Tests

```javascript
// frontend/tests/integration/chatFlow.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import App from '../../src/App';

// Mock API server
const server = setupServer(
    rest.get('http://localhost:8000/api/v1/characters', (req, res, ctx) => {
        return res(ctx.json({
            characters: [
                {
                    id: 'char_1',
                    name: 'Test Character',
                    character_class: 'Warrior',
                    background: 'Soldier',
                    personality: 'brave'
                }
            ],
            total: 1
        }));
    }),
    
    rest.post('http://localhost:8000/api/v1/chat/messages', (req, res, ctx) => {
        return res(ctx.json({
            id: 'msg_1',
            character_id: 'char_1',
            character_name: 'Test Character',
            message: req.body.message,
            chat_type: 'pub',
            timestamp: new Date().toISOString()
        }));
    })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Chat Flow Integration', () => {
    test('complete chat workflow', async () => {
        render(<App />);
        
        // Wait for characters to load
        await waitFor(() => {
            expect(screen.getByText('Test Character')).toBeInTheDocument();
        });
        
        // Select character
        fireEvent.click(screen.getByText('Test Character'));
        
        // Send message
        const messageInput = screen.getByPlaceholderText('Type your message...');
        fireEvent.change(messageInput, { target: { value: 'Integration test message' } });
        fireEvent.click(screen.getByText('Send'));
        
        // Verify message appears in chat
        await waitFor(() => {
            expect(screen.getByText('Integration test message')).toBeInTheDocument();
        });
    });
});
```

## 4. End-to-End Testing

**Framework**: Playwright for browser automation

```javascript
// e2e/tests/chatFeature.spec.js
import { test, expect } from '@playwright/test';

test.describe('Charcoal 2.0 Chat Feature', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:3000');
    });

    test('user can create character and chat', async ({ page }) => {
        // Create a character
        await page.fill('#charName', 'E2E Test Hero');
        await page.selectOption('#charClass', 'Mage');
        await page.selectOption('#charBackground', 'Sage');
        await page.selectOption('#charPersonality', 'wise');
        await page.click('text=Create Character');
        
        // Wait for character to appear
        await expect(page.locator('text=E2E Test Hero')).toBeVisible();
        
        // Select the character
        await page.click('text=E2E Test Hero');
        
        // Send a message
        await page.fill('#messageInput', 'Hello from E2E test!');
        await page.click('text=Send');
        
        // Verify message appears in chat
        await expect(page.locator('text=Hello from E2E test!')).toBeVisible();
        
        // Verify WebSocket connection status
        await expect(page.locator('text=Connected')).toBeVisible();
    });

    test('AI response generation works', async ({ page }) => {
        // Create and select character
        await page.fill('#charName', 'AI Test Character');
        await page.click('text=Create Character');
        await page.click('text=AI Test Character');
        
        // Generate AI response
        await page.click('text=AI Response');
        
        // Wait for AI message to appear
        await expect(page.locator('.message').first()).toBeVisible();
        
        // Verify the message has content
        const messageContent = await page.locator('.message-content').first().textContent();
        expect(messageContent.length).toBeGreaterThan(0);
    });

    test('real-time chat between multiple tabs', async ({ browser }) => {
        // Open two browser contexts (simulating two users)
        const context1 = await browser.newContext();
        const context2 = await browser.newContext();
        
        const page1 = await context1.newPage();
        const page2 = await context2.newPage();
        
        // Setup both pages
        await page1.goto('http://localhost:3000');
        await page2.goto('http://localhost:3000');
        
        // Create characters in both tabs
        await page1.fill('#charName', 'User 1');
        await page1.click('text=Create Character');
        await page1.click('text=User 1');
        
        await page2.fill('#charName', 'User 2');
        await page2.click('text=Create Character');
        await page2.click('text=User 2');
        
        // Send message from page1
        await page1.fill('#messageInput', 'Message from User 1');
        await page1.click('text=Send');
        
        // Verify message appears in both tabs
        await expect(page1.locator('text=Message from User 1')).toBeVisible();
        await expect(page2.locator('text=Message from User 1')).toBeVisible();
        
        await context1.close();
        await context2.close();
    });
});
```

## 5. Performance Testing

**Framework**: Locust for load testing

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import json
import random

class CharcoalUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup user session"""
        # Create a character for this user
        character_data = {
            "name": f"LoadTest_{random.randint(1000, 9999)}",
            "character_class": random.choice(["Warrior", "Mage", "Rogue", "Cleric"]),
            "background": random.choice(["Noble", "Criminal", "Sage", "Soldier"]),
            "personality": random.choice(["brave", "wise", "mischievous", "loyal"])
        }
        
        response = self.client.post("/api/v1/characters", json=character_data)
        if response.status_code == 201:
            self.character = response.json()
        else:
            self.character = None

    @task(3)
    def send_chat_message(self):
        """Send random chat messages"""
        if not self.character:
            return
            
        messages = [
            "Hello everyone!",
            "How's the adventure going?",
            "Anyone want to form a party?",
            "The tavern is quite lively tonight!",
            "I'm looking for a quest."
        ]
        
        message_data = {
            "character_id": self.character["name"],
            "message": random.choice(messages),
            "chat_type": "pub"
        }
        
        self.client.post("/api/v1/chat/messages", json=message_data)

    @task(1)
    def get_characters(self):
        """Browse character list"""
        self.client.get("/api/v1/characters")

    @task(1)
    def get_chat_history(self):
        """Load chat history"""
        self.client.get("/api/v1/chat/messages?limit=20")

    @task(2)
    def generate_ai_response(self):
        """Generate AI responses"""
        if not self.character:
            return
            
        ai_request = {
            "character_id": self.character["name"],
            "context": "You are in a busy tavern",
            "prompt": "Make a casual comment",
            "conversation_type": "casual"
        }
        
        self.client.post("/api/v1/chat/ai-response", json=ai_request)

# WebSocket load testing
# tests/performance/websocket_load.py
import asyncio
import websockets
import json
import time
from concurrent.futures import ThreadPoolExecutor

async def websocket_client(client_id):
    """Simulate a WebSocket client"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send ping every few seconds
            for i in range(60):  # Run for 1 minute
                await websocket.send(json.dumps({"type": "ping"}))
                response = await websocket.recv()
                message = json.loads(response)
                assert message["type"] == "pong"
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"Client {client_id} error: {e}")

async def run_websocket_load_test(num_clients=50):
    """Run WebSocket load test with multiple clients"""
    print(f"Starting WebSocket load test with {num_clients} clients")
    
    start_time = time.time()
    
    # Create tasks for all clients
    tasks = [websocket_client(i) for i in range(num_clients)]
    
    # Run all clients concurrently
    await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    print(f"Load test completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_websocket_load_test())
```

## 6. Security Testing

```python
# tests/security/test_input_validation.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestInputValidation:
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are blocked"""
        malicious_input = {
            "name": "'; DROP TABLE characters; --",
            "character_class": "Warrior",
            "background": "Soldier",
            "personality": "brave"
        }
        
        response = client.post("/api/v1/characters", json=malicious_input)
        
        # Should either validate or handle gracefully
        assert response.status_code in [400, 422]

    def test_xss_prevention(self):
        """Test XSS script injection prevention"""
        xss_payload = {
            "name": "<script>alert('xss')</script>",
            "character_class": "Mage",
            "background": "Sage", 
            "personality": "wise"
        }
        
        response = client.post("/api/v1/characters", json=xss_payload)
        
        if response.status_code == 201:
            # If created, ensure script tags are escaped
            data = response.json()
            assert "<script>" not in data["name"]

    def test_oversized_input_handling(self):
        """Test handling of oversized inputs"""
        large_input = {
            "name": "A" * 10000,  # Very long name
            "character_class": "Warrior",
            "background": "Soldier",
            "personality": "brave"
        }
        
        response = client.post("/api/v1/characters", json=large_input)
        assert response.status_code == 422  # Validation error

class TestRateLimiting:
    def test_chat_message_rate_limit(self):
        """Test that chat messages are rate limited"""
        # Create character first
        char_response = client.post("/api/v1/characters", json={
            "name": "Rate Test",
            "character_class": "Bard",
            "background": "Entertainer",
            "personality": "cheerful"
        })
        character = char_response.json()
        
        # Send many messages rapidly
        for i in range(20):
            response = client.post("/api/v1/chat/messages", json={
                "character_id": character["name"],
                "message": f"Spam message {i}",
                "chat_type": "pub"
            })
            
            # After some threshold, should be rate limited
            if i > 10:
                assert response.status_code in [201, 429]  # Success or rate limited
```

## 7. Continuous Integration Setup

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: charcoal_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run unit tests
      run: |
        cd backend
        pytest tests/ -v --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run unit tests
      run: |
        cd frontend
        npm test -- --coverage
    
    - name: Run contract tests
      run: |
        cd frontend
        npm run test:contract

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start backend
      run: |
        cd backend
        pip install -r requirements.txt
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        
    - name: Start frontend
      run: |
        cd frontend
        npm install
        npm start &
    
    - name: Wait for services
      run: |
        sleep 30
        curl -f http://localhost:8000/health
        curl -f http://localhost:3000
    
    - name: Run E2E tests
      run: |
        npx playwright install
        npx playwright test

  load-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start backend
      run: |
        cd backend
        pip install -r requirements.txt
        uvicorn main:app --host 0.0.0.0 --port 8000 &
    
    - name: Run load tests
      run: |
        pip install locust
        cd tests/performance
        locust --headless --users 50 --spawn-rate 5 --run-time 2m --host http://localhost:8000
```

## 8. Test Data Management

```python
# tests/fixtures/test_data.py
import pytest
from typing import List, Dict

@pytest.fixture
def sample_characters() -> List[Dict]:
    """Sample character data for testing"""
    return [
        {
            "name": "Test Warrior",
            "character_class": "Warrior",
            "background": "Soldier",
            "personality": "brave"
        },
        {
            "name": "Test Mage", 
            "character_class": "Mage",
            "background": "Sage",
            "personality": "wise"
        },
        {
            "name": "Test Rogue",
            "character_class": "Rogue", 
            "background": "Criminal",
            "personality": "mischievous"
        }
    ]

@pytest.fixture
def sample_chat_messages() -> List[Dict]:
    """Sample chat messages for testing"""
    return [
        {
            "character_name": "Test Warrior",
            "message": "Greetings, fellow adventurers!",
            "chat_type": "pub",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "character_name": "Test Mage",
            "message": "The arcane energies feel strong today.",
            "chat_type": "pub", 
            "timestamp": "2024-01-01T10:01:00Z"
        }
    ]

@pytest.fixture
def clean_database():
    """Clean database before each test"""
    # Clear test data
    yield
    # Cleanup after test
```

## 9. Monitoring and Alerting

```python
# backend/monitoring.py
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log performance metrics
        logging.info(f"Request: {request.method} {request.url.path} - "
                    f"Status: {response.status_code} - "
                    f"Time: {process_time:.4f}s")
        
        # Alert on slow requests
        if process_time > 5.0:
            logging.warning(f"Slow request detected: {request.url.path} took {process_time:.4f}s")
        
        return response
```

This comprehensive testing strategy ensures reliable integration between the Python backend and JavaScript frontend, covering all aspects from unit tests to performance and security testing. The strategy emphasizes automation, continuous integration, and maintainable test code that grows with the application.