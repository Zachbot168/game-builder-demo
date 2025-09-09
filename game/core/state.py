"""Base game state system for managing different screens and game modes."""
from abc import ABC, abstractmethod
from typing import Dict, Type, Any, Optional
from enum import Enum
import pygame


class StateID(Enum):
    """Game state identifiers."""
    MAIN_MENU = "main_menu"
    DAY_INTRO = "day_intro"
    SERVICE = "service"
    CHAOS_EVENT = "chaos_event"
    DAY_RESULTS = "day_results"
    UPGRADE_SHOP = "upgrade_shop"
    DIALOGUE = "dialogue"
    PAUSE = "pause"


class GameState(ABC):
    """Base class for all game states."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize state with reference to app."""
        self.app = app
        self.is_active = False
    
    def enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering this state."""
        self.is_active = True
        self.on_enter(data)
    
    def exit(self) -> None:
        """Called when exiting this state."""
        self.is_active = False
        self.on_exit()
    
    @abstractmethod
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """State-specific enter logic."""
        pass
    
    @abstractmethod
    def on_exit(self) -> None:
        """State-specific exit logic."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update state logic."""
        pass
    
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw state visuals."""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        pass


class StateManager:
    """Manages game states and transitions."""
    
    def __init__(self) -> None:
        """Initialize state manager."""
        self.states: Dict[StateID, GameState] = {}
        self.current_state: Optional[GameState] = None
        self.previous_state_id: Optional[StateID] = None
        self.transition_data: Optional[Dict[str, Any]] = None
    
    def register_state(self, state_id: StateID, state: GameState) -> None:
        """Register a state with an ID."""
        self.states[state_id] = state
    
    def change_state(self, state_id: StateID, data: Optional[Dict[str, Any]] = None) -> None:
        """Change to a new state."""
        if state_id not in self.states:
            raise ValueError(f"State {state_id} not registered")
        
        if self.current_state:
            self.current_state.exit()
            for sid, state in self.states.items():
                if state == self.current_state:
                    self.previous_state_id = sid
                    break
        
        self.current_state = self.states[state_id]
        self.transition_data = data
        self.current_state.enter(data)
    
    def update(self, dt: float) -> None:
        """Update current state."""
        if self.current_state:
            self.current_state.update(dt)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw current state."""
        if self.current_state:
            self.current_state.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events for current state."""
        if self.current_state:
            self.current_state.handle_event(event)
    
    def get_current_state_id(self) -> Optional[StateID]:
        """Get ID of current state."""
        for state_id, state in self.states.items():
            if state == self.current_state:
                return state_id
        return None