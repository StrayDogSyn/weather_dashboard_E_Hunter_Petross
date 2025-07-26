"""Modern button widget with glassmorphic styling and animations.

This module provides a custom Tkinter button with enhanced visual effects,
hover animations, and glassmorphic design elements.
"""

import tkinter as tk
from typing import Optional, Callable, Any

from ..styles.glassmorphic import GlassmorphicStyle


class ModernButton(tk.Button):
    """Modern button with glassmorphic styling and hover effects."""

    def __init__(self, parent, text: str = "", command: Optional[Callable] = None,
                 style_variant: str = "primary", **kwargs):
        """Initialize modern button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Command to execute on click
            style_variant: Style variant ('primary', 'secondary', 'accent')
            **kwargs: Additional button configuration
        """
        self.style = GlassmorphicStyle()
        self.style_variant = style_variant
        self.original_bg = None
        self.original_fg = None
        self.is_hovered = False
        
        # Set default styling based on variant
        default_config = self._get_default_config()
        default_config.update(kwargs)
        
        super().__init__(parent, text=text, command=command, **default_config)
        
        # Store original colors
        self.original_bg = self.cget('bg')
        self.original_fg = self.cget('fg')
        
        # Bind hover events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _get_default_config(self) -> dict:
        """Get default configuration for button style variant.
        
        Returns:
            Dictionary of default button configuration
        """
        base_config = {
            'font': self.style.fonts['button'],
            'relief': 'flat',
            'borderwidth': 0,
            'cursor': 'hand2',
            'padx': 20,
            'pady': 10,
            'activeforeground': self.style.colors['text_primary'],
        }
        
        if self.style_variant == "primary":
            base_config.update({
                'bg': self.style.colors['accent'],
                'fg': self.style.colors['text_primary'],
                'activebackground': self.style.colors['accent_hover'],
            })
        elif self.style_variant == "secondary":
            base_config.update({
                'bg': self.style.colors['surface'],
                'fg': self.style.colors['text_primary'],
                'activebackground': self.style.colors['surface_hover'],
            })
        elif self.style_variant == "accent":
            base_config.update({
                'bg': self.style.colors['secondary'],
                'fg': self.style.colors['text_primary'],
                'activebackground': self.style.colors['secondary_hover'],
            })
        else:
            # Default to primary
            base_config.update({
                'bg': self.style.colors['accent'],
                'fg': self.style.colors['text_primary'],
                'activebackground': self.style.colors['accent_hover'],
            })
        
        return base_config

    def _on_enter(self, event: tk.Event) -> None:
        """Handle mouse enter event.
        
        Args:
            event: Tkinter event object
        """
        self.is_hovered = True
        self._apply_hover_effect()

    def _on_leave(self, event: tk.Event) -> None:
        """Handle mouse leave event.
        
        Args:
            event: Tkinter event object
        """
        self.is_hovered = False
        self._remove_hover_effect()

    def _on_click(self, event: tk.Event) -> None:
        """Handle mouse click event.
        
        Args:
            event: Tkinter event object
        """
        self._apply_click_effect()

    def _on_release(self, event: tk.Event) -> None:
        """Handle mouse release event.
        
        Args:
            event: Tkinter event object
        """
        if self.is_hovered:
            self._apply_hover_effect()
        else:
            self._remove_hover_effect()

    def _apply_hover_effect(self) -> None:
        """Apply hover visual effects."""
        if self.style_variant == "primary":
            hover_bg = self.style.colors['accent_hover']
        elif self.style_variant == "secondary":
            hover_bg = self.style.colors['surface_hover']
        elif self.style_variant == "accent":
            hover_bg = self.style.colors['secondary_hover']
        else:
            hover_bg = self.style.colors['accent_hover']
        
        self.config(
            bg=hover_bg,
            relief='raised',
            borderwidth=1
        )

    def _remove_hover_effect(self) -> None:
        """Remove hover visual effects."""
        self.config(
            bg=self.original_bg,
            relief='flat',
            borderwidth=0
        )

    def _apply_click_effect(self) -> None:
        """Apply click visual effects."""
        self.config(
            relief='sunken',
            borderwidth=2
        )

    def set_style_variant(self, variant: str) -> None:
        """Change button style variant.
        
        Args:
            variant: New style variant ('primary', 'secondary', 'accent')
        """
        self.style_variant = variant
        config = self._get_default_config()
        
        # Update button configuration
        self.config(
            bg=config['bg'],
            fg=config['fg'],
            activebackground=config['activebackground']
        )
        
        # Update stored original colors
        self.original_bg = config['bg']
        self.original_fg = config['fg']

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button.
        
        Args:
            enabled: Whether button should be enabled
        """
        if enabled:
            self.config(
                state='normal',
                cursor='hand2',
                bg=self.original_bg,
                fg=self.original_fg
            )
        else:
            self.config(
                state='disabled',
                cursor='arrow',
                bg=self.style.colors['surface_disabled'],
                fg=self.style.colors['text_disabled']
            )

    def set_loading(self, loading: bool, loading_text: str = "Loading...") -> None:
        """Set button to loading state.
        
        Args:
            loading: Whether button is in loading state
            loading_text: Text to display during loading
        """
        if loading:
            self.original_text = self.cget('text')
            self.config(
                text=loading_text,
                state='disabled',
                cursor='wait'
            )
        else:
            if hasattr(self, 'original_text'):
                self.config(
                    text=self.original_text,
                    state='normal',
                    cursor='hand2'
                )

    def pulse_effect(self, duration: int = 500) -> None:
        """Apply pulse animation effect.
        
        Args:
            duration: Duration of pulse effect in milliseconds
        """
        original_bg = self.cget('bg')
        pulse_bg = self.style.colors['accent_hover']
        
        # Pulse to highlight color
        self.config(bg=pulse_bg)
        
        # Return to original color after duration
        self.after(duration, lambda: self.config(bg=original_bg))

    def glow_effect(self, color: Optional[str] = None, duration: int = 1000) -> None:
        """Apply glow animation effect.
        
        Args:
            color: Glow color (defaults to accent color)
            duration: Duration of glow effect in milliseconds
        """
        if color is None:
            color = self.style.colors['accent']
        
        original_relief = self.cget('relief')
        original_borderwidth = self.cget('borderwidth')
        
        # Apply glow effect
        self.config(
            relief='solid',
            borderwidth=2,
            highlightbackground=color,
            highlightthickness=2
        )
        
        # Remove glow after duration
        self.after(duration, lambda: self.config(
            relief=original_relief,
            borderwidth=original_borderwidth,
            highlightthickness=0
        ))


class IconButton(ModernButton):
    """Modern button with icon support."""

    def __init__(self, parent, icon: str = "", text: str = "", 
                 command: Optional[Callable] = None, icon_position: str = "left",
                 **kwargs):
        """Initialize icon button.
        
        Args:
            parent: Parent widget
            icon: Icon character or emoji
            text: Button text
            command: Command to execute on click
            icon_position: Position of icon ('left', 'right', 'top', 'bottom')
            **kwargs: Additional button configuration
        """
        self.icon = icon
        self.icon_position = icon_position
        self.button_text = text
        
        # Combine icon and text based on position
        display_text = self._format_display_text()
        
        super().__init__(parent, text=display_text, command=command, **kwargs)

    def _format_display_text(self) -> str:
        """Format display text with icon and text.
        
        Returns:
            Formatted text string with icon
        """
        if not self.icon and not self.button_text:
            return ""
        elif not self.icon:
            return self.button_text
        elif not self.button_text:
            return self.icon
        
        if self.icon_position == "left":
            return f"{self.icon} {self.button_text}"
        elif self.icon_position == "right":
            return f"{self.button_text} {self.icon}"
        elif self.icon_position == "top":
            return f"{self.icon}\n{self.button_text}"
        elif self.icon_position == "bottom":
            return f"{self.button_text}\n{self.icon}"
        else:
            return f"{self.icon} {self.button_text}"

    def set_icon(self, icon: str) -> None:
        """Update button icon.
        
        Args:
            icon: New icon character or emoji
        """
        self.icon = icon
        self.config(text=self._format_display_text())

    def set_text(self, text: str) -> None:
        """Update button text.
        
        Args:
            text: New button text
        """
        self.button_text = text
        self.config(text=self._format_display_text())

    def set_icon_position(self, position: str) -> None:
        """Update icon position.
        
        Args:
            position: New icon position ('left', 'right', 'top', 'bottom')
        """
        self.icon_position = position
        self.config(text=self._format_display_text())