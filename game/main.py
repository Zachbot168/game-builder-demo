"""Main entry point for Eldritch Espresso game."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import App
from core.state import StateID


def main() -> None:
    """Run the game."""
    app = App()
    
    # Import and register all states
    from ui.screens import (
        MainMenuState, DayIntroState, ServiceState, ChaosEventState,
        DayResultsState, UpgradeShopState, DialogueState, PauseState
    )
    
    # Register states
    app.state_manager.register_state(StateID.MAIN_MENU, MainMenuState(app))
    app.state_manager.register_state(StateID.DAY_INTRO, DayIntroState(app))
    app.state_manager.register_state(StateID.SERVICE, ServiceState(app))
    app.state_manager.register_state(StateID.CHAOS_EVENT, ChaosEventState(app))
    app.state_manager.register_state(StateID.DAY_RESULTS, DayResultsState(app))
    app.state_manager.register_state(StateID.UPGRADE_SHOP, UpgradeShopState(app))
    app.state_manager.register_state(StateID.DIALOGUE, DialogueState(app))
    app.state_manager.register_state(StateID.PAUSE, PauseState(app))
    
    # Start with main menu
    app.set_initial_state(StateID.MAIN_MENU)
    
    # Run game
    app.run()


if __name__ == "__main__":
    main()