"""Upgrade system for permanent improvements."""
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass


@dataclass
class Upgrade:
    """Upgrade definition."""
    id: str
    name: str
    description: str
    cost: int
    effect_key: str
    effect_value: float
    icon: Optional[str] = None


class UpgradeManager:
    """Manages upgrades and their effects."""
    
    def __init__(self) -> None:
        """Initialize upgrade manager."""
        self.available_upgrades: Dict[str, Upgrade] = {}
        self.purchased_upgrades: List[str] = []
        self.modifiers: Dict[str, float] = {
            'brew_speed': 1.0,
            'patience_decay': 1.0,
            'tip_multiplier': 1.0
        }
        
        # Initialize available upgrades
        self._init_upgrades()
    
    def _init_upgrades(self) -> None:
        """Initialize available upgrades."""
        self.available_upgrades = {
            "enchanted_grinder": Upgrade(
                id="enchanted_grinder",
                name="Enchanted Grinder",
                description="Reduces brew time by 20%",
                cost=15,
                effect_key="brew_speed",
                effect_value=1.2,
                icon="upgrade_grinder"
            ),
            "calming_fern": Upgrade(
                id="calming_fern",
                name="Calming Fern",
                description="Slows patience decay by 15%",
                cost=20,
                effect_key="patience_decay",
                effect_value=0.85,
                icon="upgrade_fern"
            )
        }
    
    def can_afford(self, upgrade_id: str, coins: int) -> bool:
        """Check if player can afford upgrade."""
        upgrade = self.available_upgrades.get(upgrade_id)
        return upgrade is not None and coins >= upgrade.cost
    
    def is_purchased(self, upgrade_id: str) -> bool:
        """Check if upgrade is already purchased."""
        return upgrade_id in self.purchased_upgrades
    
    def purchase(self, upgrade_id: str, coins: int) -> Optional[int]:
        """Purchase upgrade. Returns remaining coins or None if failed."""
        if upgrade_id in self.purchased_upgrades:
            return None  # Already purchased
        
        upgrade = self.available_upgrades.get(upgrade_id)
        if not upgrade or coins < upgrade.cost:
            return None  # Can't afford or doesn't exist
        
        # Purchase upgrade
        self.purchased_upgrades.append(upgrade_id)
        self._apply_upgrade(upgrade)
        
        return coins - upgrade.cost
    
    def _apply_upgrade(self, upgrade: Upgrade) -> None:
        """Apply upgrade effects."""
        if upgrade.effect_key in self.modifiers:
            if upgrade.effect_key == "patience_decay":
                # Multiply for decay (lower is better)
                self.modifiers[upgrade.effect_key] *= upgrade.effect_value
            else:
                # Multiply for other effects (higher is better)
                self.modifiers[upgrade.effect_key] *= upgrade.effect_value
    
    def get_modifiers(self) -> Dict[str, float]:
        """Get current modifiers."""
        return self.modifiers.copy()
    
    def get_shop_upgrades(self) -> List[Upgrade]:
        """Get upgrades available for purchase."""
        return [u for u in self.available_upgrades.values() 
               if u.id not in self.purchased_upgrades]
    
    def get_purchased_upgrades(self) -> List[Upgrade]:
        """Get list of purchased upgrades."""
        return [self.available_upgrades[uid] for uid in self.purchased_upgrades 
               if uid in self.available_upgrades]
    
    def reset(self) -> None:
        """Reset all upgrades (for new game)."""
        self.purchased_upgrades.clear()
        self.modifiers = {
            'brew_speed': 1.0,
            'patience_decay': 1.0,
            'tip_multiplier': 1.0
        }