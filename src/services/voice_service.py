"""Voice service implementation with Azure Speech Services integration."""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

from ..interfaces.voice_interfaces import (
    AudioFormat,
    ISpeechRecognizer,
    ISpeechSynthesizer,
    IVoiceCommandProcessor,
    IVoiceService,
    SpeechRate,
    SpeechRecognitionConfig,
    SpeechRecognitionResult,
    SpeechSynthesisResult,
    VoiceCommand,
    VoiceConfig,
    VoiceGender,
)

logger = logging.getLogger(__name__)


@dataclass
class AzureSpeechConfig:
    """Configuration for Azure Speech Services."""

    subscription_key: str
    region: str
    endpoint: Optional[str] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


class AzureSpeechSynthesizer(ISpeechSynthesizer):
    """Azure Speech Services text-to-speech implementation."""

    def __init__(self, config: AzureSpeechConfig):
        self.config = config
        self._speech_config = None
        self._synthesizer = None
        self._initialize_speech_config()

    def _initialize_speech_config(self):
        """Initialize Azure Speech SDK configuration."""
        if not speechsdk:
            raise ImportError(
                "Azure Speech SDK not installed. Install with: pip install azure-cognitiveservices-speech"
            )

        self._speech_config = speechsdk.SpeechConfig(
            subscription=self.config.subscription_key, region=self.config.region
        )

        if self.config.endpoint:
            self._speech_config.endpoint_id = self.config.endpoint

    async def synthesize_text(
        self, text: str, config: VoiceConfig
    ) -> SpeechSynthesisResult:
        """Convert text to speech using Azure Speech Services."""
        try:
            # Configure voice settings
            self._speech_config.speech_synthesis_voice_name = config.voice_name

            # Set audio format
            audio_format = self._get_audio_format(
                config.audio_format, config.sample_rate
            )
            self._speech_config.set_speech_synthesis_output_format(audio_format)

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config,
                audio_config=None,  # Return audio data instead of playing
            )

            # Build SSML for better control
            ssml = self._build_ssml(text, config)

            # Perform synthesis
            result = synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return SpeechSynthesisResult(
                    audio_data=result.audio_data,
                    audio_format=config.audio_format,
                    duration_ms=len(result.audio_data)
                    // (config.sample_rate * 2)
                    * 1000,  # Approximate
                    text=text,
                    voice_config=config,
                    success=True,
                )
            else:
                error_msg = f"Speech synthesis failed: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg += (
                        f" - {cancellation.reason}: {cancellation.error_details}"
                    )

                return SpeechSynthesisResult(
                    audio_data=b"",
                    audio_format=config.audio_format,
                    duration_ms=0,
                    text=text,
                    voice_config=config,
                    success=False,
                    error_message=error_msg,
                )

        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
            return SpeechSynthesisResult(
                audio_data=b"",
                audio_format=config.audio_format,
                duration_ms=0,
                text=text,
                voice_config=config,
                success=False,
                error_message=str(e),
            )

    async def synthesize_ssml(
        self, ssml: str, config: VoiceConfig
    ) -> SpeechSynthesisResult:
        """Convert SSML to speech using Azure Speech Services."""
        try:
            self._speech_config.speech_synthesis_voice_name = config.voice_name

            audio_format = self._get_audio_format(
                config.audio_format, config.sample_rate
            )
            self._speech_config.set_speech_synthesis_output_format(audio_format)

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config, audio_config=None
            )

            result = synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return SpeechSynthesisResult(
                    audio_data=result.audio_data,
                    audio_format=config.audio_format,
                    duration_ms=len(result.audio_data)
                    // (config.sample_rate * 2)
                    * 1000,
                    text=self._extract_text_from_ssml(ssml),
                    voice_config=config,
                    success=True,
                )
            else:
                error_msg = f"SSML synthesis failed: {result.reason}"
                return SpeechSynthesisResult(
                    audio_data=b"",
                    audio_format=config.audio_format,
                    duration_ms=0,
                    text=self._extract_text_from_ssml(ssml),
                    voice_config=config,
                    success=False,
                    error_message=error_msg,
                )

        except Exception as e:
            logger.error(f"Error in SSML synthesis: {e}")
            return SpeechSynthesisResult(
                audio_data=b"",
                audio_format=config.audio_format,
                duration_ms=0,
                text=self._extract_text_from_ssml(ssml),
                voice_config=config,
                success=False,
                error_message=str(e),
            )

    async def get_available_voices(
        self, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of available voices from Azure Speech Services."""
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config, audio_config=None
            )

            result = synthesizer.get_voices_async(language).get()

            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                voices = []
                for voice in result.voices:
                    voices.append(
                        {
                            "name": voice.name,
                            "display_name": voice.display_name,
                            "local_name": voice.local_name,
                            "short_name": voice.short_name,
                            "gender": voice.gender.name.lower(),
                            "locale": voice.locale,
                            "sample_rate_hertz": voice.sample_rate_hertz,
                            "voice_type": voice.voice_type.name,
                        }
                    )
                return voices
            else:
                logger.error(f"Failed to retrieve voices: {result.reason}")
                return []

        except Exception as e:
            logger.error(f"Error retrieving voices: {e}")
            return []

    def _build_ssml(self, text: str, config: VoiceConfig) -> str:
        """Build SSML markup for enhanced speech control."""
        rate_map = {
            SpeechRate.X_SLOW: "x-slow",
            SpeechRate.SLOW: "slow",
            SpeechRate.MEDIUM: "medium",
            SpeechRate.FAST: "fast",
            SpeechRate.X_FAST: "x-fast",
        }

        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{config.language}">
            <voice name="{config.voice_name}">
                <prosody rate="{rate_map.get(config.rate, 'medium')}" pitch="{config.pitch}" volume="{config.volume}">
                    {text}
                </prosody>
            </voice>
        </speak>"""

        return ssml

    def _get_audio_format(self, format_type: AudioFormat, sample_rate: int):
        """Get Azure Speech SDK audio format."""
        format_map = {
            AudioFormat.WAV: speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm,
            AudioFormat.MP3: speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
            AudioFormat.OGG: speechsdk.SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus,
        }

        return format_map.get(
            format_type, speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
        )

    def _extract_text_from_ssml(self, ssml: str) -> str:
        """Extract plain text from SSML markup."""
        import re

        # Remove SSML tags
        text = re.sub(r"<[^>]+>", "", ssml)
        return text.strip()


class AzureSpeechRecognizer(ISpeechRecognizer):
    """Azure Speech Services speech-to-text implementation."""

    def __init__(self, config: AzureSpeechConfig):
        self.config = config
        self._speech_config = None
        self._initialize_speech_config()

    def _initialize_speech_config(self):
        """Initialize Azure Speech SDK configuration."""
        if not speechsdk:
            raise ImportError("Azure Speech SDK not installed")

        self._speech_config = speechsdk.SpeechConfig(
            subscription=self.config.subscription_key, region=self.config.region
        )

    async def recognize_once(
        self, config: SpeechRecognitionConfig
    ) -> SpeechRecognitionResult:
        """Recognize speech from microphone (single utterance)."""
        try:
            self._speech_config.speech_recognition_language = config.language

            if config.phrase_hints:
                phrase_list = speechsdk.PhraseListGrammar.from_recognizer(
                    speechsdk.SpeechRecognizer(speech_config=self._speech_config)
                )
                for phrase in config.phrase_hints:
                    phrase_list.addPhrase(phrase)

            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self._speech_config, audio_config=audio_config
            )

            result = recognizer.recognize_once_async().get()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return SpeechRecognitionResult(
                    text=result.text,
                    confidence=1.0,  # Azure doesn't provide confidence in basic recognition
                    is_final=True,
                )
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return SpeechRecognitionResult(
                    text="",
                    confidence=0.0,
                    is_final=True,
                    error_message="No speech could be recognized",
                )
            else:
                error_msg = f"Recognition failed: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg += (
                        f" - {cancellation.reason}: {cancellation.error_details}"
                    )

                return SpeechRecognitionResult(
                    text="", confidence=0.0, is_final=True, error_message=error_msg
                )

        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return SpeechRecognitionResult(
                text="", confidence=0.0, is_final=True, error_message=str(e)
            )

    async def recognize_continuous(
        self, config: SpeechRecognitionConfig
    ) -> AsyncGenerator[SpeechRecognitionResult, None]:
        """Recognize speech continuously from microphone."""
        try:
            self._speech_config.speech_recognition_language = config.language

            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self._speech_config, audio_config=audio_config
            )

            results_queue = asyncio.Queue()

            def recognized_handler(evt):
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    result = SpeechRecognitionResult(
                        text=evt.result.text, confidence=1.0, is_final=True
                    )
                    asyncio.create_task(results_queue.put(result))

            def recognizing_handler(evt):
                if config.interim_results and evt.result.text:
                    result = SpeechRecognitionResult(
                        text=evt.result.text, confidence=0.5, is_final=False
                    )
                    asyncio.create_task(results_queue.put(result))

            recognizer.recognized.connect(recognized_handler)
            if config.interim_results:
                recognizer.recognizing.connect(recognizing_handler)

            recognizer.start_continuous_recognition_async()

            try:
                while True:
                    result = await asyncio.wait_for(
                        results_queue.get(), timeout=config.timeout_seconds
                    )
                    yield result
            except asyncio.TimeoutError:
                logger.info("Continuous recognition timeout")
            finally:
                recognizer.stop_continuous_recognition_async()

        except Exception as e:
            logger.error(f"Error in continuous recognition: {e}")
            yield SpeechRecognitionResult(
                text="", confidence=0.0, is_final=True, error_message=str(e)
            )

    async def recognize_from_file(
        self, file_path: str, config: SpeechRecognitionConfig
    ) -> SpeechRecognitionResult:
        """Recognize speech from audio file."""
        try:
            self._speech_config.speech_recognition_language = config.language

            audio_config = speechsdk.audio.AudioConfig(filename=file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self._speech_config, audio_config=audio_config
            )

            result = recognizer.recognize_once_async().get()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return SpeechRecognitionResult(
                    text=result.text, confidence=1.0, is_final=True
                )
            else:
                return SpeechRecognitionResult(
                    text="",
                    confidence=0.0,
                    is_final=True,
                    error_message=f"Recognition failed: {result.reason}",
                )

        except Exception as e:
            logger.error(f"Error in file recognition: {e}")
            return SpeechRecognitionResult(
                text="", confidence=0.0, is_final=True, error_message=str(e)
            )


