# AMNESIA.md - Important Information for Future Development

## Project Overview

This is a Python prototype of "Eldritch Espresso" - a cosmic coffee shop management game. The prototype demonstrates core gameplay mechanics and is intended for eventual porting to Unity.

## Key Architecture Decisions

### State Machine Pattern
- All game screens inherit from `GameState` base class
- States are managed by `StateManager` in `core/state.py`
- Easy to add new states by following the existing pattern

### Data-Driven Design
- Recipes and customers loaded from JSON files in `data/`
- Makes content easy to modify without code changes
- Will translate well to Unity ScriptableObjects

### System Separation
- Core systems (service, chaos, upgrades, dialogue) are independent
- Each system has clear interfaces and responsibilities
- Modular design allows easy extension

## Critical Implementation Details

### Fixed Timestep
- Game uses fixed timestep (60 FPS) with accumulator pattern
- Ensures consistent gameplay regardless of framerate
- See `App.run()` in `core/app.py`

### Audio System
- Uses generated tones if numpy is available
- Falls back to silence if numpy missing
- Audio files can replace generated sounds in `sfx/` directory

### Customer Quirks
- Fire elemental's heat affects ice drinks (not fully implemented)
- Ghost invisibility uses timer-based reveal system
- Quirks checked in `ServiceController.update()`

### Chaos Event Timing
- Triggers at 45 seconds remaining (midpoint of 90-second day)
- Only portal event implemented, but system supports multiple event types
- Resolution requires specific recipe matching

## Known Limitations & Future Work

### Not Implemented
1. Ice drink melting mechanic (heat affects timer)
2. Save/load system for progress persistence  
3. Difficulty settings
4. Additional chaos events
5. More customer types and quirks
6. Extended recipe system

### Technical Debt
1. UI positioning is hardcoded - should use relative layout
2. No proper animation system - just static sprites
3. Sound generation requires numpy - should include .wav files
4. Limited error handling in file loading

### Performance Considerations
- Customer queue updates every frame (could optimize)
- No sprite batching or optimization
- Assets generated on startup (could pre-generate)

## Unity Migration Guide

### Direct Mappings
- `GameState` ’ Unity Scene or State Machine Behaviour
- JSON data files ’ ScriptableObject assets
- `ServiceController` ’ GameManager component
- Drawing code ’ Unity UI system

### Key Differences
- Unity uses component system vs inheritance
- Unity has built-in animation and audio
- Unity UI uses anchoring for responsive layout

### Preserve These Concepts
1. State machine for game flow
2. Data-driven content (recipes, customers)
3. Separation of systems (service, chaos, upgrades)
4. Fixed timestep for gameplay logic

## Testing Checklist

When modifying the game, ensure:
- [ ] All customers can spawn and be served
- [ ] All recipes work correctly
- [ ] Chaos event triggers and can be resolved
- [ ] Upgrades apply their effects
- [ ] State transitions work smoothly
- [ ] Audio plays at appropriate times
- [ ] No crashes during full playthrough

## Quick Start for Developers

1. Main entry: `main.py`
2. Game loop: `core/app.py`
3. Gameplay: `systems/service.py`
4. UI: `ui/screens.py`
5. Add content: Edit JSON files in `data/`

## Common Issues

### "Module not found" errors
- Run with `python -m main` from game directory
- Don't run from parent directory

### Black screen
- Assets generating, wait a moment
- Check console for errors

### No customers spawning
- Check `data/customers.json` exists
- Verify `ServiceController.load_customers()` succeeded

Remember: This is a prototype focusing on core mechanics. Polish and extended features are for the Unity version!