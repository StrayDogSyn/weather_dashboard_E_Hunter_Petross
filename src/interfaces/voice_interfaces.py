"""Interfaces for voice and speech services."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import asyncio


class VoiceGender(Enum):
    """Voice gender options."""
    FEMALE = "female"
    MALE = "male"
    NEUTRAL = "neutral"


class SpeechRate(Enum):
    """Speech rate options."""
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"
    X_SLOW = "x-slow"
    X_FAST = "x-fast"


class AudioFormat(Enum):
    """Audio format options."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


@dataclass
class VoiceConfig:
    """Configuration for voice synthesis."""
    voice_name: str = "en-US-AriaNeural"
    language: str = "en-US"
    gender: VoiceGender = VoiceGender.FEMALE
    rate: SpeechRate = SpeechRate.MEDIUM
    pitch: str = "medium"
    volume: str = "medium"
    audio_format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 16000


@dataclass
class SpeechRecognitionConfig:
    """Configuration for speech recognition."""
    language: str = "en-US"
    continuous: bool = False
    interim_results: bool = True
    profanity_filter: bool = True
    timeout_seconds: int = 10
    phrase_hints: Optional[List[str]] = None


@dataclass
class VoiceCommand:
    """Represents a recognized voice command."""
    text: str
    confidence: float
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


@dataclass
class SpeechSynthesisResult:
    """Result of speech synthesis operation."""
    audio_data: bytes
    audio_format: AudioFormat
    duration_ms: int
    text: str
    voice_config: VoiceConfig
    success: bool
    error_message: Optional[str] = None


@dataclass
class SpeechRecognitionResult:
    """Result of speech recognition operation."""
    text: str
    confidence: float
    is_final: bool
    alternatives: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None


class ISpeechSynthesizer(ABC):
    """Interface for text-to-speech synthesis."""

    @abstractmethod
    async def synthesize_text(self, text: str, config: VoiceConfig) -> SpeechSynthesisResult:
        """Convert text to speech.
        
        Args:
            text: Text to synthesize
            config: Voice configuration
            
        Returns:
            Speech synthesis result with audio data
        """
        pass

    @abstractmethod
    async def get_available_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available voices.
        
        Args:
            language: Filter by language code (optional)
            
        Returns:
            List of available voice configurations
        """
        pass

    @abstractmethod
    async def synthesize_ssml(self, ssml: str, config: VoiceConfig) -> SpeechSynthesisResult:
        """Convert SSML to speech.
        
        Args:
            ssml: SSML markup to synthesize
            config: Voice configuration
            
        Returns:
            Speech synthesis result with audio data
        """
        pass


class ISpeechRecognizer(ABC):
    """Interface for speech-to-text recognition."""

    @abstractmethod
    async def recognize_once(self, config: SpeechRecognitionConfig) -> SpeechRecognitionResult:
        """Recognize speech from microphone (single utterance).
        
        Args:
            config: Recognition configuration
            
        Returns:
            Recognition result
        """
        pass

    @abstractmethod
    async def recognize_continuous(self, config: SpeechRecognitionConfig) -> AsyncGenerator[SpeechRecognitionResult, None]:
        """Recognize speech continuously from microphone.
        
        Args:
            config: Recognition configuration
            
        Yields:
            Recognition results as they become available
        """
        pass

    @abstractmethod
    async def recognize_from_file(self, file_path: str, config: SpeechRecognitionConfig) -> SpeechRecognitionResult:
        """Recognize speech from audio file.
        
        Args:
            file_path: Path to audio file
            config: Recognition configuration
            
        Returns:
            Recognition result
        """
        pass


class IVoiceCommandProcessor(ABC):
    """Interface for processing voice commands."""

    @abstractmethod
    async def process_command(self, command_text: str) -> VoiceCommand:
        """Process recognized speech into structured command.
        
        Args:
            command_text: Recognized speech text
            
        Returns:
            Structured voice command with intent and entities
        """
        pass

    @abstractmethod
    async def register_intent(self, intent_name: str, patterns: List[str]) -> bool:
        """Register a new voice command intent.
        
        Args:
            intent_name: Name of the intent
            patterns: List of text patterns that match this intent
            
        Returns:
            True if registration successful
        """
        pass

    @abstractmethod
    async def get_supported_intents(self) -> List[str]:
        """Get list of supported command intents.
        
        Returns:
            List of intent names
        """
        pass


class IVoiceService(ABC):
    """High-level interface for voice service operations."""

    @abstractmethod
    async def speak(self, text: str, config: Optional[VoiceConfig] = None) -> bool:
        """Speak text using text-to-speech.
        
        Args:
            text: Text to speak
            config: Voice configuration (optional)
            
        Returns:
            True if speech was successful
        """
        pass

    @abstractmethod
    async def listen(self, config: Optional[SpeechRecognitionConfig] = None) -> Optional[str]:
        """Listen for speech and return recognized text.
        
        Args:
            config: Recognition configuration (optional)
            
        Returns:
            Recognized text or None if recognition failed
        """
        pass

    @abstractmethod
    async def listen_for_command(self, config: Optional[SpeechRecognitionConfig] = None) -> Optional[VoiceCommand]:
        """Listen for speech and process as command.
        
        Args:
            config: Recognition configuration (optional)
            
        Returns:
            Processed voice command or None if recognition failed
        """
        pass

    @abstractmethod
    async def start_conversation(self) -> AsyncGenerator[VoiceCommand, None]:
        """Start continuous conversation mode.
        
        Yields:
            Voice commands as they are recognized
        """
        pass

    @abstractmethod
    async def stop_conversation(self) -> bool:
        """Stop continuous conversation mode.
        
        Returns:
            True if stopped successfully
        """
        pass

    @abstractmethod
    async def is_listening(self) -> bool:
        """Check if service is currently listening.
        
        Returns:
            True if actively listening for speech
        """
        pass

    @abstractmethod
    async def get_voice_settings(self) -> VoiceConfig:
        """Get current voice configuration.
        
        Returns:
            Current voice settings
        """
        pass

    @abstractmethod
    async def update_voice_settings(self, config: VoiceConfig) -> bool:
        """Update voice configuration.
        
        Args:
            config: New voice configuration
            
        Returns:
            True if update successful
        """
        pass