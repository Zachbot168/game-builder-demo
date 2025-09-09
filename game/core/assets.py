"""Asset loading and management with fallback shape generation."""
import pygame
import os
from typing import Dict, Optional, Tuple
import pygame.freetype


class Assets:
    """Manages game assets with fallback shape generation."""
    
    def __init__(self) -> None:
        """Initialize asset manager."""
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.freetype.Font] = {}
        
        # Initialize pygame font system
        pygame.freetype.init()
        
        # Load default fonts
        self.fonts['default'] = pygame.freetype.Font(None, 16)
        self.fonts['title'] = pygame.freetype.Font(None, 32)
        self.fonts['medium'] = pygame.freetype.Font(None, 20)
        self.fonts['small'] = pygame.freetype.Font(None, 14)
        
        # Generate fallback shapes
        self._generate_fallback_shapes()
        
        # Generate fallback sounds
        self._generate_fallback_sounds()
    
    def _generate_fallback_shapes(self) -> None:
        """Generate fallback shapes for missing sprites."""
        # Customer silhouettes
        self._create_customer_shape("tentacled", (100, 150, 200), "circle")
        self._create_customer_shape("fire_elemental", (255, 100, 50), "flame")
        self._create_customer_shape("ghost", (220, 220, 255), "ghost")
        
        # Ingredient icons
        self._create_ingredient_icon("beans", (101, 67, 33))
        self._create_ingredient_icon("milk", (255, 255, 240))
        self._create_ingredient_icon("stardust", (255, 215, 0))
        self._create_ingredient_icon("meteor_shot", (255, 69, 0))
        self._create_ingredient_icon("moonlight", (192, 192, 255))
        self._create_ingredient_icon("sigil", (148, 0, 211))
        
        # UI elements
        self._create_ui_element("button_normal", (80, 80, 100))
        self._create_ui_element("button_hover", (100, 100, 120))
        self._create_ui_element("button_pressed", (60, 60, 80))
        self._create_ui_element("panel", (40, 40, 50))
        
        # Special effects
        self._create_portal_sprite()
        self._create_thermometer_icon()
    
    def _create_customer_shape(self, name: str, color: Tuple[int, int, int], shape: str) -> None:
        """Create a customer silhouette shape."""
        surf = pygame.Surface((60, 80), pygame.SRCALPHA)
        
        if shape == "circle":
            # Tentacled creature
            pygame.draw.circle(surf, color, (30, 30), 25)
            # Tentacles
            for i in range(4):
                start_x = 30 + (i - 1.5) * 10
                pygame.draw.arc(surf, color, (start_x - 5, 40, 10, 30), 0, 3.14, 3)
        elif shape == "flame":
            # Fire elemental
            points = [(30, 10), (40, 30), (35, 50), (30, 60), (25, 50), (20, 30)]
            pygame.draw.polygon(surf, color, points)
            # Inner flame
            inner_color = (255, 200, 100)
            inner_points = [(30, 20), (35, 30), (32, 40), (30, 45), (28, 40), (25, 30)]
            pygame.draw.polygon(surf, inner_color, inner_points)
        elif shape == "ghost":
            # Ghost shape
            pygame.draw.ellipse(surf, color, (10, 10, 40, 40))
            # Wavy bottom
            pygame.draw.circle(surf, color, (20, 45), 10)
            pygame.draw.circle(surf, color, (30, 45), 10)
            pygame.draw.circle(surf, color, (40, 45), 10)
        
        self.images[f"customer_{name}"] = surf
    
    def _create_ingredient_icon(self, name: str, color: Tuple[int, int, int]) -> None:
        """Create an ingredient icon."""
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        if name == "beans":
            # Coffee beans
            pygame.draw.ellipse(surf, color, (8, 8, 16, 20))
            pygame.draw.line(surf, (50, 30, 10), (16, 8), (16, 28), 2)
        elif name in ["milk", "moonlight"]:
            # Liquid drop
            pygame.draw.circle(surf, color, (16, 12), 10)
            points = [(16, 20), (10, 16), (16, 28), (22, 16)]
            pygame.draw.polygon(surf, color, points)
        elif name in ["stardust", "meteor_shot"]:
            # Star shape
            center = (16, 16)
            size = 12
            points = []
            for i in range(10):
                angle = i * 3.14159 / 5
                if i % 2 == 0:
                    r = size
                else:
                    r = size * 0.5
                x = center[0] + r * pygame.math.Vector2(0, -1).rotate_rad(angle).x
                y = center[1] + r * pygame.math.Vector2(0, -1).rotate_rad(angle).y
                points.append((x, y))
            pygame.draw.polygon(surf, color, points)
        elif name == "sigil":
            # Mystical symbol
            pygame.draw.circle(surf, color, (16, 16), 12, 2)
            # Inner triangle
            points = [(16, 8), (8, 24), (24, 24)]
            pygame.draw.polygon(surf, color, points, 2)
        
        self.images[f"ingredient_{name}"] = surf
    
    def _create_ui_element(self, name: str, color: Tuple[int, int, int]) -> None:
        """Create a UI element."""
        if name.startswith("button"):
            surf = pygame.Surface((120, 40), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, 120, 40), border_radius=5)
            pygame.draw.rect(surf, (color[0] + 20, color[1] + 20, color[2] + 20), 
                           (0, 0, 120, 40), 2, border_radius=5)
        else:  # panel
            surf = pygame.Surface((200, 150), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, 200, 150), border_radius=8)
            pygame.draw.rect(surf, (60, 60, 70), (0, 0, 200, 150), 2, border_radius=8)
        
        self.images[name] = surf
    
    def _create_portal_sprite(self) -> None:
        """Create portal animation sprite."""
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        # Outer ring
        pygame.draw.circle(surf, (148, 0, 211), (40, 40), 35, 5)
        # Inner swirl
        pygame.draw.circle(surf, (186, 85, 211), (40, 40), 25, 3)
        pygame.draw.circle(surf, (221, 160, 221), (40, 40), 15, 2)
        self.images["portal"] = surf
    
    def _create_thermometer_icon(self) -> None:
        """Create thermometer icon."""
        surf = pygame.Surface((24, 48), pygame.SRCALPHA)
        # Thermometer body
        pygame.draw.rect(surf, (200, 200, 200), (8, 8, 8, 28))
        pygame.draw.circle(surf, (200, 200, 200), (12, 38), 8)
        # Mercury
        pygame.draw.rect(surf, (255, 0, 0), (10, 20, 4, 16))
        pygame.draw.circle(surf, (255, 0, 0), (12, 38), 5)
        self.images["thermometer"] = surf
    
    def load_image(self, name: str, path: str) -> pygame.Surface:
        """Load an image from file or return existing."""
        if name in self.images:
            return self.images[name]
        
        try:
            image = pygame.image.load(path).convert_alpha()
            self.images[name] = image
            return image
        except:
            # Return a placeholder
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (255, 0, 255), (0, 0, 64, 64))
            pygame.draw.line(placeholder, (0, 0, 0), (0, 0), (64, 64), 2)
            pygame.draw.line(placeholder, (0, 0, 0), (64, 0), (0, 64), 2)
            return placeholder
    
    def load_sound(self, name: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound from file or return existing."""
        if name in self.sounds:
            return self.sounds[name]
        
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return sound
        except:
            return None
    
    def get_image(self, name: str) -> pygame.Surface:
        """Get an image by name."""
        return self.images.get(name, self._create_placeholder())
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a sound by name."""
        return self.sounds.get(name)
    
    def get_font(self, name: str = 'default') -> pygame.freetype.Font:
        """Get a font by name."""
        return self.fonts.get(name, self.fonts['default'])
    
    def _create_placeholder(self) -> pygame.Surface:
        """Create a placeholder surface."""
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 255), (0, 0, 64, 64), 2)
        return surf
    
    def _generate_fallback_sounds(self) -> None:
        """Generate simple placeholder sounds."""
        try:
            import numpy as np
            
            # Generate simple tones
            sample_rate = 22050
            duration = 0.2  # 200ms
            
            # Ding sound (order ready) - 880Hz
            self._generate_tone("ding", 880, duration, sample_rate)
            
            # Whoosh sound (portal) - sweep from 200 to 100 Hz
            self._generate_sweep("whoosh", 200, 100, 0.5, sample_rate)
            
            # Background loop - simple chord
            self._generate_background("background_music", 2.0, sample_rate)
            
        except ImportError:
            # If numpy not available, create silent sounds
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            silence = pygame.sndarray.make_sound(np.zeros((22050, 2), dtype=np.int16))
            self.sounds["ding"] = silence
            self.sounds["whoosh"] = silence
            self.sounds["background_music"] = silence
    
    def _generate_tone(self, name: str, frequency: float, duration: float, sample_rate: int) -> None:
        """Generate a simple tone."""
        try:
            import numpy as np
            samples = int(duration * sample_rate)
            waves = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
            
            # Apply envelope
            envelope = np.exp(-3 * np.linspace(0, duration, samples))
            waves = waves * envelope
            
            # Convert to 16-bit integers
            waves = (waves * 32767).astype(np.int16)
            stereo_waves = np.column_stack((waves, waves))
            
            # Create sound
            sound = pygame.sndarray.make_sound(stereo_waves)
            self.sounds[name] = sound
        except:
            pass
    
    def _generate_sweep(self, name: str, start_freq: float, end_freq: float, 
                       duration: float, sample_rate: int) -> None:
        """Generate a frequency sweep sound."""
        try:
            import numpy as np
            samples = int(duration * sample_rate)
            t = np.linspace(0, duration, samples)
            
            # Linear frequency sweep
            frequency = np.linspace(start_freq, end_freq, samples)
            phase = 2 * np.pi * np.cumsum(frequency) / sample_rate
            waves = np.sin(phase)
            
            # Apply envelope
            envelope = np.exp(-2 * t)
            waves = waves * envelope
            
            # Convert to 16-bit integers
            waves = (waves * 16383).astype(np.int16)
            stereo_waves = np.column_stack((waves, waves))
            
            # Create sound
            sound = pygame.sndarray.make_sound(stereo_waves)
            self.sounds[name] = sound
        except:
            pass
    
    def _generate_background(self, name: str, duration: float, sample_rate: int) -> None:
        """Generate simple background music loop."""
        try:
            import numpy as np
            samples = int(duration * sample_rate)
            t = np.linspace(0, duration, samples)
            
            # Simple chord: C major (C, E, G)
            c_wave = np.sin(2 * np.pi * 261.63 * t) * 0.3
            e_wave = np.sin(2 * np.pi * 329.63 * t) * 0.3
            g_wave = np.sin(2 * np.pi * 392.00 * t) * 0.3
            
            waves = c_wave + e_wave + g_wave
            
            # Apply gentle LFO
            lfo = np.sin(2 * np.pi * 0.5 * t) * 0.1 + 0.9
            waves = waves * lfo
            
            # Fade in/out for seamless loop
            fade_samples = int(0.1 * sample_rate)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            waves[:fade_samples] *= fade_in
            waves[-fade_samples:] *= fade_out
            
            # Convert to 16-bit integers
            waves = (waves * 8192).astype(np.int16)
            stereo_waves = np.column_stack((waves, waves))
            
            # Create sound
            sound = pygame.sndarray.make_sound(stereo_waves)
            self.sounds[name] = sound
        except:
            pass
    
    def play_sound(self, name: str, volume: float = 1.0, loop: bool = False) -> None:
        """Play a sound by name."""
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(volume)
            if loop:
                sound.play(-1)  # Loop infinitely
            else:
                sound.play()
    
    def is_sound_playing(self, name: str) -> bool:
        """Check if a sound is currently playing."""
        # Check if any channels are playing our sound
        for i in range(pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            if channel.get_busy():
                # This is a simple check - in reality you'd need to track channels
                # For background music, we'll use a simpler approach in the states
                return True
        return False
    
    def stop_sound(self, name: str) -> None:
        """Stop a specific sound."""
        # For simplicity, stop all sounds when stopping background music
        if name == "background_music":
            pygame.mixer.stop()


# Global assets instance
assets = Assets()