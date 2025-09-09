"""Service system managing customer queue and drink brewing."""
import json
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class Customer:
    """Customer entity."""
    name: str
    species: str
    quirk: Optional[str]
    patience: float
    max_patience: float
    tip_range: List[int]
    desired_recipe: Optional[str] = None
    is_visible: bool = True
    reveal_timer: float = 0.0
    
    def update(self, dt: float, modifiers: Dict[str, float]) -> None:
        """Update customer state."""
        # Patience decay
        patience_modifier = modifiers.get('patience_decay', 1.0)
        self.patience -= dt * patience_modifier
        
        # Handle ghost visibility
        if self.quirk == "invisible" and self.reveal_timer > 0:
            self.reveal_timer -= dt
            if self.reveal_timer <= 0:
                self.is_visible = False
    
    def reveal(self, duration: float = 2.0) -> None:
        """Reveal invisible customer."""
        if self.quirk == "invisible":
            self.is_visible = True
            self.reveal_timer = duration
    
    def calculate_tip(self, correct_drink: bool, remaining_patience_ratio: float) -> int:
        """Calculate tip based on service quality."""
        if not correct_drink:
            return 0
        
        base_tip = self.tip_range[0]
        bonus = int((self.tip_range[1] - self.tip_range[0]) * remaining_patience_ratio)
        return base_tip + bonus


@dataclass
class Recipe:
    """Drink recipe."""
    id: str
    name: str
    steps: List[str]
    difficulty: int
    
    def matches(self, steps: List[str]) -> bool:
        """Check if provided steps match recipe."""
        return steps == self.steps


class RecipeBook:
    """Manages all recipes."""
    
    def __init__(self) -> None:
        """Initialize recipe book."""
        self.recipes: Dict[str, Recipe] = {}
        self.load_recipes()
    
    def load_recipes(self) -> None:
        """Load recipes from JSON."""
        try:
            with open('data/recipes.json', 'r') as f:
                data = json.load(f)
                for recipe_data in data:
                    recipe = Recipe(**recipe_data)
                    self.recipes[recipe.id] = recipe
        except Exception as e:
            print(f"Failed to load recipes: {e}")
    
    def find(self, recipe_id: str) -> Optional[Recipe]:
        """Find recipe by ID."""
        return self.recipes.get(recipe_id)
    
    def get_random_recipe(self) -> Recipe:
        """Get random recipe (excluding special ones)."""
        regular_recipes = [r for r in self.recipes.values() 
                          if not r.id.startswith('banishing')]
        return random.choice(regular_recipes)


class CustomerQueue:
    """Manages customer queue."""
    
    def __init__(self, max_size: int = 5) -> None:
        """Initialize queue."""
        self.customers: List[Optional[Customer]] = [None] * max_size
        self.max_size = max_size
    
    def add_customer(self, customer: Customer) -> bool:
        """Add customer to queue. Returns True if successful."""
        for i in range(self.max_size):
            if self.customers[i] is None:
                self.customers[i] = customer
                return True
        return False
    
    def remove_customer(self, index: int) -> Optional[Customer]:
        """Remove and return customer at index."""
        if 0 <= index < self.max_size:
            customer = self.customers[index]
            self.customers[index] = None
            return customer
        return None
    
    def get_active_customers(self) -> List[Customer]:
        """Get list of active customers."""
        return [c for c in self.customers if c is not None]
    
    def update(self, dt: float, modifiers: Dict[str, float]) -> List[Customer]:
        """Update all customers, return list of customers who left."""
        left_customers = []
        for i in range(self.max_size):
            if self.customers[i]:
                self.customers[i].update(dt, modifiers)
                if self.customers[i].patience <= 0:
                    left_customers.append(self.customers[i])
                    self.customers[i] = None
        return left_customers


class BrewingStation:
    """Manages drink brewing process."""
    
    def __init__(self) -> None:
        """Initialize brewing station."""
        self.current_recipe: List[str] = []
        self.available_ingredients = ["beans", "milk", "stardust", "meteor_shot", "moonlight", "sigil"]
        self.brew_time_per_step = 1.2
        self.current_brew_time = 0.0
        self.is_brewing = False
        self.selected_customer_index: Optional[int] = None
    
    def start_order(self, customer_index: int) -> None:
        """Start brewing for a customer."""
        self.selected_customer_index = customer_index
        self.current_recipe = []
        self.is_brewing = True
        self.current_brew_time = 0.0
    
    def add_ingredient(self, ingredient: str) -> bool:
        """Add ingredient to current recipe."""
        if ingredient in self.available_ingredients and len(self.current_recipe) < 3:
            self.current_recipe.append(ingredient)
            self.current_brew_time = 0.0
            return True
        return False
    
    def update(self, dt: float, modifiers: Dict[str, float]) -> bool:
        """Update brewing progress. Returns True when step complete."""
        if self.is_brewing and self.current_recipe:
            brew_speed = modifiers.get('brew_speed', 1.0)
            self.current_brew_time += dt * brew_speed
            if self.current_brew_time >= self.brew_time_per_step:
                return True
        return False
    
    def complete_order(self) -> List[str]:
        """Complete and return the current recipe."""
        recipe = self.current_recipe.copy()
        self.current_recipe = []
        self.is_brewing = False
        self.selected_customer_index = None
        return recipe
    
    def cancel_order(self) -> None:
        """Cancel current order."""
        self.current_recipe = []
        self.is_brewing = False
        self.selected_customer_index = None


