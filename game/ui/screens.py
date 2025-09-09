"""All game screen implementations for different states."""
import pygame
from typing import Dict, Any, Optional, List
import random

from core.state import GameState, StateID
from core.assets import assets
from ui.widgets import Button, ProgressBar, CustomerCard, Panel, Label, DialogueBox
from systems.service import ServiceController
from systems.chaos import ChaosManager
from systems.upgrades import UpgradeManager
from systems.dialogue import DialogueManager


class MainMenuState(GameState):
    """Main menu screen."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize main menu."""
        super().__init__(app)
        self.buttons: List[Button] = []
        self.background_particles: List[Dict[str, Any]] = []
        self.background_music_playing = False
        self.init_ui()
        self.init_particles()
    
    def init_ui(self) -> None:
        """Initialize UI elements."""
        center_x = self.app.width // 2
        button_width = 200
        button_height = 50
        
        self.buttons = [
            Button(
                center_x - button_width // 2, 250,
                button_width, button_height,
                "Start Game",
                self.start_game
            ),
            Button(
                center_x - button_width // 2, 320,
                button_width, button_height,
                "Quit",
                self.quit_game
            )
        ]
    
    def init_particles(self) -> None:
        """Initialize background particles."""
        for _ in range(50):
            self.background_particles.append({
                'x': random.uniform(0, self.app.width),
                'y': random.uniform(0, self.app.height),
                'vel_x': random.uniform(-0.5, 0.5),
                'vel_y': random.uniform(-0.8, -0.2),
                'size': random.randint(1, 3),
                'color': random.choice([(100, 150, 200), (150, 100, 200), (200, 150, 100)])
            })
    
    def start_game(self) -> None:
        """Start the game."""
        self.app.game_data["day"] = 1
        self.app.game_data["coins"] = 10
        self.app.state_manager.change_state(StateID.DAY_INTRO, {"day": 1})
    
    def quit_game(self) -> None:
        """Quit the game."""
        self.app.running = False
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering main menu."""
        # Play background music
        assets.play_sound("background_music", volume=0.3, loop=True)
        self.background_music_playing = True
    
    def on_exit(self) -> None:
        """Called when exiting main menu."""
        # Stop background music when leaving main menu
        if self.background_music_playing:
            assets.stop_sound("background_music")
            self.background_music_playing = False
    
    def update(self, dt: float) -> None:
        """Update main menu."""
        # Update particles
        for particle in self.background_particles:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = self.app.width
            elif particle['x'] > self.app.width:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = self.app.height
            elif particle['y'] > self.app.height:
                particle['y'] = 0
        
        # Background music will loop automatically since we set loop=True when starting
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw main menu."""
        # Draw particles
        for particle in self.background_particles:
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        # Title
        title_font = assets.get_font('title')
        title_text = "Eldritch Espresso"
        title_rect = title_font.get_rect(title_text)
        title_pos = (self.app.width // 2 - title_rect.width // 2, 150)
        title_font.render_to(screen, title_pos, title_text, (255, 255, 255))
        
        # Subtitle
        subtitle_font = assets.get_font('medium')
        subtitle_text = "Coffee for Cosmic Beings"
        subtitle_rect = subtitle_font.get_rect(subtitle_text)
        subtitle_pos = (self.app.width // 2 - subtitle_rect.width // 2, 190)
        subtitle_font.render_to(screen, subtitle_pos, subtitle_text, (200, 200, 200))
        
        # Buttons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        for button in self.buttons:
            button.handle_event(event)


class DayIntroState(GameState):
    """Day introduction screen with dialogue."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize day intro."""
        super().__init__(app)
        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox(50, 350, 860, 140)
        self.continue_button = Button(800, 450, 100, 40, "Continue", self.advance_dialogue)
        self.day_number = 1
        self.timer = 0.0
        self.auto_advance_delay = 3.0
    
    def advance_dialogue(self) -> None:
        """Advance dialogue or proceed to service."""
        if not self.dialogue_manager.advance():
            # Dialogue complete, start service
            self.app.state_manager.change_state(StateID.SERVICE, {"day": self.day_number})
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering day intro."""
        if data:
            self.day_number = data.get("day", 1)
        
        # Start random intro dialogue
        self.dialogue_manager.start_scene(context="day_intro")
        self.timer = 0.0
    
    def on_exit(self) -> None:
        """Called when exiting day intro."""
        self.dialogue_manager.end_scene()
    
    def update(self, dt: float) -> None:
        """Update day intro."""
        self.timer += dt
        
        # Auto-advance if no dialogue or after delay
        if not self.dialogue_manager.get_current_line():
            if self.timer >= self.auto_advance_delay:
                self.app.state_manager.change_state(StateID.SERVICE, {"day": self.day_number})
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw day intro."""
        # Background gradient
        for y in range(0, self.app.height, 4):
            color_factor = y / self.app.height
            color = (
                int(20 + color_factor * 30),
                int(20 + color_factor * 40),
                int(40 + color_factor * 50)
            )
            pygame.draw.rect(screen, color, (0, y, self.app.width, 4))
        
        # Day title
        title_font = assets.get_font('title')
        title_text = f"Day {self.day_number}"
        title_rect = title_font.get_rect(title_text)
        title_pos = (self.app.width // 2 - title_rect.width // 2, 100)
        title_font.render_to(screen, title_pos, title_text, (255, 255, 255))
        
        # Dialogue
        current_line = self.dialogue_manager.get_current_line()
        if current_line:
            self.dialogue_box.show_dialogue(current_line.speaker, current_line.text)
            self.dialogue_box.draw(screen)
            self.continue_button.draw(screen)
        else:
            # Show "Starting day..." message
            font = assets.get_font('medium')
            text = "Starting day..."
            text_rect = font.get_rect(text)
            text_pos = (self.app.width // 2 - text_rect.width // 2, 250)
            font.render_to(screen, text_pos, text, (200, 200, 200))
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        if self.dialogue_manager.get_current_line():
            self.continue_button.handle_event(event)
            
            # Space or Enter to advance
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.advance_dialogue()


class ServiceState(GameState):
    """Main service gameplay screen."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize service state."""
        super().__init__(app)
        self.service_controller = ServiceController()
        self.chaos_manager = ChaosManager()
        self.upgrade_manager = UpgradeManager()
        
        # UI elements
        self.customer_cards: List[CustomerCard] = []
        self.ingredient_buttons: List[Button] = []
        self.status_panel = Panel(0, 500, 960, 40, "Status")
        self.bell_button = Button(850, 10, 100, 40, "Ring Bell", self.ring_bell)
        self.thermometer_rect = pygame.Rect(780, 60, 24, 48)
        
        # Brewing UI (repositioned)
        self.serve_button = Button(300, 450, 120, 50, "Serve Drink", self.serve_drink)
        self.cancel_button = Button(430, 450, 120, 50, "Cancel Order", self.cancel_order)
        
        # Ingredient name mapping for display
        self.ingredient_display_names = {
            "beans": "☕ Coffee Beans",
            "milk": "🥛 Milk",
            "stardust": "✨ Stardust",
            "meteor_shot": "☄️ Meteor Shot",
            "moonlight": "🌙 Moonlight",
            "sigil": "🔮 Sigil"
        }
        
        # Order display
        self.order_tickets: List[Panel] = []
        
        # Current brewing display
        self.current_recipe_panel = Panel(300, 140, 380, 60, "Current Recipe")
        self.target_recipe_panel = Panel(300, 210, 380, 60, "Target Recipe")
        
        # Audio state
        self.background_music_playing = False
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize UI layout."""
        # Customer queue (left side)
        queue_width = 280
        card_height = 90
        for i in range(5):
            card = CustomerCard(10, 10 + i * (card_height + 5), queue_width - 20, card_height)
            self.customer_cards.append(card)
        
        # Ingredient buttons (larger and more obvious)
        ingredients = ["beans", "milk", "stardust", "meteor_shot", "moonlight", "sigil"]
        button_size = 80  # Increased size
        start_x = 300
        start_y = 280
        
        for i, ingredient in enumerate(ingredients):
            x = start_x + (i % 3) * (button_size + 15)
            y = start_y + (i // 3) * (button_size + 15)
            button = Button(x, y, button_size, button_size, 
                          ingredient.replace("_", " ").title(),
                          lambda ing=ingredient: self.add_ingredient(ing))
            self.ingredient_buttons.append(button)
        
        # Recipe book panel (top middle)
        self.recipe_book_panel = Panel(300, 10, 380, 120, "Recipe Book")
        
        # Order tickets (right side)
        ticket_width = 270
        for i in range(5):
            panel = Panel(690, 10 + i * 90, ticket_width - 20, 80, f"Order {i+1}")
            self.order_tickets.append(panel)
    
    def ring_bell(self) -> None:
        """Ring bell to reveal ghost customers."""
        self.service_controller.ring_bell()
    
    def add_ingredient(self, ingredient: str) -> None:
        """Add ingredient to current recipe."""
        if self.service_controller.brewing_station.selected_customer_index is not None:
            self.service_controller.brewing_station.add_ingredient(ingredient)
    
    def serve_drink(self) -> None:
        """Serve the current drink."""
        recipe = self.service_controller.brewing_station.current_recipe
        if recipe and self.service_controller.brewing_station.selected_customer_index is not None:
            result = self.service_controller.serve_drink(recipe)
            
            # Play ding sound for correct drink
            if result and result.get('correct', False):
                assets.play_sound("ding", volume=0.7)
            
            # Check if this resolves chaos event
            if self.chaos_manager.is_active():
                resolution = self.chaos_manager.try_resolve("serve_drink", recipe)
                if resolution:
                    # Show resolution message
                    pass
            
            # Complete brewing
            self.service_controller.brewing_station.complete_order()
    
    def cancel_order(self) -> None:
        """Cancel current order."""
        self.service_controller.brewing_station.cancel_order()
    
    def select_customer(self, index: int) -> None:
        """Select customer for brewing."""
        customer = self.service_controller.customer_queue.customers[index]
        if customer:
            self.service_controller.brewing_station.start_order(index)
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering service."""
        day = data.get("day", 1) if data else 1
        self.service_controller.start_day(day)
        self.chaos_manager.reset()
        
        # Play background music at low volume
        assets.play_sound("background_music", volume=0.3, loop=True)
        self.background_music_playing = True
    
    def on_exit(self) -> None:
        """Called when exiting service."""
        # Stop background music when leaving service
        if self.background_music_playing:
            assets.stop_sound("background_music")
            self.background_music_playing = False
    
    def update(self, dt: float) -> None:
        """Update service state."""
        modifiers = self.upgrade_manager.get_modifiers()
        
        # Update service
        events = self.service_controller.update(dt, modifiers)
        
        # Check for day end
        if events.get('day_ended'):
            results_data = {
                'day': self.app.game_data.get('day', 1),
                'customers_served': self.service_controller.customers_served,
                'tips_earned': self.service_controller.total_tips,
                'time_bonus': int(self.service_controller.time_remaining)
            }
            self.app.state_manager.change_state(StateID.DAY_RESULTS, results_data)
            return
        
        # Update chaos events
        self.chaos_manager.check_trigger(self.service_controller.time_remaining)
        chaos_events = self.chaos_manager.update(dt)
        
        # Update customer cards
        for i, card in enumerate(self.customer_cards):
            customer = self.service_controller.customer_queue.customers[i]
            card.set_customer(customer)
            card.update(dt)
        
        # Background music will loop automatically since we set loop=True when starting
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw service screen."""
        # Background sections
        # Customer queue area (left)
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, 280, 500))
        pygame.draw.line(screen, (60, 60, 70), (280, 0), (280, 500), 2)
        
        # Brewing area (middle) - wider
        pygame.draw.rect(screen, (25, 35, 45), (280, 0, 410, 500))
        pygame.draw.line(screen, (60, 60, 70), (690, 0), (690, 500), 2)
        
        # Order area (right)
        pygame.draw.rect(screen, (35, 25, 45), (690, 0, 270, 500))
        
        # Customer queue title
        font = assets.get_font('medium')
        font.render_to(screen, (10, 480), "Customer Queue", (255, 255, 255))
        
        # Customer cards
        for card in self.customer_cards:
            card.draw(screen)
            
        # Instruction text
        instruction_font = assets.get_font('small')
        instruction_font.render_to(screen, (290, 510), "Instructions: Click customer → Add ingredients → Serve", (200, 220, 200))
        
        # Recipe book panel
        self.recipe_book_panel.draw(screen)
        self.draw_recipe_book(screen)
        
        # Current recipe panel
        self.current_recipe_panel.draw(screen)
        self.draw_current_recipe(screen)
        
        # Target recipe panel (when customer selected)
        if self.service_controller.brewing_station.selected_customer_index is not None:
            self.target_recipe_panel.draw(screen)
            self.draw_target_recipe(screen)
        
        # Brewing progress (enhanced)
        if self.service_controller.brewing_station.is_brewing and self.service_controller.brewing_station.current_recipe:
            progress = self.service_controller.brewing_station.current_brew_time / self.service_controller.brewing_station.brew_time_per_step
            progress_bar = ProgressBar(300, 430, 380, 15)
            progress_bar.set_value(progress * 100)
            progress_bar.draw(screen)
            
            # Progress text
            progress_font = assets.get_font('small')
            progress_text = f"Brewing... {int(progress * 100)}%"
            progress_font.render_to(screen, (490 - len(progress_text) * 3, 410), progress_text, (255, 255, 150))
        
        # Ingredient buttons
        # Ingredient section label
        ingredient_font = assets.get_font('medium')
        ingredient_font.render_to(screen, (300, 250), "Ingredients:", (255, 255, 255))
        
        for button in self.ingredient_buttons:
            # Make selected customer's needed ingredients more obvious
            if self.service_controller.brewing_station.selected_customer_index is not None:
                customer = self.service_controller.customer_queue.customers[self.service_controller.brewing_station.selected_customer_index]
                if customer:
                    recipe = self.service_controller.recipe_book.find(customer.desired_recipe)
                    if recipe:
                        # Get ingredient name from button text
                        ingredient_name = button.text.lower().replace(" ", "_")
                        if ingredient_name in recipe.steps:
                            # Highlight needed ingredients
                            highlight_rect = button.rect.inflate(6, 6)
                            pygame.draw.rect(screen, (100, 200, 100), highlight_rect, 3)
            
            button.draw(screen)
            
            # Draw ingredient icons/symbols on buttons
            ingredient_name = button.text.lower().replace(" ", "_")
            if ingredient_name in self.ingredient_display_names:
                symbol = self.ingredient_display_names[ingredient_name].split()[0]
                symbol_font = assets.get_font('medium')
                symbol_rect = symbol_font.get_rect(symbol)
                symbol_x = button.rect.x + (button.rect.width - symbol_rect.width) // 2
                symbol_y = button.rect.y + 5
                symbol_font.render_to(screen, (symbol_x, symbol_y), symbol, (255, 255, 255))
        
        # Brew buttons
        self.serve_button.draw(screen)
        self.cancel_button.draw(screen)
        
        # Order tickets section
        font.render_to(screen, (700, 480), "Orders", (255, 255, 255))
        
        # Display customer orders (with highlighting for selected customer)
        for i, customer in enumerate(self.service_controller.customer_queue.get_active_customers()):
            if i < len(self.order_tickets):
                panel = self.order_tickets[i]
                
                # Highlight if this customer is selected
                selected = (self.service_controller.brewing_station.selected_customer_index is not None and 
                           self.service_controller.customer_queue.customers[self.service_controller.brewing_station.selected_customer_index] == customer)
                
                if selected:
                    # Draw highlight background
                    highlight_rect = panel.rect.inflate(4, 4)
                    pygame.draw.rect(screen, (100, 150, 100), highlight_rect, 3)
                
                panel.draw(screen)
                
                # Show customer name and desired recipe
                recipe = self.service_controller.recipe_book.find(customer.desired_recipe)
                recipe_name = recipe.name if recipe else "Unknown"
                order_text = f"{customer.name}:"
                recipe_text = recipe_name
                
                # Word wrap if too long
                if len(recipe_text) > 20:
                    recipe_text = recipe_text[:17] + "..."
                
                font = assets.get_font('small')
                color = (150, 255, 150) if selected else (255, 255, 255)
                font.render_to(screen, (panel.rect.x + 10, panel.rect.y + 15), order_text, color)
                font.render_to(screen, (panel.rect.x + 10, panel.rect.y + 35), recipe_text, color)
        
        # Status bar
        self.status_panel.draw(screen)
        
        # Time remaining
        time_text = f"Time: {self.service_controller.time_remaining:.1f}s"
        font.render_to(screen, (10, 510), time_text, (255, 255, 255))
        
        # Tips earned
        tips_text = f"Tips: {self.service_controller.total_tips}"
        font.render_to(screen, (120, 510), tips_text, (255, 255, 255))
        
        # Customers served
        served_text = f"Served: {self.service_controller.customers_served}"
        font.render_to(screen, (220, 510), served_text, (255, 255, 255))
        
        # Bell button
        self.bell_button.draw(screen)
        
        # Thermometer
        thermometer_img = assets.get_image("thermometer")
        screen.blit(thermometer_img, self.thermometer_rect.topleft)
        
        # Heat level indicator
        heat_ratio = self.service_controller.cafe_heat / 100.0
        heat_height = int(40 * heat_ratio)
        if heat_height > 0:
            heat_rect = pygame.Rect(785, 85 + (40 - heat_height), 14, heat_height)
            heat_color = (255, int(255 * (1 - heat_ratio)), 0)
            pygame.draw.rect(screen, heat_color, heat_rect)
        
        # Portal indicator during chaos
        if self.chaos_manager.is_active():
            portal_img = assets.get_image("portal")
            screen.blit(portal_img, (440, 150))
            
            # Portal stability if it's a portal event
            if hasattr(self.chaos_manager.current_event, 'rift_stability'):
                stability = self.chaos_manager.current_event.rift_stability
                stability_text = f"Rift Stability: {stability:.1f}%"
                font.render_to(screen, (400, 250), stability_text, (255, 100, 100))
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        # UI buttons
        self.bell_button.handle_event(event)
        self.serve_button.handle_event(event)
        self.cancel_button.handle_event(event)
        
        for button in self.ingredient_buttons:
            button.handle_event(event)
        
        # Customer selection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            
            # Check customer card clicks
            for i, card in enumerate(self.customer_cards):
                if card.rect.collidepoint(mouse_x, mouse_y) and card.customer:
                    self.select_customer(i)
                    
        # Keyboard shortcuts for common actions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.service_controller.brewing_station.current_recipe:
                self.serve_drink()
            elif event.key == pygame.K_ESCAPE:
                self.cancel_order()
    
    def draw_recipe_book(self, screen: pygame.Surface) -> None:
        """Draw the recipe book showing all available recipes."""
        recipes = [
            {"name": "Milky Way Mocha", "steps": ["beans", "milk", "stardust"]},
            {"name": "Flaming Meteor Espresso", "steps": ["beans", "meteor_shot"]},
            {"name": "Banishing Espresso", "steps": ["beans", "moonlight", "sigil"]}
        ]
        
        font = assets.get_font('small')
        start_x = 310
        start_y = 35
        
        for i, recipe in enumerate(recipes):
            y_pos = start_y + i * 25
            
            # Recipe name
            font.render_to(screen, (start_x, y_pos), recipe["name"][:18], (255, 255, 255))
            
            # Ingredient icons
            icon_x = start_x + 140
            for j, ingredient in enumerate(recipe["steps"]):
                if ingredient in self.ingredient_display_names:
                    icon = self.ingredient_display_names[ingredient].split()[0]
                    font.render_to(screen, (icon_x + j * 20, y_pos), icon, (200, 200, 100))
    
    def draw_current_recipe(self, screen: pygame.Surface) -> None:
        """Draw the current recipe being brewed."""
        font = assets.get_font('small')
        
        # Label
        font.render_to(screen, (310, 155), "Current Recipe:", (255, 255, 255))
        
        # Current ingredients
        current = self.service_controller.brewing_station.current_recipe
        if current:
            icon_x = 310
            for i, ingredient in enumerate(current):
                if ingredient in self.ingredient_display_names:
                    icon = self.ingredient_display_names[ingredient].split()[0]
                    font.render_to(screen, (icon_x + i * 30, 175), icon, (150, 255, 150))
            
            # Show "+" between ingredients and slots for remaining
            for i in range(len(current), 3):
                font.render_to(screen, (icon_x + i * 30, 175), "?", (100, 100, 100))
        else:
            font.render_to(screen, (310, 175), "Empty - Select a customer first!", (200, 200, 200))
    
    def draw_target_recipe(self, screen: pygame.Surface) -> None:
        """Draw the target recipe for selected customer."""
        customer_index = self.service_controller.brewing_station.selected_customer_index
        if customer_index is None:
            return
            
        customer = self.service_controller.customer_queue.customers[customer_index]
        if not customer:
            return
            
        recipe = self.service_controller.recipe_book.find(customer.desired_recipe)
        if not recipe:
            return
        
        font = assets.get_font('small')
        
        # Label with customer name
        font.render_to(screen, (310, 225), f"Target Recipe for {customer.name}:", (255, 255, 150))
        
        # Recipe name
        font.render_to(screen, (310, 245), recipe.name, (255, 200, 100))
        
        # Target ingredients
        icon_x = 500
        for i, ingredient in enumerate(recipe.steps):
            if ingredient in self.ingredient_display_names:
                icon = self.ingredient_display_names[ingredient].split()[0]
                font.render_to(screen, (icon_x + i * 30, 245), icon, (255, 200, 100))


class ChaosEventState(GameState):
    """Chaos event presentation screen."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize chaos event state."""
        super().__init__(app)
        self.event_text = ""
        self.continue_button = Button(430, 400, 100, 40, "Continue", self.continue_game)
        self.timer = 0.0
        self.display_duration = 3.0
        self.portal_opened = False
        self.portal_closed = False
    
    def continue_game(self) -> None:
        """Continue to service."""
        self.app.state_manager.change_state(StateID.SERVICE)
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering chaos event."""
        if data:
            self.event_text = data.get("message", "A chaos event has occurred!")
        self.timer = 0.0
        self.portal_opened = False
        self.portal_closed = False
        
        # Play portal opening sound
        assets.play_sound("whoosh", volume=0.7)
        self.portal_opened = True
    
    def on_exit(self) -> None:
        """Called when exiting chaos event."""
        pass
    
    def update(self, dt: float) -> None:
        """Update chaos event."""
        self.timer += dt
        
        # Play portal closing sound near end
        if self.timer >= self.display_duration - 0.5 and not self.portal_closed:
            assets.play_sound("whoosh", volume=0.7)
            self.portal_closed = True
        
        # Auto-continue after duration
        if self.timer >= self.display_duration:
            self.continue_game()
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw chaos event."""
        # Dark overlay
        overlay = pygame.Surface((self.app.width, self.app.height))
        overlay.set_alpha(180)
        overlay.fill((20, 0, 30))
        screen.blit(overlay, (0, 0))
        
        # Event title
        title_font = assets.get_font('title')
        title_text = "Chaos Event!"
        title_rect = title_font.get_rect(title_text)
        title_pos = (self.app.width // 2 - title_rect.width // 2, 200)
        title_font.render_to(screen, title_pos, title_text, (255, 100, 100))
        
        # Event description
        font = assets.get_font('medium')
        text_rect = font.get_rect(self.event_text)
        text_pos = (self.app.width // 2 - text_rect.width // 2, 250)
        font.render_to(screen, text_pos, self.event_text, (255, 255, 255))
        
        # Continue button
        self.continue_button.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        self.continue_button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.continue_game()


class DayResultsState(GameState):
    """Day results and earnings screen."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize day results."""
        super().__init__(app)
        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox(50, 350, 860, 140)
        self.continue_button = Button(400, 450, 160, 40, "Continue to Shop", self.continue_to_shop)
        
        # Results data
        self.day = 1
        self.customers_served = 0
        self.tips_earned = 0
        self.time_bonus = 0
        self.total_earnings = 0
    
    def continue_to_shop(self) -> None:
        """Continue to upgrade shop."""
        # Update game data
        self.app.game_data["coins"] += self.total_earnings
        self.app.state_manager.change_state(StateID.UPGRADE_SHOP, {"day": self.day})
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering day results."""
        if data:
            self.day = data.get("day", 1)
            self.customers_served = data.get("customers_served", 0)
            self.tips_earned = data.get("tips_earned", 0)
            self.time_bonus = data.get("time_bonus", 0)
        
        # Calculate total earnings
        self.total_earnings = self.tips_earned + self.time_bonus
        
        # Play ding sound when showing results
        assets.play_sound("ding", volume=0.7)
        
        # Start results dialogue
        self.dialogue_manager.start_scene(context="day_results")
    
    def on_exit(self) -> None:
        """Called when exiting day results."""
        self.dialogue_manager.end_scene()
    
    def update(self, dt: float) -> None:
        """Update day results."""
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw day results."""
        # Background
        screen.fill((25, 25, 35))
        
        # Title
        title_font = assets.get_font('title')
        title_text = f"Day {self.day} Complete!"
        title_rect = title_font.get_rect(title_text)
        title_pos = (self.app.width // 2 - title_rect.width // 2, 50)
        title_font.render_to(screen, title_pos, title_text, (255, 255, 255))
        
        # Results panel
        panel = Panel(300, 120, 360, 200, "Results")
        panel.draw(screen)
        
        # Results text
        font = assets.get_font('medium')
        y_offset = 160
        line_height = 25
        
        results = [
            f"Customers Served: {self.customers_served}",
            f"Tips Earned: {self.tips_earned} coins",
            f"Time Bonus: {self.time_bonus} coins",
            f"Total Earned: {self.total_earnings} coins"
        ]
        
        for i, line in enumerate(results):
            font.render_to(screen, (320, y_offset + i * line_height), line, (255, 255, 255))
        
        # Dialogue
        current_line = self.dialogue_manager.get_current_line()
        if current_line:
            self.dialogue_box.show_dialogue(current_line.speaker, current_line.text)
            self.dialogue_box.draw(screen)
        
        # Continue button
        self.continue_button.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        self.continue_button.handle_event(event)
        
        # Advance dialogue
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if not self.dialogue_manager.advance():
                    self.continue_to_shop()


class UpgradeShopState(GameState):
    """Upgrade shop screen."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize upgrade shop."""
        super().__init__(app)
        self.upgrade_manager = UpgradeManager()
        self.upgrade_buttons: List[Button] = []
        self.next_day_button = Button(400, 450, 160, 40, "Start Next Day", self.start_next_day)
        self.current_day = 1
    
    def start_next_day(self) -> None:
        """Start the next day."""
        # Update app modifiers from upgrades
        self.app.game_data["modifiers"] = self.upgrade_manager.get_modifiers()
        
        # Advance day
        self.current_day += 1
        self.app.game_data["day"] = self.current_day
        
        # Go to next day intro
        self.app.state_manager.change_state(StateID.DAY_INTRO, {"day": self.current_day})
    
    def purchase_upgrade(self, upgrade_id: str) -> None:
        """Purchase an upgrade."""
        coins = self.app.game_data.get("coins", 0)
        remaining_coins = self.upgrade_manager.purchase(upgrade_id, coins)
        
        if remaining_coins is not None:
            self.app.game_data["coins"] = remaining_coins
            self.init_upgrade_buttons()  # Refresh buttons
    
    def init_upgrade_buttons(self) -> None:
        """Initialize upgrade buttons."""
        self.upgrade_buttons.clear()
        available_upgrades = self.upgrade_manager.get_shop_upgrades()
        
        for i, upgrade in enumerate(available_upgrades):
            button = Button(
                200, 150 + i * 80,
                400, 60,
                f"{upgrade.name} - {upgrade.cost} coins",
                lambda uid=upgrade.id: self.purchase_upgrade(uid)
            )
            
            # Disable if can't afford
            coins = self.app.game_data.get("coins", 0)
            button.enabled = self.upgrade_manager.can_afford(upgrade.id, coins)
            
            self.upgrade_buttons.append(button)
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering shop."""
        if data:
            self.current_day = data.get("day", 1)
        
        self.init_upgrade_buttons()
    
    def on_exit(self) -> None:
        """Called when exiting shop."""
        pass
    
    def update(self, dt: float) -> None:
        """Update shop."""
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw shop."""
        # Background
        screen.fill((30, 40, 30))
        
        # Title
        title_font = assets.get_font('title')
        title_text = "Upgrade Shop"
        title_rect = title_font.get_rect(title_text)
        title_pos = (self.app.width // 2 - title_rect.width // 2, 50)
        title_font.render_to(screen, title_pos, title_text, (255, 255, 255))
        
        # Coins display
        font = assets.get_font('medium')
        coins_text = f"Coins: {self.app.game_data.get('coins', 0)}"
        font.render_to(screen, (50, 100), coins_text, (255, 215, 0))
        
        # Upgrade buttons
        for i, button in enumerate(self.upgrade_buttons):
            button.draw(screen)
            
            # Draw upgrade description
            upgrades = self.upgrade_manager.get_shop_upgrades()
            if i < len(upgrades):
                upgrade = upgrades[i]
                desc_y = button.rect.y + 25
                font = assets.get_font('small')
                font.render_to(screen, (button.rect.x + 10, desc_y), upgrade.description, (200, 200, 200))
        
        # Purchased upgrades
        purchased = self.upgrade_manager.get_purchased_upgrades()
        if purchased:
            font = assets.get_font('medium')
            font.render_to(screen, (650, 150), "Owned Upgrades:", (255, 255, 255))
            
            for i, upgrade in enumerate(purchased):
                y_pos = 180 + i * 25
                font = assets.get_font('small')
                font.render_to(screen, (650, y_pos), upgrade.name, (100, 255, 100))
        
        # Next day button
        self.next_day_button.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        for button in self.upgrade_buttons:
            button.handle_event(event)
        
        self.next_day_button.handle_event(event)


class DialogueState(GameState):
    """Full-screen dialogue state."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize dialogue state."""
        super().__init__(app)
        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox(50, 300, 860, 200)
        self.continue_button = Button(800, 450, 100, 40, "Continue", self.advance_dialogue)
        self.background_scene = None
    
    def advance_dialogue(self) -> None:
        """Advance dialogue."""
        if not self.dialogue_manager.advance():
            # Dialogue complete, return to previous state
            if self.app.state_manager.previous_state_id:
                self.app.state_manager.change_state(self.app.state_manager.previous_state_id)
            else:
                self.app.state_manager.change_state(StateID.MAIN_MENU)
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering dialogue."""
        if data:
            scene_id = data.get("scene_id")
            context = data.get("context")
            self.background_scene = data.get("background")
            
            if scene_id:
                self.dialogue_manager.start_scene(scene_id=scene_id)
            elif context:
                self.dialogue_manager.start_scene(context=context)
    
    def on_exit(self) -> None:
        """Called when exiting dialogue."""
        self.dialogue_manager.end_scene()
    
    def update(self, dt: float) -> None:
        """Update dialogue."""
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw dialogue."""
        # Background
        if self.background_scene:
            # Draw simplified background scene
            screen.fill((20, 25, 30))
        else:
            screen.fill((15, 15, 25))
        
        # Dialogue
        current_line = self.dialogue_manager.get_current_line()
        if current_line:
            self.dialogue_box.show_dialogue(current_line.speaker, current_line.text)
            self.dialogue_box.draw(screen)
            self.continue_button.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        self.continue_button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.advance_dialogue()


class PauseState(GameState):
    """Pause screen overlay."""
    
    def __init__(self, app: 'App') -> None:
        """Initialize pause state."""
        super().__init__(app)
        self.resume_button = Button(380, 200, 200, 50, "Resume", self.resume_game)
        self.menu_button = Button(380, 270, 200, 50, "Main Menu", self.return_to_menu)
        self.quit_button = Button(380, 340, 200, 50, "Quit", self.quit_game)
    
    def resume_game(self) -> None:
        """Resume the game."""
        if self.app.state_manager.previous_state_id:
            self.app.state_manager.change_state(self.app.state_manager.previous_state_id)
    
    def return_to_menu(self) -> None:
        """Return to main menu."""
        self.app.state_manager.change_state(StateID.MAIN_MENU)
    
    def quit_game(self) -> None:
        """Quit the game."""
        self.app.running = False
    
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Called when entering pause."""
        pass
    
    def on_exit(self) -> None:
        """Called when exiting pause."""
        pass
    
    def update(self, dt: float) -> None:
        """Update pause screen."""
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw pause screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.app.width, self.app.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Pause panel
        panel = Panel(300, 150, 360, 250, "Game Paused")
        panel.draw(screen)
        
        # Buttons
        self.resume_button.draw(screen)
        self.menu_button.draw(screen)
        self.quit_button.draw(screen)
        
        # Instructions
        font = assets.get_font('small')
        font.render_to(screen, (350, 420), "Press ESC to resume", (200, 200, 200))
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        self.resume_button.handle_event(event)
        self.menu_button.handle_event(event)
        self.quit_button.handle_event(event)