"""
Sound Effects Service for Weather Dashboard.

This service provides fun audio feedback for various user interactions
and weather-related events throughout the application.
"""

import logging
import os
import threading
import time
from enum import Enum
from typing import Dict, Optional

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
    BUTTON_CLICK = "button_click"
    BUTTON_HOVER = "button_hover"
    TAB_SWITCH = "tab_switch"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    NOTIFICATION = "notification"
    
    # Weather Related Sounds
    WEATHER_LOAD = "weather_load"
    WEATHER_REFRESH = "weather_refresh"
    RAIN = "rain"
    THUNDER = "thunder"
    WIND = "wind"
    SUNNY = "sunny"
    SNOW = "snow"
    
    # Feature Specific Sounds
    COMPARE_CITIES = "compare_cities"
    JOURNAL_SAVE = "journal_save"
    POETRY_GENERATE = "poetry_generate"
    ACTIVITY_SUGGEST = "activity_suggest"
    TEAM_DATA_REFRESH = "team_data_refresh"
    
    # Fun Notification Sounds
    ACHIEVEMENT = "achievement"
    MAGIC = "magic"
    CHIME = "chime"
    WHOOSH = "whoosh"
    POP = "pop"


class SoundEffectsService:
    """Service for managing and playing sound effects throughout the application."""
    
    def __init__(self, enabled: bool = True, volume: float = 0.7):
        """
        Initialize the sound effects service.
        
        Args:
            enabled: Whether sound effects are enabled
            volume: Default volume level (0.0 to 1.0)
        """
        self.logger = logging.getLogger(__name__)
        self.enabled = enabled
        self.volume = volume
        self.sounds_cache: Dict[SoundType, any] = {}
        
        # Define sound file mappings
        self.sound_files = {
            SoundType.BUTTON_CLICK: "super-mario-coin-sound.mp3",
            SoundType.BUTTON_HOVER: "ding-sound-effect_2.mp3", 
            SoundType.TAB_SWITCH: "maro-jump-sound-effect_1.mp3",
            SoundType.SUCCESS: "super-mario-coin-sound.mp3",
            SoundType.ERROR: "emotional-damage-meme.mp3",
            SoundType.WARNING: "danger-alarm-sound-effect-meme.mp3",
            SoundType.CHIME: "ding-sound-effect_2.mp3",
            SoundType.NOTIFICATION: "super-mario-beedoo_F3cwLoe.mp3",
            SoundType.POP: "maro-jump-sound-effect_1.mp3",
            SoundType.MAGIC: "magic-fairy.mp3",
            SoundType.WEATHER_LOAD: "super-mario-coin-sound.mp3",
            SoundType.COMPARE_CITIES: "test-your-might.mp3",
            SoundType.JOURNAL_SAVE: "ding-sound-effect_2.mp3",
            SoundType.ACTIVITY_SUGGEST: "toasty_tfCWsU6.mp3",
            SoundType.POETRY_GENERATE: "magic-fairy.mp3",
            SoundType.RAIN: "danger-alarm-sound-effect-meme.mp3",  # Creative use
            SoundType.WIND: "super-mario-beedoo_F3cwLoe.mp3",      # Creative use
            SoundType.THUNDER: "metal-gear-alert-sound-effect_XKoHReZ.mp3",
        }
        
        # Check available audio backends
        self.audio_backend = self._detect_audio_backend()
        
        if self.audio_backend and self.enabled:
            self._initialize_audio()
            self._load_sound_effects()
        else:
            self.logger.info("Sound effects disabled or no audio backend available")
    
    def _detect_audio_backend(self) -> Optional[str]:
        """Detect available audio backend."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                pygame.mixer.quit()
                return "pygame"
            except Exception as e:
                self.logger.debug(f"Pygame audio not available: {e}")
        
        if WINSOUND_AVAILABLE:
            return "winsound"
        
        self.logger.warning("No audio backend available for sound effects")
        return None
    
    def _initialize_audio(self):
        """Initialize the audio system."""
        try:
            if self.audio_backend == "pygame":
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.logger.info("Pygame audio initialized for sound effects")
            elif self.audio_backend == "winsound":
                self.logger.info("Windows sound system available for sound effects")
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self.enabled = False
    
    def _load_sound_effects(self):
        """Load sound effects from audio files."""
        if not self.enabled:
            return
        
        # Get the path to the sounds directory
        sounds_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sounds')
        
        if not os.path.exists(sounds_dir):
            self.logger.warning(f"Sounds directory not found: {sounds_dir}")
            return
        
        loaded_count = 0
        
        # Load audio files based on sound type mappings
        for sound_type, filename in self.sound_files.items():
            file_path = os.path.join(sounds_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    if self.audio_backend == "pygame" and PYGAME_AVAILABLE:
                        sound = pygame.mixer.Sound(file_path)
                        self.sounds_cache[sound_type] = sound
                        loaded_count += 1
                    else:
                        # Store file path for winsound fallback
                        self.sounds_cache[sound_type] = file_path
                        loaded_count += 1
                        
                except Exception as e:
                    self.logger.debug(f"Failed to load sound {filename}: {e}")
            else:
                self.logger.debug(f"Sound file not found: {file_path}")
        
        # Generate fallback procedural sounds for missing files
        if loaded_count < len(self.sound_files):
            self._generate_fallback_sounds()
        
        self.logger.info(f"Loaded {loaded_count} sound effects from audio files")
    
    def _generate_fallback_sounds(self):
        """Generate simple fallback sounds for missing audio files."""
        # Simple frequency mappings for winsound fallback
        fallback_sounds = {
            SoundType.BUTTON_CLICK: (800, 100),
            SoundType.BUTTON_HOVER: (600, 50),
            SoundType.TAB_SWITCH: (1000, 150),
            SoundType.SUCCESS: (523, 200),  # C note
            SoundType.ERROR: (200, 300),
            SoundType.WARNING: (400, 150),
            SoundType.NOTIFICATION: (880, 100),
            SoundType.WEATHER_LOAD: (659, 150),  # E note
            SoundType.COMPARE_CITIES: (440, 250),  # A note
            SoundType.JOURNAL_SAVE: (784, 200),  # G note
            SoundType.ACTIVITY_SUGGEST: (698, 150),  # F# note
            SoundType.POETRY_GENERATE: (1047, 300),  # High C
            SoundType.MAGIC: (1319, 200),  # High E
            SoundType.CHIME: (1175, 100),  # High D
        }
        
        # Only add fallback sounds that weren't loaded from files
        for sound_type, (freq, duration) in fallback_sounds.items():
            if sound_type not in self.sounds_cache:
                self.sounds_cache[sound_type] = (freq, duration)
    
    def _generate_procedural_sounds(self):
        """Generate procedural sound effects using code."""
        if self.audio_backend != "pygame":
            return
        
        try:
            import numpy as np
            
            # Sample rate and duration
            sample_rate = 22050
            
            # Generate different sound effects
            self._generate_button_click(sample_rate)
            self._generate_success_sound(sample_rate)
            self._generate_error_sound(sample_rate)
            self._generate_weather_sounds(sample_rate)
            self._generate_notification_sounds(sample_rate)
            
        except ImportError:
            self.logger.debug("NumPy not available for procedural sound generation")
            self._generate_simple_sounds()
    
    def _generate_button_click(self, sample_rate: int):
        """Generate button click sound."""
        try:
            import numpy as np
            
            duration = 0.1
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Quick click sound - brief sine wave with envelope
            frequency = 800
            wave = np.sin(2 * np.pi * frequency * t)
            envelope = np.exp(-t * 20)  # Quick decay
            sound = (wave * envelope * 0.3 * 32767).astype(np.int16)
            
            # Convert to stereo
            stereo_sound = np.array([sound, sound]).T
            
            if PYGAME_AVAILABLE:
                sound_obj = pygame.sndarray.make_sound(stereo_sound)
                self.sounds_cache[SoundType.BUTTON_CLICK] = sound_obj
        except Exception as e:
            self.logger.debug(f"Failed to generate button click sound: {e}")
    
    def _generate_success_sound(self, sample_rate: int):
        """Generate success notification sound."""
        try:
            import numpy as np
            
            duration = 0.5
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Ascending chord progression for success
            freqs = [523, 659, 784]  # C, E, G major chord
            wave = np.zeros_like(t)
            
            for i, freq in enumerate(freqs):
                start_time = i * 0.15
                mask = t >= start_time
                chord_wave = np.sin(2 * np.pi * freq * (t - start_time)) * mask
                envelope = np.exp(-(t - start_time) * 4) * mask
                wave += chord_wave * envelope
            
            sound = (wave * 0.2 * 32767).astype(np.int16)
            stereo_sound = np.array([sound, sound]).T
            
            if PYGAME_AVAILABLE:
                sound_obj = pygame.sndarray.make_sound(stereo_sound)
                self.sounds_cache[SoundType.SUCCESS] = sound_obj
        except Exception as e:
            self.logger.debug(f"Failed to generate success sound: {e}")
    
    def _generate_error_sound(self, sample_rate: int):
        """Generate error notification sound."""
        try:
            import numpy as np
            
            duration = 0.3
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Descending dissonant sound for error
            frequency = 300
            wave = np.sin(2 * np.pi * frequency * t) + 0.5 * np.sin(2 * np.pi * (frequency * 1.2) * t)
            envelope = np.exp(-t * 5)
            sound = (wave * envelope * 0.25 * 32767).astype(np.int16)
            
            stereo_sound = np.array([sound, sound]).T
            
            if PYGAME_AVAILABLE:
                sound_obj = pygame.sndarray.make_sound(stereo_sound)
                self.sounds_cache[SoundType.ERROR] = sound_obj
        except Exception as e:
            self.logger.debug(f"Failed to generate error sound: {e}")
    
    def _generate_weather_sounds(self, sample_rate: int):
        """Generate weather-related sound effects."""
        try:
            import numpy as np
            
            # Rain sound - white noise filtered
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            rain_noise = np.random.normal(0, 0.1, len(t))
            
            # Filter for rain-like sound
            rain_sound = (rain_noise * 0.3 * 32767).astype(np.int16)
            stereo_rain = np.array([rain_sound, rain_sound]).T
            
            if PYGAME_AVAILABLE:
                rain_obj = pygame.sndarray.make_sound(stereo_rain)
                self.sounds_cache[SoundType.RAIN] = rain_obj
            
            # Wind sound - low frequency noise
            wind_freq = np.random.normal(200, 50, len(t))
            wind_wave = np.sin(2 * np.pi * wind_freq * t)
            wind_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)  # Slow modulation
            wind_sound = (wind_wave * wind_envelope * 0.2 * 32767).astype(np.int16)
            stereo_wind = np.array([wind_sound, wind_sound]).T
            
            if PYGAME_AVAILABLE:
                wind_obj = pygame.sndarray.make_sound(stereo_wind)
                self.sounds_cache[SoundType.WIND] = wind_obj
            
        except Exception as e:
            self.logger.debug(f"Failed to generate weather sounds: {e}")
    
    def _generate_notification_sounds(self, sample_rate: int):
        """Generate notification sound effects."""
        try:
            import numpy as np
            
            duration = 0.3
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Magic sound - sparkly effect
            frequencies = [1047, 1319, 1568, 2093]  # High notes
            magic_wave = np.zeros_like(t)
            
            for i, freq in enumerate(frequencies):
                start_time = i * 0.05
                if start_time < duration:
                    mask = t >= start_time
                    note_wave = np.sin(2 * np.pi * freq * (t - start_time)) * mask
                    envelope = np.exp(-(t - start_time) * 8) * mask
                    magic_wave += note_wave * envelope
            
            magic_sound = (magic_wave * 0.15 * 32767).astype(np.int16)
            stereo_magic = np.array([magic_sound, magic_sound]).T
            
            if PYGAME_AVAILABLE:
                magic_obj = pygame.sndarray.make_sound(stereo_magic)
                self.sounds_cache[SoundType.MAGIC] = magic_obj
            
            # Chime sound
            chime_freq = 1760  # High A
            chime_wave = np.sin(2 * np.pi * chime_freq * t)
            chime_envelope = np.exp(-t * 3)
            chime_sound = (chime_wave * chime_envelope * 0.2 * 32767).astype(np.int16)
            stereo_chime = np.array([chime_sound, chime_sound]).T
            
            if PYGAME_AVAILABLE:
                chime_obj = pygame.sndarray.make_sound(stereo_chime)
                self.sounds_cache[SoundType.CHIME] = chime_obj
                
        except Exception as e:
            self.logger.debug(f"Failed to generate notification sounds: {e}")
    
    def _generate_simple_sounds(self):
        """Generate simple beep sounds as fallback."""
        if self.audio_backend == "winsound":
            # Windows system sounds as fallback
            self.sounds_cache[SoundType.BUTTON_CLICK] = 1000  # Frequency for beep
            self.sounds_cache[SoundType.SUCCESS] = (523, 100)  # Note and duration
            self.sounds_cache[SoundType.ERROR] = (300, 200)
            self.sounds_cache[SoundType.WARNING] = (400, 150)
    
    def play_sound(self, sound_type: SoundType, volume: Optional[float] = None):
        """
        Play a sound effect.
        
        Args:
            sound_type: Type of sound to play
            volume: Volume override (0.0 to 1.0)
        """
        if not self.enabled or not self.audio_backend:
            return
        
        # Use provided volume or default
        play_volume = volume if volume is not None else self.volume
        
        try:
            if self.audio_backend == "pygame" and sound_type in self.sounds_cache:
                sound = self.sounds_cache[sound_type]
                
                # Handle pygame Sound objects
                if hasattr(sound, 'set_volume') and hasattr(sound, 'play'):
                    sound.set_volume(play_volume)
                    sound.play()
                # Handle file paths (fallback)
                elif isinstance(sound, str) and PYGAME_AVAILABLE:
                    try:
                        import pygame
                        temp_sound = pygame.mixer.Sound(sound)
                        temp_sound.set_volume(play_volume)
                        temp_sound.play()
                    except Exception:
                        # Fall back to winsound
                        self._play_winsound_fallback(sound_type)
            
            elif self.audio_backend == "winsound" and sound_type in self.sounds_cache:
                self._play_winsound_fallback(sound_type)
                    
        except Exception as e:
            self.logger.debug(f"Failed to play sound {sound_type.value}: {e}")
    
    def _play_winsound_fallback(self, sound_type: SoundType):
        """Play sound using winsound fallback."""
        if not WINSOUND_AVAILABLE:
            return
            
        try:
            import winsound
            sound_data = self.sounds_cache.get(sound_type)
            if isinstance(sound_data, tuple):
                freq, duration = sound_data
                winsound.Beep(freq, duration)
            elif isinstance(sound_data, int):
                winsound.Beep(sound_data, 100)
        except Exception:
            pass
    
    def play_sound_async(self, sound_type: SoundType, volume: Optional[float] = None):
        """
        Play a sound effect asynchronously to avoid blocking the UI.
        
        Args:
            sound_type: Type of sound to play
            volume: Volume override (0.0 to 1.0)
        """
        if not self.enabled:
            return
        
        def play_async():
            self.play_sound(sound_type, volume)
        
        threading.Thread(target=play_async, daemon=True).start()
    
    def play_weather_sound(self, weather_condition: str):
        """
        Play a sound based on weather condition.
        
        Args:
            weather_condition: Weather condition string
        """
        if not self.enabled:
            return
        
        condition_lower = weather_condition.lower()
        
        if "rain" in condition_lower or "drizzle" in condition_lower:
            self.play_sound_async(SoundType.RAIN, 0.4)
        elif "thunder" in condition_lower or "storm" in condition_lower:
            self.play_sound_async(SoundType.THUNDER, 0.6)
        elif "wind" in condition_lower:
            self.play_sound_async(SoundType.WIND, 0.3)
        elif "snow" in condition_lower:
            self.play_sound_async(SoundType.SNOW, 0.3)
        elif "clear" in condition_lower or "sunny" in condition_lower:
            self.play_sound_async(SoundType.SUNNY, 0.3)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self.enabled = enabled
        self.logger.info(f"Sound effects {'enabled' if enabled else 'disabled'}")
    
    def set_volume(self, volume: float):
        """
        Set the default volume level.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        self.logger.debug(f"Sound volume set to {self.volume}")
    
    def play_sequence(self, sound_types: list, delay: float = 0.1):
        """
        Play a sequence of sounds with delay between them.
        
        Args:
            sound_types: List of SoundType to play in sequence
            delay: Delay between sounds in seconds
        """
        if not self.enabled:
            return
        
        def play_sequence_async():
            for sound_type in sound_types:
                self.play_sound(sound_type)
                time.sleep(delay)
        
        threading.Thread(target=play_sequence_async, daemon=True).start()
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            if self.audio_backend == "pygame" and PYGAME_AVAILABLE:
                import pygame
                pygame.mixer.quit()
            self.sounds_cache.clear()
            self.logger.debug("Sound service cleaned up")
        except Exception as e:
            self.logger.debug(f"Error during sound service cleanup: {e}")


# Global sound service instance
_sound_service: Optional[SoundEffectsService] = None


def get_sound_service() -> SoundEffectsService:
    """Get the global sound service instance."""
    global _sound_service
    if _sound_service is None:
        _sound_service = SoundEffectsService()
    return _sound_service


def play_sound(sound_type: SoundType, volume: Optional[float] = None):
    """Convenience function to play a sound."""
    get_sound_service().play_sound_async(sound_type, volume)


def play_weather_sound(weather_condition: str):
    """Convenience function to play weather-based sound."""
    get_sound_service().play_weather_sound(weather_condition)
