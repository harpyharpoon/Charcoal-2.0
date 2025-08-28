# Getting Started with Charcoal 2.0

Welcome to your new text-based MMORPG with AI characters! This implementation provides a working foundation for the Charcoal 2.0 vision.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Try the Demo
```bash
python main.py demo
```

### 3. Run the Interactive Spectator Mode
```bash
python main.py
```

## Features Implemented

✅ **AI Character System**
- 8 pre-created characters with different classes and personalities
- Character configuration with classes, backgrounds, and personality traits
- Mock AI dialogue system (works without OpenAI API key)

✅ **World & Dungeon System**
- 3 different themed dungeons (Ancient Temple, Enchanted Grove, Crystal Caves)
- Multiple interconnected areas per dungeon
- Different area types (entrance, chambers, boss rooms, treasure rooms, etc.)

✅ **Party Mechanics**
- Party formation with multiple AI characters
- Party exploration and movement between areas
- Experience tracking and inventory management

✅ **AI Dialogue System**
- Character-specific dialogue based on personality and class
- Group conversations between party members
- Context-aware responses to different situations
- Works in both mock mode and with real OpenAI API

✅ **Spectator Interface**
- Real-time watching of party adventures
- Colored terminal output for different event types
- Interactive commands for controlling the experience
- Auto-advance mode for continuous watching

## Commands in Spectator Mode

- `create party` - Create a new random party
- `watch <party>` - Watch a specific party's adventure
- `list parties` - Show all active parties
- `list chars` - Show all available characters
- `list dungeons` - Show available dungeons
- `change dungeon <name>` - Switch to a different dungeon
- `step` - Advance the current party one step
- `auto` - Toggle auto-advance mode for continuous action
- `status` - Show current system status
- `help` - Show available commands
- `quit` - Exit the program

## Using Real AI (Optional)

1. Get an OpenAI API key from https://openai.com/
2. Copy `.env.example` to `.env`
3. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
4. Run the program - it will now use real AI for dialogue!

## Example Session

```
> create party
✅ Created party: Party 1
Members: Felix, Kael, Lyra, Theron
👁️ Now watching: Party 1

> step
📖 As Felix, Kael, Lyra and Theron explore the area carefully in the Temple Entrance, the air grows thick with anticipation.
💬 Lyra: "I sense magical energy here." says Lyra.

> step
🚶 The party moves from Temple Entrance to Grand Hall.
✨ **New area discovered: Grand Hall**
💬 Felix: "Stay positive, friends!" says Felix.

> auto
🔄 Auto-advance enabled for Party 1
Press Ctrl+C to stop auto-advance
```

## Architecture

The system consists of several key components:

- **`character.py`** - Character creation and management
- **`world.py`** - Dungeon and area generation
- **`ai_dialogue.py`** - AI-powered dialogue system
- **`party.py`** - Party mechanics and adventure logic
- **`spectator.py`** - Interactive viewing interface
- **`config.py`** - Configuration and settings
- **`main.py`** - Entry point and demo mode

## Extending the System

This implementation provides a solid foundation that can be extended with:

- More character classes and backgrounds
- Additional dungeon themes and areas
- Combat system with stats and equipment
- Persistent save/load functionality
- Web interface for multi-user spectating
- Voice synthesis for audio dramas
- More sophisticated AI decision making

The modular design makes it easy to add new features while maintaining the core functionality.

## Technical Notes

- Uses mock AI responses when no OpenAI API key is provided
- All game state is maintained in memory (can be extended to persistent storage)
- Character dialogue is generated based on class, background, and personality
- Adventure events are procedurally generated with multiple event types
- Color-coded terminal output enhances the viewing experience

Enjoy watching your AI characters come to life in their adventures!