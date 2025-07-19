"""
Sound Effects Service for Weather Dashboard.

This service provides audio feedback for user interactions and weather events.
Simplified and optimized for better maintainability.
"""

import logging
import os
import threading
from enum import Enum
from typing import Dict, Optional, Any

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


class SoundType(Enum):
    """Enumeration of different sound effect types."""
    
    # UI Interaction Sounds
    BUTTON_CLICK = "button_click"      # Covers clicks, hovers, tab switches
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    NOTIFICATION = "notification"
    
    # Weather Related Sounds
    WEATHER_LOAD = "weather_load"
    RAIN = "rain"
    THUNDER = "thunder"
    
    # Feature Specific Sounds
    COMPARE_CITIES = "compare_cities"
    JOURNAL_SAVE = "journal_save"
    MAGIC = "magic"                    # Covers poetry, activity suggestions, special effects


class SoundService:
    """Simplified service for managing sound effects."""
    
    def __init__(self, enabled: bool = True, volume: float = 0.7):
        """Initialize the sound service."""
        self.logger = logging.getLogger(__name__)
        self.enabled = enabled
        self.volume = volume
        self.sounds_cache: Dict[SoundType, Any] = {}
        
        # Sound file mappings - each sound type gets a unique file (11 of 12 files used)
        self.sound_files = {
            SoundType.BUTTON_CLICK: "super-mario-coin-sound.mp3",
            SoundType.SUCCESS: "ding-sound-effect_2.mp3",
            SoundType.ERROR: "emotional-damage-meme.mp3",
            SoundType.WARNING: "danger-alarm-sound-effect-meme.mp3", 
            SoundType.NOTIFICATION: "super-mario-beedoo_F3cwLoe.mp3",
            SoundType.WEATHER_LOAD: "maro-jump-sound-effect_1.mp3",
            SoundType.RAIN: "metal-gear-alert-sound-effect_XKoHReZ.mp3",
            SoundType.THUNDER: "mka.mp3",
            SoundType.COMPARE_CITIES: "test-your-might.mp3",
            SoundType.JOURNAL_SAVE: "toasty_tfCWsU6.mp3",
            SoundType.MAGIC: "magic-fairy.mp3",
            # mortal-kombat-intro.mp3 reserved for future special events
        }
        
        # Initialize audio backend
        self.audio_backend = self._detect_audio_backend()
        if self.audio_backend and self.enabled:
            self._initialize_audio()
            self._load_sounds()

    def _detect_audio_backend(self) -> Optional[str]:
        """Detect available audio backend."""
        if PYGAME_AVAILABLE:
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.quit()
                return "pygame"
            except Exception:
                pass
        
        if WINSOUND_AVAILABLE:
            return "winsound"
        
        return None

    def _initialize_audio(self):
        """Initialize the audio system."""
        try:
            if self.audio_backend == "pygame":
                import pygame
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.logger.info("Audio initialized with pygame")
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self.enabled = False

    def _load_sounds(self):
        """Load sound effects from files."""
        if not self.enabled:
            return
        
        sounds_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sounds')
        if not os.path.exists(sounds_dir):
            self.logger.warning(f"Sounds directory not found: {sounds_dir}")
            return
        
        loaded_count = 0
        for sound_type, filename in self.sound_files.items():
            file_path = os.path.join(sounds_dir, filename)
            if os.path.exists(file_path):
                try:
                    if self.audio_backend == "pygame":
                        import pygame
                        sound = pygame.mixer.Sound(file_path)
                        self.sounds_cache[sound_type] = sound
                        loaded_count += 1
                except Exception as e:
                    self.logger.debug(f"Failed to load {filename}: {e}")
        
        self.logger.info(f"Loaded {loaded_count} sound effects")

    def play_sound(self, sound_type: SoundType, volume: Optional[float] = None):
        """Play a sound effect."""
        if not self.enabled or not self.audio_backend:
            return
        
        try:
            play_volume = volume if volume is not None else self.volume
            
            if self.audio_backend == "pygame" and sound_type in self.sounds_cache:
                sound = self.sounds_cache[sound_type]
                if hasattr(sound, 'set_volume') and hasattr(sound, 'play'):
                    sound.set_volume(play_volume)
                    sound.play()
            elif self.audio_backend == "winsound":
                # Simple fallback beeps
                if WINSOUND_AVAILABLE:
                    import winsound
                    frequencies = {
                        SoundType.BUTTON_CLICK: 800,
                        SoundType.SUCCESS: 523,
                        SoundType.ERROR: 200,
                        SoundType.WARNING: 400,
                        SoundType.NOTIFICATION: 880,
                        SoundType.WEATHER_LOAD: 750,
                        SoundType.RAIN: 300,
                        SoundType.THUNDER: 150,
                        SoundType.COMPARE_CITIES: 450,
                        SoundType.JOURNAL_SAVE: 900,
                        SoundType.MAGIC: 1100,
                    }
                    freq = frequencies.get(sound_type, 600)
                    winsound.Beep(freq, 100)
                    
        except Exception as e:
            self.logger.debug(f"Failed to play sound {sound_type.value}: {e}")

    def play_sound_async(self, sound_type: SoundType, volume: Optional[float] = None):
        """Play a sound effect asynchronously."""
        if not self.enabled:
            return
        
        threading.Thread(
            target=self.play_sound, 
            args=(sound_type, volume), 
            daemon=True
        ).start()

    def play_weather_sound(self, weather_condition: str):
        """Play a sound based on weather condition."""
        condition_lower = weather_condition.lower()
        
        if "rain" in condition_lower:
            self.play_sound_async(SoundType.RAIN, 0.4)
        elif "thunder" in condition_lower or "storm" in condition_lower:
            self.play_sound_async(SoundType.THUNDER, 0.6)
        elif "wind" in condition_lower:
            self.play_sound_async(SoundType.WARNING, 0.3)  # Use warning sound for wind

    def set_enabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self.enabled = enabled

    def set_volume(self, volume: float):
        """Set the volume level."""
        self.volume = max(0.0, min(1.0, volume))

    def cleanup(self):
        """Clean up audio resources."""
        try:
            if self.audio_backend == "pygame" and PYGAME_AVAILABLE:
                import pygame
                pygame.mixer.quit()
            self.sounds_cache.clear()
        except Exception as e:
            self.logger.debug(f"Error during cleanup: {e}")


# Global sound service instance
_sound_service: Optional[SoundService] = None


def get_sound_service() -> SoundService:
    """Get the global sound service instance."""
    global _sound_service
    if _sound_service is None:
        _sound_service = SoundService()
    return _sound_service


def play_sound(sound_type: SoundType, volume: Optional[float] = None):
    """Convenience function to play a sound."""
    get_sound_service().play_sound_async(sound_type, volume)


def play_weather_sound(weather_condition: str):
    """Convenience function to play weather-based sound."""
    get_sound_service().play_weather_sound(weather_condition)
