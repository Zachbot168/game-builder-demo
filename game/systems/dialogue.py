"""Simple dialogue system for story moments."""
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DialogueLine:
    """Single line of dialogue."""
    speaker: str
    text: str


@dataclass 
class DialogueScene:
    """Complete dialogue scene."""
    id: str
    lines: List[DialogueLine]
    context: str  # "day_intro" or "day_results"


class DialogueManager:
    """Manages dialogue scenes."""
    
    def __init__(self) -> None:
        """Initialize dialogue manager."""
        self.scenes: Dict[str, List[DialogueScene]] = {
            "day_intro": [],
            "day_results": []
        }
        self._init_dialogue()
        self.current_scene: Optional[DialogueScene] = None
        self.current_line_index = 0
    
    def _init_dialogue(self) -> None:
        """Initialize dialogue content."""
        # Day intro scenes
        self.scenes["day_intro"] = [
            DialogueScene(
                id="intro_1",
                context="day_intro",
                lines=[
                    DialogueLine("Mysterious Voice", "The veil between worlds grows thin today..."),
                    DialogueLine("You", "Just another day at Eldritch Espresso!"),
                    DialogueLine("Mysterious Voice", "Indeed. The coffee must flow.")
                ]
            ),
            DialogueScene(
                id="intro_2",
                context="day_intro",
                lines=[
                    DialogueLine("Azzu", "The stars align favorably for lattes today."),
                    DialogueLine("You", "I'll keep that in mind!"),
                ]
            ),
            DialogueScene(
                id="intro_3", 
                context="day_intro",
                lines=[
                    DialogueLine("Ignis", "The flames speak of busy times ahead."),
                    DialogueLine("You", "Let's hope they're good tippers!"),
                    DialogueLine("Ignis", "*crackles warmly*")
                ]
            )
        ]
        
        # Day results scenes
        self.scenes["day_results"] = [
            DialogueScene(
                id="results_1",
                context="day_results",
                lines=[
                    DialogueLine("Whim", "The ethereal beans were perfectly balanced today."),
                    DialogueLine("You", "Thanks! I've been practicing."),
                    DialogueLine("Whim", "*phases through the wall contentedly*")
                ]
            ),
            DialogueScene(
                id="results_2",
                context="day_results",
                lines=[
                    DialogueLine("Elder Thing", "Ph'nglui mglw'nafh Caffeine R'lyeh wgah'nagl fhtagn!"),
                    DialogueLine("You", "...I'll take that as a compliment?"),
                ]
            ),
            DialogueScene(
                id="results_3",
                context="day_results",
                lines=[
                    DialogueLine("Cosmic Barista", "Your brewing resonates across dimensions."),
                    DialogueLine("You", "Just doing my best!"),
                    DialogueLine("Cosmic Barista", "The multiverse appreciates good coffee.")
                ]
            )
        ]
    
    def get_random_scene(self, context: str) -> Optional[DialogueScene]:
        """Get a random dialogue scene for the context."""
        if context in self.scenes and self.scenes[context]:
            return random.choice(self.scenes[context])
        return None
    
    def start_scene(self, scene_id: Optional[str] = None, context: Optional[str] = None) -> bool:
        """Start a dialogue scene."""
        if scene_id:
            # Find specific scene
            for ctx_scenes in self.scenes.values():
                for scene in ctx_scenes:
                    if scene.id == scene_id:
                        self.current_scene = scene
                        self.current_line_index = 0
                        return True
        elif context:
            # Get random scene for context
            self.current_scene = self.get_random_scene(context)
            self.current_line_index = 0
            return self.current_scene is not None
        
        return False
    
    def get_current_line(self) -> Optional[DialogueLine]:
        """Get current dialogue line."""
        if not self.current_scene or self.current_line_index >= len(self.current_scene.lines):
            return None
        
        return self.current_scene.lines[self.current_line_index]
    
    def advance(self) -> bool:
        """Advance to next line. Returns False if scene complete."""
        if not self.current_scene:
            return False
        
        self.current_line_index += 1
        return self.current_line_index < len(self.current_scene.lines)
    
    def is_complete(self) -> bool:
        """Check if current scene is complete."""
        if not self.current_scene:
            return True
        
        return self.current_line_index >= len(self.current_scene.lines)
    
    def end_scene(self) -> None:
        """End current scene."""
        self.current_scene = None
        self.current_line_index = 0