class SimpleVoiceCommandProcessor(IVoiceCommandProcessor):
    """Simple pattern-based voice command processor."""

    def __init__(self):
        self.intents: Dict[str, List[str]] = {
            "weather_current": [
                r"what.*weather.*like",
                r"current.*weather",
                r"weather.*now",
                r"how.*weather",
            ],
            "weather_forecast": [
                r"weather.*forecast",
                r"forecast.*weather",
                r"weather.*tomorrow",
                r"weather.*week",
            ],
            "weather_location": [
                r"weather.*in.*",
                r"weather.*for.*",
                r".*weather.*city",
            ],
            "greeting": [r"hello.*cortana", r"hi.*cortana", r"hey.*cortana"],
            "goodbye": [r"goodbye.*cortana", r"bye.*cortana", r"see.*you.*later"],
        }

    async def process_command(self, command_text: str) -> VoiceCommand:
        """Process recognized speech into structured command."""
        command_lower = command_text.lower()

        # Find matching intent
        matched_intent = None
        confidence = 0.0

        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    matched_intent = intent
                    confidence = 0.8  # Simple confidence score
                    break
            if matched_intent:
                break

        # Extract entities (simple implementation)
        entities = self._extract_entities(command_lower, matched_intent)

        return VoiceCommand(
            text=command_text,
            confidence=confidence,
            intent=matched_intent,
            entities=entities,
            timestamp=datetime.now().isoformat(),
        )

    async def register_intent(self, intent_name: str, patterns: List[str]) -> bool:
        """Register a new voice command intent."""
        try:
            self.intents[intent_name] = patterns
            return True
        except Exception as e:
            logger.error(f"Error registering intent {intent_name}: {e}")
            return False

    async def get_supported_intents(self) -> List[str]:
        """Get list of supported command intents."""
        return list(self.intents.keys())

    def _extract_entities(self, text: str, intent: Optional[str]) -> Dict[str, Any]:
        """Extract entities from command text."""
        entities = {}

        if intent == "weather_location":
            # Extract location from "weather in [location]" or "weather for [location]"
            location_match = re.search(r"weather\s+(?:in|for)\s+([a-zA-Z\s]+)", text)
            if location_match:
                entities["location"] = location_match.group(1).strip()

        return entities


