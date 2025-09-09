"""UI widget components for the game."""
import pygame
from typing import Optional, Tuple, Callable, List
from core.assets import assets


class Button:
    """Clickable button widget."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Optional[Callable[[], None]] = None) -> None:
        """Initialize button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.state = "normal"  # normal, hover, pressed
        self.enabled = True
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.state = "hover"
            else:
                self.state = "normal"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = "pressed"
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.state == "pressed":
                self.state = "hover"
                if self.callback:
                    self.callback()
                return True
            self.state = "normal"
        
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw button."""
        # Get appropriate button image
        img_name = f"button_{self.state}" if self.enabled else "button_normal"
        button_img = assets.get_image(img_name)
        
        # Scale to button size
        scaled_img = pygame.transform.scale(button_img, (self.rect.width, self.rect.height))
        screen.blit(scaled_img, self.rect.topleft)
        
        # Draw text
        font = assets.get_font('medium')
        text_color = (255, 255, 255) if self.enabled else (150, 150, 150)
        text_rect = font.get_rect(self.text)
        text_pos = (self.rect.centerx - text_rect.width // 2, 
                   self.rect.centery - text_rect.height // 2)
        font.render_to(screen, text_pos, self.text, text_color)


class ProgressBar:
    """Progress/timer bar widget."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 max_value: float = 100.0, color: Tuple[int, int, int] = (100, 200, 100)) -> None:
        """Initialize progress bar."""
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = max_value
        self.color = color
        self.bg_color = (40, 40, 40)
        self.border_color = (80, 80, 80)
        
    def set_value(self, value: float) -> None:
        """Set current value."""
        self.current_value = max(0, min(value, self.max_value))
    
    def update_value(self, delta: float) -> None:
        """Update value by delta."""
        self.set_value(self.current_value + delta)
    
    def get_percentage(self) -> float:
        """Get fill percentage (0-1)."""
        return self.current_value / self.max_value if self.max_value > 0 else 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw progress bar."""
        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # Progress fill
        fill_width = int(self.rect.width * self.get_percentage())
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(screen, self.color, fill_rect)
        
        # Border
        pygame.draw.rect(screen, self.border_color, self.rect, 2)


class CustomerCard:
    """Card displaying customer info in queue."""
    
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize customer card."""
        self.rect = pygame.Rect(x, y, width, height)
        self.customer = None
        self.patience_bar = ProgressBar(x + 5, y + height - 15, width - 10, 10)
        self.visible = True
        
    def set_customer(self, customer: Optional['Customer']) -> None:
        """Set customer to display."""
        self.customer = customer
        if customer:
            self.patience_bar.max_value = customer.max_patience
            self.patience_bar.current_value = customer.patience
            # Set patience bar color based on urgency
            if customer.patience / customer.max_patience < 0.3:
                self.patience_bar.color = (255, 50, 50)  # Red
            elif customer.patience / customer.max_patience < 0.6:
                self.patience_bar.color = (255, 200, 50)  # Yellow
            else:
                self.patience_bar.color = (100, 200, 100)  # Green
    
    def update(self, dt: float) -> None:
        """Update card."""
        if self.customer:
            self.patience_bar.set_value(self.customer.patience)
            # Update color
            ratio = self.customer.patience / self.customer.max_patience
            if ratio < 0.3:
                self.patience_bar.color = (255, 50, 50)  # Red
            elif ratio < 0.6:
                self.patience_bar.color = (255, 200, 50)  # Yellow
            else:
                self.patience_bar.color = (100, 200, 100)  # Green
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw customer card."""
        if not self.customer or not self.visible:
            return
        
        # Card background
        panel_img = assets.get_image("panel")
        scaled_panel = pygame.transform.scale(panel_img, (self.rect.width, self.rect.height))
        screen.blit(scaled_panel, self.rect.topleft)
        
        # Customer sprite
        sprite = assets.get_image(f"customer_{self.customer.species}")
        sprite_rect = sprite.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
        screen.blit(sprite, sprite_rect)
        
        # Customer name
        font = assets.get_font('small')
        name_rect = font.get_rect(self.customer.name)
        name_pos = (self.rect.centerx - name_rect.width // 2, self.rect.y + 5)
        font.render_to(screen, name_pos, self.customer.name, (255, 255, 255))
        
        # Patience bar
        self.patience_bar.draw(screen)


class Panel:
    """Generic UI panel."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 title: str = "", color: Optional[Tuple[int, int, int]] = None) -> None:
        """Initialize panel."""
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.color = color or (40, 40, 50)
        self.border_color = (60, 60, 70)
        self.title_color = (255, 255, 255)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw panel."""
        # Background
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        
        # Border
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=8)
        
        # Title
        if self.title:
            font = assets.get_font('medium')
            title_rect = font.get_rect(self.title)
            title_pos = (self.rect.centerx - title_rect.width // 2, self.rect.y + 10)
            font.render_to(screen, title_pos, self.title, self.title_color)


class Label:
    """Simple text label."""
    
    def __init__(self, x: int, y: int, text: str, font_name: str = 'default',
                 color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Initialize label."""
        self.x = x
        self.y = y
        self.text = text
        self.font_name = font_name
        self.color = color
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw label."""
        font = assets.get_font(self.font_name)
        font.render_to(screen, (self.x, self.y), self.text, self.color)
    
    def set_text(self, text: str) -> None:
        """Update label text."""
        self.text = text


class DialogueBox:
    """Box for displaying dialogue."""
    
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize dialogue box."""
        self.rect = pygame.Rect(x, y, width, height)
        self.speaker = ""
        self.text = ""
        self.visible = False
        
    def show_dialogue(self, speaker: str, text: str) -> None:
        """Show dialogue."""
        self.speaker = speaker
        self.text = text
        self.visible = True
    
    def hide(self) -> None:
        """Hide dialogue box."""
        self.visible = False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw dialogue box."""
        if not self.visible:
            return
        
        # Background
        pygame.draw.rect(screen, (20, 20, 30), self.rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), self.rect, 3, border_radius=10)
        
        # Speaker name
        if self.speaker:
            font = assets.get_font('medium')
            speaker_pos = (self.rect.x + 20, self.rect.y + 10)
            font.render_to(screen, speaker_pos, self.speaker + ":", (255, 200, 100))
        
        # Text (simple word wrap)
        font = assets.get_font('default')
        y_offset = 40 if self.speaker else 20
        words = self.text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.get_rect(test_line).width < self.rect.width - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:5]):  # Max 5 lines
            text_pos = (self.rect.x + 20, self.rect.y + y_offset + i * 20)
            font.render_to(screen, text_pos, line, (255, 255, 255))