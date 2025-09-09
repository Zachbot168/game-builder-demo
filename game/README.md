# Eldritch Espresso - Python Demo

A cosmic coffee shop management game where you serve otherworldly customers and manage supernatural chaos!

## Setup Instructions

### Requirements
- Python 3.10 or newer
- pygame 2.5.0 or newer
- numpy (optional, for audio generation)

### Installation

1. Install Python from [python.org](https://python.org) if you don't have it

2. Navigate to the game directory:
   ```bash
   cd game
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Alternative manual installation:**
   ```bash
   pip install pygame numpy
   ```
   
   Note: If numpy installation fails, the game will still run with silent placeholders for audio.

4. Run the game:
   ```bash
   python -m main
   ```

### Quick Start
```bash
# Clone or download the project
cd game
pip install -r requirements.txt
python -m main
```

## How to Play

### Controls
- **Mouse**: All game interactions
- **Left Click**: Select customers, ingredients, buttons
- **Escape**: Pause/unpause during gameplay

### Game Flow

1. **Main Menu**: Click "Start Game" to begin

2. **Day Introduction**: Brief dialogue with cosmic entities

3. **Service Phase** (90 seconds):
   - **Customer Queue** (left): Shows waiting customers with patience bars
   - **Brewing Station** (middle): Create drinks by selecting ingredients
   - **Order Display** (right): Shows what each customer wants
   
   **How to serve drinks:**
   - Click a customer to select their order
   - Click ingredient buttons to add to the recipe
   - Click "Confirm" to serve the drink
   - Correct recipes earn tips!

4. **Chaos Event** (mid-day):
   - A portal opens and pastries float away
   - Brew a "Banishing Espresso" (Beans + Moonlight + Sigil) to close it
   - Act fast before the rift consumes everything!

5. **Day Results**: See your earnings and customer feedback

6. **Upgrade Shop**: Spend coins on permanent improvements:
   - **Enchanted Grinder**: 20% faster brewing
   - **Calming Fern**: 15% slower patience decay

### Customer Quirks

- **Fire Elemental** (Ignis): Heats the caf�, making ice drinks melt faster
- **Ghost** (Whim): Invisible! Use the bell button to reveal them briefly
- **Tentacled** (Azzu): Standard customer, no special quirks

### Recipes

- **Milky Way Mocha**: Beans + Milk + Stardust
- **Flaming Meteor Espresso**: Beans + Meteor Shot
- **Banishing Espresso**: Beans + Moonlight + Sigil (for chaos events)

### Tips for Success

- Watch patience bars - customers leave if you're too slow
- Fire elementals make the caf� hot - serve ice drinks quickly!
- Ring the bell regularly to spot invisible ghosts
- Save the Banishing Espresso recipe for portal events
- Buy upgrades to make subsequent days easier

## Troubleshooting

### Game won't start
- Ensure Python 3.10+ is installed
- Check pygame installation: `pip show pygame`
- **IMPORTANT**: Run from the game directory, not the parent folder
- The game expects to find `data/recipes.json` and `data/customers.json` relative to current directory

### No audio
- This is normal if numpy isn't installed
- Try: `pip install numpy` for generated sound effects
- The game is fully playable without audio

### Performance issues
- Close other applications
- The game targets 60 FPS but may run slower on older hardware
- Reduce window size isn't supported in this version

### Black screen on startup
- Wait a moment for assets to generate
- Check console for error messages
- Ensure pygame is properly installed

## Game Architecture

The game uses a state machine pattern with the following states:
- Main Menu
- Day Introduction  
- Service (main gameplay)
- Chaos Event
- Day Results
- Upgrade Shop
- Dialogue
- Pause

Core systems include:
- Service Controller (customer queue and brewing)
- Chaos Manager (portal events)
- Upgrade Manager (persistent improvements)
- Dialogue System (story moments)

## Credits

Created as a Python prototype for Eldritch Espresso.
Built with pygame for rapid prototyping.