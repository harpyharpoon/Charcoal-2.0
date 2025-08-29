# Charcoal 2.0 - AI-Powered Text Adventure Game

**ALWAYS follow these instructions first and fallback to additional search and context gathering only when information here is incomplete or found to be in error.**

Charcoal 2.0 is a Python-based text adventure game where AI characters form parties, explore dungeons, and interact with each other in a persistent world. Players can spectate adventures in real-time or interact through a pub interface.

## Working Effectively

### Bootstrap and Setup
1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   - Takes ~30 seconds
   - Installs: openai, python-dotenv, colorama, pydantic
   - Works with Python 3.11+ (tested with 3.12)

2. **Test the installation:**
   ```bash
   python main.py demo
   ```
   - Takes ~3 seconds to complete
   - Shows AI characters in action with mock dialogue
   - **VALIDATION**: Should display party creation, movement, item discovery, and character dialogue

### Running the Application

3. **Run interactive mode:**
   ```bash
   python main.py
   ```
   - Interactive menu with three options:
     - **Pub Mode**: Create characters, view quests, chat with NPCs
     - **Spectator Mode**: Watch AI parties explore dungeons
     - **Demo Mode**: Quick automated demonstration

4. **Test all core functionality:**
   ```bash
   # Run all test suites
   python test_enhanced_system.py
   python test_items.py  
   python test_pub_interface.py
   python test_world.py
   ```
   - Each test takes <1 second
   - All tests should pass with "OK" status
   - **VALIDATION**: Confirms character system, world generation, party mechanics, and item systems work

## Validation Scenarios

**ALWAYS test these scenarios after making changes:**

1. **Core Demo Functionality:**
   ```bash
   python main.py demo
   ```
   - Verify: Party creation with 4 characters
   - Verify: Movement between dungeon areas
   - Verify: Item discovery and inventory
   - Verify: AI character dialogue (mock responses)

2. **Interactive Pub Experience:**
   ```bash
   python main.py
   # Choose option 1 (Enter The Pub)
   # Test: Character creation, quest board, patron chat
   # Exit cleanly with option 6
   ```

3. **Spectator Mode Validation:**
   ```bash
   python main.py  
   # Choose option 2 (Spectator Mode)
   # Commands: help, list chars, list dungeons, create party
   # Exit with: quit
   ```

## AI System Notes

- **Mock AI Mode**: Works without OpenAI API key (default)
- **Real AI Mode**: Requires OPENAI_API_KEY in .env file
- **Configuration**: Copy `.env.example` to `.env` and add API key for real AI
- The application gracefully handles missing API keys

## Project Structure

### Core Modules
- **`main.py`** - Application entry point and main menu
- **`character.py`** - Character creation and management system
- **`world.py`** - Dungeon and area generation
- **`party.py`** - Party mechanics and adventure logic  
- **`spectator.py`** - Interactive spectator interface
- **`pub_interface.py`** - Pub/tavern interaction system
- **`ai_dialogue.py`** - AI-powered dialogue generation
- **`items.py`** - Item generation and inventory system
- **`config.py`** - Application configuration

### Data Files
- **`characters.json`** - Default character definitions
- **`requirements.txt`** - Python dependencies
- **`.env.example`** - Environment variable template

### Testing
- **`test_enhanced_system.py`** - Comprehensive system integration tests
- **`test_items.py`** - Item system validation
- **`test_pub_interface.py`** - Pub interface testing
- **`test_world.py`** - World generation and party system tests

## Common Development Tasks

### Running Tests
```bash
# Run specific test suite
python test_enhanced_system.py

# Run all tests
python test_enhanced_system.py && python test_items.py && python test_pub_interface.py && python test_world.py
```

### Quick Development Validation
```bash
# Test core functionality
python main.py demo

# Test interactive features  
python main.py
# Select option 1 or 2, test features, exit cleanly
```

### Adding New Features
1. **Test existing functionality first** - Run demo mode and interactive tests
2. **Character System**: Modify `character.py` and update `characters.json`
3. **World Content**: Update `world.py` for new dungeons/areas
4. **AI Behavior**: Modify `ai_dialogue.py` for dialogue patterns
5. **Always validate** with demo mode after changes

## Error Handling

- **Missing dependencies**: Clear ModuleNotFoundError - run pip install
- **Import errors**: Check file paths and module structure
- **Runtime errors**: Application handles gracefully and shows user-friendly messages
- **AI service errors**: Falls back to mock responses automatically

## Development Environment

- **Python Version**: 3.11+ required
- **Dependencies**: Listed in requirements.txt
- **No build system** - Direct Python execution
- **No linting setup** - Code follows Python standards
- **No CI/CD configured** - Manual testing required

## Key Design Patterns

- **Event-driven**: Characters and parties generate events
- **Modular**: Each system (characters, world, AI) is separate
- **Configurable**: Mock vs real AI, different character types
- **Interactive**: Real-time user input in both pub and spectator modes
- **Stateful**: Game maintains character inventories and world state

## Performance Notes

- **Startup**: <1 second for any mode
- **Demo execution**: ~3 seconds for full demo
- **Test execution**: <1 second per test suite
- **Memory usage**: Minimal (text-based, no heavy assets)
- **AI calls**: Throttled to prevent rate limiting when using real API

## Future Architecture

The repository context indicates planned expansion to:
- **Frontend**: React/JavaScript web interface
- **Backend**: FastAPI REST API with WebSocket support
- **Database**: PostgreSQL for persistence
- **Deployment**: Docker containerization

Current implementation serves as the core logic foundation for this expansion.