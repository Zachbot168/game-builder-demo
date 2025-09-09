"""Main application class managing the game loop and core systems."""
import pygame
from typing import Dict, Any, Optional
import time

from .state import StateManager, StateID


class App:
    """Main application managing game loop and systems."""
    
    def __init__(self, width: int = 960, height: int = 540, title: str = "Eldritch Espresso") -> None:
        """Initialize the application."""
        pygame.init()
        pygame.mixer.init()
        
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Core systems
        self.state_manager = StateManager()
        
        # Game state
        self.game_data: Dict[str, Any] = {
            "coins": 10,
            "day": 1,
            "upgrades": [],
            "modifiers": {},
            "customers_served": 0,
            "total_tips": 0
        }
        
        # Fixed timestep
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS
        self.accumulator = 0.0
        self.last_time = time.time()
    
    def run(self) -> None:
        """Run the main game loop."""
        self.running = True
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            frame_time = min(current_time - self.last_time, 0.25)  # Cap at 0.25s
            self.last_time = current_time
            self.accumulator += frame_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Handle pause
                    current_state = self.state_manager.get_current_state_id()
                    if current_state == StateID.PAUSE:
                        # Unpause - return to previous state
                        if self.state_manager.previous_state_id:
                            self.state_manager.change_state(self.state_manager.previous_state_id)
                    elif current_state not in [StateID.MAIN_MENU, StateID.DIALOGUE]:
                        # Pause game
                        self.state_manager.change_state(StateID.PAUSE)
                else:
                    self.state_manager.handle_event(event)
            
            # Fixed timestep update
            while self.accumulator >= self.fixed_timestep:
                self.state_manager.update(self.fixed_timestep)
                self.accumulator -= self.fixed_timestep
            
            # Render
            self.screen.fill((20, 20, 30))  # Dark background
            self.state_manager.draw(self.screen)
            pygame.display.flip()
            
            # Cap framerate
            self.clock.tick(60)
        
        self.quit()
    
    def quit(self) -> None:
        """Clean up and exit."""
        pygame.mixer.quit()
        pygame.quit()
    
    def set_initial_state(self, state_id: StateID) -> None:
        """Set the initial game state."""
        self.state_manager.change_state(state_id)
    
    def get_modifiers(self) -> Dict[str, float]:
        """Get active game modifiers from upgrades."""
        return self.game_data.get("modifiers", {})