class ServiceController:
    """Main service controller."""
    
    def __init__(self) -> None:
        """Initialize service controller."""
        self.recipe_book = RecipeBook()
        self.customer_queue = CustomerQueue()
        self.brewing_station = BrewingStation()
        self.customer_pool: List[Dict[str, Any]] = []
        self.load_customers()
        
        # Service state
        self.day_time = 90.0  # 90 seconds per day
        self.time_remaining = self.day_time
        self.customers_served = 0
        self.total_tips = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 12.0  # Spawn customer every 12 seconds
        self.cafe_heat = 0.0  # For fire elemental
        self.active = False
    
    def load_customers(self) -> None:
        """Load customer data from JSON."""
        try:
            with open('data/customers.json', 'r') as f:
                self.customer_pool = json.load(f)
        except Exception as e:
            print(f"Failed to load customers: {e}")
    
    def start_day(self, day: int) -> None:
        """Start a new service day."""
        self.time_remaining = self.day_time
        self.customers_served = 0
        self.total_tips = 0
        self.spawn_timer = 2.0  # First customer after 2 seconds
        self.cafe_heat = 0.0
        self.active = True
        
        # Clear queue
        self.customer_queue.customers = [None] * self.customer_queue.max_size
        
        # Spawn initial customer
        self.spawn_customer()
    
    def spawn_customer(self) -> bool:
        """Spawn a new customer."""
        if not self.customer_pool or not self.active:
            return False
        
        # Pick random customer template
        template = random.choice(self.customer_pool)
        
        # Create customer instance
        customer = Customer(
            name=template['name'],
            species=template['species'],
            quirk=template['quirk'],
            patience=float(template['patience']),
            max_patience=float(template['patience']),
            tip_range=template['tip'],
            desired_recipe=self.recipe_book.get_random_recipe().id
        )
        
        # Make ghost invisible initially
        if customer.quirk == "invisible":
            customer.is_visible = False
        
        return self.customer_queue.add_customer(customer)
    
    def update(self, dt: float, modifiers: Dict[str, float]) -> Dict[str, Any]:
        """Update service state. Returns events that occurred."""
        events = {
            'customers_left': [],
            'day_ended': False
        }
        
        if not self.active:
            return events
        
        # Update time
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.active = False
            events['day_ended'] = True
        
        # Spawn timer
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and self.customers_served + len(self.customer_queue.get_active_customers()) < 8:
            if self.spawn_customer():
                self.spawn_timer = self.spawn_interval + random.uniform(-2, 2)
        
        # Update customers
        left_customers = self.customer_queue.update(dt, modifiers)
        events['customers_left'] = left_customers
        
        # Update brewing
        self.brewing_station.update(dt, modifiers)
        
        # Update cafe heat
        has_fire_elemental = any(c and c.species == "fire_elemental" 
                               for c in self.customer_queue.customers)
        if has_fire_elemental:
            self.cafe_heat = min(100, self.cafe_heat + dt * 10)
        else:
            self.cafe_heat = max(0, self.cafe_heat - dt * 5)
        
        return events
    
    def serve_drink(self, recipe_steps: List[str]) -> Dict[str, Any]:
        """Serve drink to selected customer."""
        result = {
            'success': False,
            'tip': 0,
            'message': ''
        }
        
        customer_index = self.brewing_station.selected_customer_index
        if customer_index is None:
            return result
        
        customer = self.customer_queue.customers[customer_index]
        if not customer:
            return result
        
        # Check if recipe matches
        desired_recipe = self.recipe_book.find(customer.desired_recipe)
        correct = desired_recipe and desired_recipe.matches(recipe_steps)
        
        # Calculate tip
        patience_ratio = customer.patience / customer.max_patience
        tip = customer.calculate_tip(correct, patience_ratio)
        
        # Update stats
        self.customers_served += 1
        self.total_tips += tip
        
        # Remove customer
        self.customer_queue.remove_customer(customer_index)
        
        result['success'] = correct
        result['tip'] = tip
        if correct:
            result['message'] = f"{customer.name} loved their {desired_recipe.name}!"
        else:
            result['message'] = f"{customer.name} didn't get what they ordered..."
        
        return result
    
    def ring_bell(self) -> None:
        """Ring bell to reveal ghost customers."""
        for customer in self.customer_queue.customers:
            if customer and customer.quirk == "invisible":
                customer.reveal()
    
    def get_ice_melt_rate(self) -> float:
        """Get ice melt rate based on cafe heat."""
        return self.cafe_heat / 100.0  # 0-1 range