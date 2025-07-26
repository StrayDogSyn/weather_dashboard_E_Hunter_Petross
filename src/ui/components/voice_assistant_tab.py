"""Voice Assistant Tab Component for Weather Dashboard.

This module provides a comprehensive voice interface for the Cortana voice assistant,
integrating speech-to-text, text-to-speech, and voice command processing.
"""

import asyncio
import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional

from ...business.interfaces import ICortanaVoiceService
from ..styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from ..widgets.enhanced_button import ButtonFactory
from ..widgets.modern_button import ModernButton
from .responsive_layout import ResponsiveSpacing


class VoiceAssistantTab(GlassmorphicFrame):
    """Voice Assistant Tab with speech recognition and synthesis capabilities."""

    def __init__(
        self,
        parent,
        voice_service: Optional[ICortanaVoiceService] = None,
        on_voice_command: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        """Initialize voice assistant tab.

        Args:
            parent: Parent widget
            voice_service: Cortana voice service instance
            on_voice_command: Callback for voice commands
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)

        self.style = GlassmorphicStyle()
        self.button_factory = ButtonFactory()
        self.logger = logging.getLogger(__name__)

        # Services
        self.voice_service = voice_service
        self.on_voice_command = on_voice_command

        # State
        self.is_listening = False
        self.is_speaking = False
        self.current_city = None
        self.conversation_history = []

        # UI Components
        self.status_label: Optional[tk.Label] = None
        self.listen_button: Optional[ModernButton] = None
        self.stop_button: Optional[ModernButton] = None
        self.conversation_text: Optional[tk.Text] = None
        self.command_entry: Optional[tk.Entry] = None
        self.send_button: Optional[ModernButton] = None
        self.voice_profile_var: Optional[tk.StringVar] = None
        self.voice_profile_combo: Optional[ttk.Combobox] = None

        self._setup_ui()
        self._update_voice_status()

    def _setup_ui(self) -> None:
        """Set up the voice assistant user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header section
        self._create_header_section()

        # Main content area
        self._create_main_content()

        # Control panel
        self._create_control_panel()

    def _create_header_section(self) -> None:
        """Create header section with status and controls."""
        header_frame = GlassmorphicFrame(self, padding=ResponsiveSpacing.MEDIUM)
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=ResponsiveSpacing.MEDIUM,
            pady=(ResponsiveSpacing.MEDIUM, 0),
        )
        header_frame.grid_columnconfigure(1, weight=1)

        # Voice status indicator
        self.status_label = tk.Label(
            header_frame,
            text="Voice Assistant Ready",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        # Voice profile selection
        profile_frame = tk.Frame(header_frame, bg=self.style.colors["surface"])
        profile_frame.grid(
            row=0, column=1, sticky="e", padx=(ResponsiveSpacing.MEDIUM, 0)
        )

        tk.Label(
            profile_frame,
            text="Voice Profile:",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        ).pack(side="left", padx=(0, ResponsiveSpacing.SMALL))

        self.voice_profile_var = tk.StringVar(value="en-US_Standard")
        self.voice_profile_combo = ttk.Combobox(
            profile_frame,
            textvariable=self.voice_profile_var,
            values=self._get_voice_profiles(),
            state="readonly",
            width=15,
        )
        self.voice_profile_combo.pack(side="left")
        self.voice_profile_combo.bind(
            "<<ComboboxSelected>>", self._on_voice_profile_change
        )

    def _create_main_content(self) -> None:
        """Create main conversation area."""
        main_frame = GlassmorphicFrame(self, padding=ResponsiveSpacing.MEDIUM)
        main_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=ResponsiveSpacing.MEDIUM,
            pady=ResponsiveSpacing.SMALL,
        )
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Conversation history
        conversation_frame = tk.Frame(main_frame, bg=self.style.colors["surface"])
        conversation_frame.grid(row=0, column=0, sticky="nsew")
        conversation_frame.grid_columnconfigure(0, weight=1)
        conversation_frame.grid_rowconfigure(0, weight=1)

        # Conversation text area with scrollbar
        text_frame = tk.Frame(conversation_frame, bg=self.style.colors["surface"])
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        self.conversation_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=self.style.fonts["body"],
            bg=self.style.colors["background"],
            fg=self.style.colors["text_primary"],
            insertbackground=self.style.colors["accent"],
            selectbackground=self.style.colors["accent"],
            relief="flat",
            padx=ResponsiveSpacing.MEDIUM,
            pady=ResponsiveSpacing.MEDIUM,
            state="disabled",
        )
        self.conversation_text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for conversation
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.conversation_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.conversation_text.config(yscrollcommand=scrollbar.set)

        # Add initial welcome message
        self._add_conversation_message(
            "Cortana",
            "Hello! I'm your weather assistant. You can ask me about weather conditions, forecasts, and more. Try saying 'get weather for New York' or type your command below.",
        )

    def _create_control_panel(self) -> None:
        """Create control panel with voice and text input."""
        control_frame = GlassmorphicFrame(self, padding=ResponsiveSpacing.MEDIUM)
        control_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=ResponsiveSpacing.MEDIUM,
            pady=(0, ResponsiveSpacing.MEDIUM),
        )
        control_frame.grid_columnconfigure(1, weight=1)

        # Voice control buttons
        voice_buttons_frame = tk.Frame(control_frame, bg=self.style.colors["surface"])
        voice_buttons_frame.grid(
            row=0, column=0, sticky="w", padx=(0, ResponsiveSpacing.MEDIUM)
        )

        self.listen_button = self.button_factory.create_button(
            voice_buttons_frame,
            text="🎤 Listen",
            command=self._start_listening,
            style="primary",
        )
        self.listen_button.pack(side="left", padx=(0, ResponsiveSpacing.SMALL))

        self.stop_button = self.button_factory.create_button(
            voice_buttons_frame,
            text="⏹️ Stop",
            command=self._stop_listening,
            style="secondary",
            state="disabled",
        )
        self.stop_button.pack(side="left")

        # Text input area
        input_frame = tk.Frame(control_frame, bg=self.style.colors["surface"])
        input_frame.grid(
            row=0, column=1, sticky="ew", padx=(0, ResponsiveSpacing.MEDIUM)
        )
        input_frame.grid_columnconfigure(0, weight=1)

        self.command_entry = tk.Entry(
            input_frame,
            font=self.style.fonts["body"],
            bg=self.style.colors["background"],
            fg=self.style.colors["text_primary"],
            insertbackground=self.style.colors["accent"],
            relief="flat",
            bd=1,
        )
        self.command_entry.grid(
            row=0, column=0, sticky="ew", padx=(0, ResponsiveSpacing.SMALL)
        )
        self.command_entry.bind("<Return>", self._on_text_command)
        self.command_entry.bind("<KeyPress>", self._on_typing)

        # Send button
        self.send_button = self.button_factory.create_button(
            control_frame,
            text="Send",
            command=self._send_text_command,
            style="primary",
        )
        self.send_button.grid(row=0, column=2, sticky="e")

    def _get_voice_profiles(self) -> list:
        """Get available voice profiles.

        Returns:
            List of available voice profiles
        """
        if self.voice_service:
            try:
                return self.voice_service.get_available_voice_profiles()
            except Exception as e:
                self.logger.warning(f"Failed to get voice profiles: {e}")

        return ["en-US_Standard", "en-US_Neural", "en-GB_Standard", "en-AU_Standard"]

    def _update_voice_status(self) -> None:
        """Update voice status display."""
        if not self.status_label:
            return

        if not self.voice_service:
            self.status_label.config(
                text="Voice Assistant Unavailable", fg=self.style.colors["error"]
            )
            self._disable_voice_controls()
            return

        if self.is_listening:
            self.status_label.config(
                text="🎤 Listening...", fg=self.style.colors["accent"]
            )
        elif self.is_speaking:
            self.status_label.config(
                text="🔊 Speaking...", fg=self.style.colors["accent"]
            )
        else:
            self.status_label.config(
                text="Voice Assistant Ready", fg=self.style.colors["success"]
            )

    def _disable_voice_controls(self) -> None:
        """Disable voice control buttons when service is unavailable."""
        if self.listen_button:
            self.listen_button.config(state="disabled")
        if self.stop_button:
            self.stop_button.config(state="disabled")

    def _start_listening(self) -> None:
        """Start voice listening."""
        if not self.voice_service:
            self._add_conversation_message("System", "Voice service is not available.")
            return

        if self.is_listening:
            return

        self.is_listening = True
        self._update_voice_status()

        # Update button states
        self.listen_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # Start listening in separate thread
        threading.Thread(target=self._listen_for_speech, daemon=True).start()

        self._add_conversation_message("System", "Listening for your command...")

    def _stop_listening(self) -> None:
        """Stop voice listening."""
        self.is_listening = False
        self._update_voice_status()

        # Update button states
        self.listen_button.config(state="normal")
        self.stop_button.config(state="disabled")

        self._add_conversation_message("System", "Stopped listening.")

    def _listen_for_speech(self) -> None:
        """Listen for speech input (placeholder implementation)."""
        try:
            # Simulate listening delay
            import time

            time.sleep(2)

            if not self.is_listening:
                return

            # Placeholder: In a real implementation, this would capture audio
            # and use the voice service's speech_to_text method

            # For now, simulate a recognized command
            recognized_text = "get weather for London"

            # Process the recognized command
            self.after(0, lambda: self._process_recognized_speech(recognized_text))

        except Exception as e:
            self.logger.error(f"Error during speech recognition: {e}")
            self.after(
                0,
                lambda: self._add_conversation_message(
                    "System", f"Speech recognition error: {e}"
                ),
            )
        finally:
            self.after(0, self._stop_listening)

    def _process_recognized_speech(self, text: str) -> None:
        """Process recognized speech text.

        Args:
            text: Recognized speech text
        """
        self._add_conversation_message("You", text)
        self._process_voice_command(text)

    def _on_text_command(self, event) -> None:
        """Handle text command entry.

        Args:
            event: Key press event
        """
        self._send_text_command()

    def _on_typing(self, event) -> None:
        """Handle typing in command entry.

        Args:
            event: Key press event
        """
        # Could add typing indicators or auto-complete here
        pass

    def _send_text_command(self) -> None:
        """Send text command."""
        command = self.command_entry.get().strip()
        if not command:
            return

        # Clear the entry
        self.command_entry.delete(0, tk.END)

        # Add to conversation
        self._add_conversation_message("You", command)

        # Process the command
        self._process_voice_command(command)

    def _process_voice_command(self, command: str) -> None:
        """Process voice command.

        Args:
            command: Voice command text
        """
        if not self.voice_service:
            response = "Voice service is not available."
            self._add_conversation_message("Cortana", response)
            return

        # Process command in separate thread
        threading.Thread(
            target=self._process_command_async, args=(command,), daemon=True
        ).start()

    def _process_command_async(self, command: str) -> None:
        """Process command asynchronously.

        Args:
            command: Voice command text
        """
        try:
            # Extract city from command if present
            city = self._extract_city_from_command(command)

            # Use the existing voice service's process_voice_command method
            if hasattr(self.voice_service, "process_voice_command"):
                response = self.voice_service.process_voice_command(command, city)
            else:
                response = "Voice command processing is not available."

            # Update UI in main thread
            self.after(0, lambda: self._add_conversation_message("Cortana", response))

            # Trigger text-to-speech if available
            if response and hasattr(self.voice_service, "text_to_speech"):
                self.after(0, lambda: self._speak_response(response))

            # Call external command callback
            if self.on_voice_command:
                self.after(0, lambda: self.on_voice_command(command))

        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            error_response = (
                "I'm sorry, I encountered an error processing your request."
            )
            self.after(
                0, lambda: self._add_conversation_message("Cortana", error_response)
            )

    def _extract_city_from_command(self, command: str) -> Optional[str]:
        """Extract city name from voice command.

        Args:
            command: Voice command text

        Returns:
            Extracted city name or None
        """
        # Simple city extraction logic
        command_lower = command.lower()

        # Look for "for [city]" pattern
        if " for " in command_lower:
            parts = command_lower.split(" for ")
            if len(parts) > 1:
                city = parts[1].strip()
                # Remove common trailing words
                for word in ["please", "today", "now", "currently"]:
                    if city.endswith(f" {word}"):
                        city = city[: -len(f" {word}")]
                return city.title()

        # Look for "in [city]" pattern
        if " in " in command_lower:
            parts = command_lower.split(" in ")
            if len(parts) > 1:
                city = parts[1].strip()
                return city.title()

        return self.current_city

    def _speak_response(self, text: str) -> None:
        """Speak response using text-to-speech.

        Args:
            text: Text to speak
        """
        if not self.voice_service or self.is_speaking:
            return

        self.is_speaking = True
        self._update_voice_status()

        # Start speaking in separate thread
        threading.Thread(target=self._speak_async, args=(text,), daemon=True).start()

    def _speak_async(self, text: str) -> None:
        """Speak text asynchronously.

        Args:
            text: Text to speak
        """
        try:
            # Placeholder: In a real implementation, this would use
            # the voice service's text_to_speech method
            import time

            time.sleep(len(text) * 0.05)  # Simulate speaking time

        except Exception as e:
            self.logger.error(f"Error during text-to-speech: {e}")
        finally:
            self.is_speaking = False
            self.after(0, self._update_voice_status)

    def _add_conversation_message(self, sender: str, message: str) -> None:
        """Add message to conversation history.

        Args:
            sender: Message sender (You, Cortana, System)
            message: Message content
        """
        if not self.conversation_text:
            return

        # Enable text widget for editing
        self.conversation_text.config(state="normal")

        # Add timestamp
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Format message based on sender
        if sender == "You":
            formatted_message = f"[{timestamp}] You: {message}\n\n"
            tag = "user"
        elif sender == "Cortana":
            formatted_message = f"[{timestamp}] Cortana: {message}\n\n"
            tag = "assistant"
        else:
            formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
            tag = "system"

        # Insert message
        self.conversation_text.insert(tk.END, formatted_message, tag)

        # Configure tags for styling
        self.conversation_text.tag_config(
            "user", foreground=self.style.colors["accent"]
        )
        self.conversation_text.tag_config(
            "assistant", foreground=self.style.colors["success"]
        )
        self.conversation_text.tag_config(
            "system", foreground=self.style.colors["text_secondary"]
        )

        # Scroll to bottom
        self.conversation_text.see(tk.END)

        # Disable text widget
        self.conversation_text.config(state="disabled")

        # Store in history
        self.conversation_history.append(
            {"timestamp": timestamp, "sender": sender, "message": message}
        )

    def _on_voice_profile_change(self, event) -> None:
        """Handle voice profile change.

        Args:
            event: Combobox selection event
        """
        new_profile = self.voice_profile_var.get()
        self.logger.info(f"Voice profile changed to: {new_profile}")

        # Configure voice service with new profile
        if self.voice_service and hasattr(
            self.voice_service, "configure_voice_settings"
        ):
            try:
                asyncio.run(
                    self.voice_service.configure_voice_settings(
                        {"voice_profile": new_profile}
                    )
                )
                self._add_conversation_message(
                    "System", f"Voice profile changed to {new_profile}"
                )
            except Exception as e:
                self.logger.error(f"Failed to change voice profile: {e}")
                self._add_conversation_message(
                    "System", f"Failed to change voice profile: {e}"
                )

    def set_current_city(self, city: str) -> None:
        """Set current city for voice commands.

        Args:
            city: Current city name
        """
        self.current_city = city
        self.logger.info(f"Current city set to: {city}")

    def clear_conversation(self) -> None:
        """Clear conversation history."""
        if self.conversation_text:
            self.conversation_text.config(state="normal")
            self.conversation_text.delete(1.0, tk.END)
            self.conversation_text.config(state="disabled")

        self.conversation_history.clear()
        self._add_conversation_message("System", "Conversation cleared.")

    def get_conversation_history(self) -> list:
        """Get conversation history.

        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()

    def set_voice_service(self, voice_service: ICortanaVoiceService) -> None:
        """Set voice service.

        Args:
            voice_service: Cortana voice service instance
        """
        self.voice_service = voice_service
        self._update_voice_status()

        # Update voice profiles
        if self.voice_profile_combo:
            profiles = self._get_voice_profiles()
            self.voice_profile_combo.config(values=profiles)
            if profiles:
                self.voice_profile_var.set(profiles[0])
