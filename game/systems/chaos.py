"""Chaos event system for managing special events during service."""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class ChaosEvent(ABC):
    """Base class for chaos events."""
    
    def __init__(self) -> None:
        """Initialize chaos event."""
        self.active = False
        self.resolved = False
        self.timer = 0.0
        
    @abstractmethod
    def start(self) -> None:
        """Start the chaos event."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> Dict[str, Any]:
        """Update chaos event. Returns event data."""
        pass
    
    @abstractmethod
    def can_resolve(self, action: str, data: Any) -> bool:
        """Check if action can resolve event."""
        pass
    
    @abstractmethod
    def resolve(self) -> Dict[str, Any]:
        """Resolve the chaos event."""
        pass


class PortalEvent(ChaosEvent):
    """Portal chaos event where pastries float away."""
    
    def __init__(self) -> None:
        """Initialize portal event."""
        super().__init__()
        self.rift_stability = 100.0  # Drains over time
        self.drain_rate = 5.0  # Per second
        self.pastries_lost = 0
        self.max_pastries_lost = 10
        
    def start(self) -> None:
        """Start portal event."""
        self.active = True
        self.resolved = False
        self.rift_stability = 100.0
        self.pastries_lost = 0
        
    def update(self, dt: float) -> Dict[str, Any]:
        """Update portal state."""
        if not self.active or self.resolved:
            return {}
        
        # Drain rift stability
        self.rift_stability = max(0, self.rift_stability - self.drain_rate * dt)
        
        # Lose pastries periodically
        self.timer += dt
        if self.timer >= 2.0:  # Every 2 seconds
            self.timer = 0.0
            self.pastries_lost += 1
            
        # Check fail condition
        if self.rift_stability <= 0 or self.pastries_lost >= self.max_pastries_lost:
            self.active = False
            return {
                'event': 'portal_failed',
                'pastries_lost': self.pastries_lost,
                'message': 'The portal consumed too many pastries!'
            }
        
        return {
            'rift_stability': self.rift_stability,
            'pastries_lost': self.pastries_lost
        }
    
    def can_resolve(self, action: str, data: Any) -> bool:
        """Check if banishing espresso can close portal."""
        if action != "serve_drink" or not isinstance(data, list):
            return False
        
        # Check if it's the banishing espresso recipe
        return data == ["beans", "moonlight", "sigil"]
    
    def resolve(self) -> Dict[str, Any]:
        """Resolve portal event."""
        self.resolved = True
        self.active = False
        
        # Bonus based on remaining stability
        bonus = int(self.rift_stability / 10)
        
        return {
            'event': 'portal_closed',
            'bonus': bonus,
            'message': f'Portal banished! Saved {10 - self.pastries_lost} pastries!'
        }


class ChaosManager:
    """Manages chaos events during service."""
    
    def __init__(self) -> None:
        """Initialize chaos manager."""
        self.current_event: Optional[ChaosEvent] = None
        self.event_triggered = False
        self.trigger_time = 45.0  # Trigger at day midpoint
        
    def reset(self) -> None:
        """Reset for new day."""
        self.current_event = None
        self.event_triggered = False
        
    def check_trigger(self, time_remaining: float) -> bool:
        """Check if chaos event should trigger."""
        if not self.event_triggered and time_remaining <= self.trigger_time:
            self.event_triggered = True
            self.current_event = PortalEvent()
            self.current_event.start()
            return True
        return False
    
    def update(self, dt: float) -> Dict[str, Any]:
        """Update current chaos event."""
        if self.current_event and self.current_event.active:
            return self.current_event.update(dt)
        return {}
    
    def try_resolve(self, action: str, data: Any) -> Optional[Dict[str, Any]]:
        """Try to resolve current event with action."""
        if not self.current_event or not self.current_event.active:
            return None
        
        if self.current_event.can_resolve(action, data):
            return self.current_event.resolve()
        
        return None
    
    def is_active(self) -> bool:
        """Check if chaos event is active."""
        return self.current_event is not None and self.current_event.active