class VoiceService(IVoiceService):
    """High-level voice service implementation."""

    def __init__(
        self,
        synthesizer: ISpeechSynthesizer,
        recognizer: ISpeechRecognizer,
        command_processor: IVoiceCommandProcessor,
        default_voice_config: Optional[VoiceConfig] = None,
        default_recognition_config: Optional[SpeechRecognitionConfig] = None,
    ):
        self.synthesizer = synthesizer
        self.recognizer = recognizer
        self.command_processor = command_processor
        self.voice_config = default_voice_config or VoiceConfig()
        self.recognition_config = (
            default_recognition_config or SpeechRecognitionConfig()
        )
        self._is_listening = False
        self._conversation_task: Optional[asyncio.Task] = None

    async def speak(self, text: str, config: Optional[VoiceConfig] = None) -> bool:
        """Speak text using text-to-speech."""
        try:
            voice_config = config or self.voice_config
            result = await self.synthesizer.synthesize_text(text, voice_config)
            return result.success
        except Exception as e:
            logger.error(f"Error in speak: {e}")
            return False

    async def listen(
        self, config: Optional[SpeechRecognitionConfig] = None
    ) -> Optional[str]:
        """Listen for speech and return recognized text."""
        try:
            recognition_config = config or self.recognition_config
            result = await self.recognizer.recognize_once(recognition_config)
            return result.text if result.text else None
        except Exception as e:
            logger.error(f"Error in listen: {e}")
            return None

    async def listen_for_command(
        self, config: Optional[SpeechRecognitionConfig] = None
    ) -> Optional[VoiceCommand]:
        """Listen for speech and process as command."""
        try:
            text = await self.listen(config)
            if text:
                return await self.command_processor.process_command(text)
            return None
        except Exception as e:
            logger.error(f"Error in listen_for_command: {e}")
            return None

    async def start_conversation(self) -> AsyncGenerator[VoiceCommand, None]:
        """Start continuous conversation mode."""
        self._is_listening = True

        try:
            async for result in self.recognizer.recognize_continuous(
                self.recognition_config
            ):
                if not self._is_listening:
                    break

                if result.is_final and result.text:
                    command = await self.command_processor.process_command(result.text)
                    yield command
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
        finally:
            self._is_listening = False

    async def stop_conversation(self) -> bool:
        """Stop continuous conversation mode."""
        try:
            self._is_listening = False
            if self._conversation_task and not self._conversation_task.done():
                self._conversation_task.cancel()
            return True
        except Exception as e:
            logger.error(f"Error stopping conversation: {e}")
            return False

    async def is_listening(self) -> bool:
        """Check if service is currently listening."""
        return self._is_listening

    async def get_voice_settings(self) -> VoiceConfig:
        """Get current voice configuration."""
        return self.voice_config

    async def update_voice_settings(self, config: VoiceConfig) -> bool:
        """Update voice configuration."""
        try:
            self.voice_config = config
            return True
        except Exception as e:
            logger.error(f"Error updating voice settings: {e}")
            return False


def create_voice_service(
    azure_config: AzureSpeechConfig,
    voice_config: Optional[VoiceConfig] = None,
    recognition_config: Optional[SpeechRecognitionConfig] = None,
) -> VoiceService:
    """Factory function to create a complete voice service."""
    synthesizer = AzureSpeechSynthesizer(azure_config)
    recognizer = AzureSpeechRecognizer(azure_config)
    command_processor = SimpleVoiceCommandProcessor()

    return VoiceService(
        synthesizer=synthesizer,
        recognizer=recognizer,
        command_processor=command_processor,
        default_voice_config=voice_config,
        default_recognition_config=recognition_config,
    )


def create_voice_service_from_env() -> VoiceService:
    """Create voice service using environment variables."""
    subscription_key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")

    if not subscription_key or not region:
        raise ValueError(
            "AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables must be set"
        )

    azure_config = AzureSpeechConfig(subscription_key=subscription_key, region=region)

    return create_voice_service(azure_config)
