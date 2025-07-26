"""Enhanced button component with improved accessibility and responsive design.

This module provides an advanced button implementation with better visual feedback,
accessibility features, and integration with the responsive layout system.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional

from ..components.responsive_layout import ResponsiveSpacing
from ..styles.glassmorphic import GlassmorphicStyle


class EnhancedButton(tk.Frame):
    """Enhanced button with glassmorphic styling and improved UX."""

    def __init__(
        self,
        parent,
        text: str = "",
        command: Optional[Callable] = None,
        style_variant: str = "primary",
        icon: Optional[str] = None,
        tooltip: Optional[str] = None,
        keyboard_shortcut: Optional[str] = None,
        **kwargs,
    ):
        """Initialize enhanced button.

        Args:
            parent: Parent widget
            text: Button text
            command: Command to execute on click
            style_variant: Style variant ('primary', 'secondary', 'accent', 'danger')
            icon: Optional icon character/emoji
            tooltip: Optional tooltip text
            keyboard_shortcut: Optional keyboard shortcut description
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.text = text
        self.command = command
        self.style_variant = style_variant
        self.icon = icon
        self.tooltip = tooltip
        self.keyboard_shortcut = keyboard_shortcut

        # State management
        self.is_hovered = False
        self.is_pressed = False
        self.is_enabled = True
        self.is_focused = False

        # Style configuration
        self.style = GlassmorphicStyle()
        self._setup_styles()

        # Create button components
        self._create_button_elements()
        self._setup_bindings()

        # Configure frame
        self.configure(bg=self.current_bg, relief="flat", bd=0)

        # Setup tooltip if provided
        if self.tooltip:
            self._setup_tooltip()

    def _setup_styles(self) -> None:
        """Setup style configurations for different variants."""
        self.style_configs = {
            "primary": {
                "bg": self.style.colors["primary"],
                "fg": self.style.colors["on_primary"],
                "hover_bg": self._lighten_color(self.style.colors["primary"], 0.1),
                "active_bg": self._darken_color(self.style.colors["primary"], 0.1),
                "border": self.style.colors["primary_variant"],
            },
            "secondary": {
                "bg": self.style.colors["secondary"],
                "fg": self.style.colors["on_secondary"],
                "hover_bg": self._lighten_color(self.style.colors["secondary"], 0.1),
                "active_bg": self._darken_color(self.style.colors["secondary"], 0.1),
                "border": self.style.colors["secondary_variant"],
            },
            "accent": {
                "bg": self.style.colors["accent"],
                "fg": self.style.colors["on_accent"],
                "hover_bg": self._lighten_color(self.style.colors["accent"], 0.1),
                "active_bg": self._darken_color(self.style.colors["accent"], 0.1),
                "border": self.style.colors["accent"],
            },
            "danger": {
                "bg": self.style.colors.get("error", "#dc3545"),
                "fg": "#ffffff",
                "hover_bg": "#c82333",
                "active_bg": "#bd2130",
                "border": "#dc3545",
            },
            "ghost": {
                "bg": "transparent",
                "fg": self.style.colors["on_surface"],
                "hover_bg": self.style.colors["surface_variant"],
                "active_bg": self.style.colors["outline"],
                "border": self.style.colors["outline"],
            },
        }

        # Set current style
        self.current_style = self.style_configs.get(
            self.style_variant, self.style_configs["primary"]
        )
        self.current_bg = self.current_style["bg"]
        self.current_fg = self.current_style["fg"]

    def _create_button_elements(self) -> None:
        """Create button visual elements."""
        # Main button frame with glassmorphic effect
        self.button_frame = tk.Frame(
            self,
            bg=self.current_bg,
            relief="flat",
            bd=0,
            highlightthickness=2,
            highlightcolor=self.current_style["border"],
            highlightbackground=self.current_style["border"],
        )
        self.button_frame.pack(fill=tk.BOTH, expand=True)

        # Content container
        self.content_frame = tk.Frame(self.button_frame, bg=self.current_bg)
        self.content_frame.pack(
            padx=ResponsiveSpacing.BUTTON_PADDING_X,
            pady=ResponsiveSpacing.BUTTON_PADDING_Y,
        )

        # Icon label (if provided)
        if self.icon:
            self.icon_label = tk.Label(
                self.content_frame,
                text=self.icon,
                bg=self.current_bg,
                fg=self.current_fg,
                font=self.style.fonts["icon"],
            )
            self.icon_label.pack(side=tk.LEFT, padx=(0, ResponsiveSpacing.SMALL))

        # Text container for multi-line support
        self.text_frame = tk.Frame(self.content_frame, bg=self.current_bg)
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Main text label
        main_text = self.text.split("\n")[0] if "\n" in self.text else self.text
        self.text_label = tk.Label(
            self.text_frame,
            text=main_text,
            bg=self.current_bg,
            fg=self.current_fg,
            font=self.style.fonts["button"],
        )
        self.text_label.pack()

        # Keyboard shortcut label (if provided)
        if self.keyboard_shortcut or (
            "\n" in self.text and len(self.text.split("\n")) > 1
        ):
            shortcut_text = self.keyboard_shortcut or self.text.split("\n")[1]
            self.shortcut_label = tk.Label(
                self.text_frame,
                text=shortcut_text,
                bg=self.current_bg,
                fg=self._adjust_opacity(self.current_fg, 0.7),
                font=self.style.fonts["caption"],
            )
            self.shortcut_label.pack()

        # Focus indicator
        self.focus_indicator = tk.Frame(
            self.button_frame, height=2, bg=self.current_style["border"]
        )
        # Initially hidden

        # Ripple effect frame (for click animation)
        self.ripple_frame = tk.Frame(
            self.button_frame, bg=self.current_style["active_bg"]
        )
        # Initially hidden

    def _setup_bindings(self) -> None:
        """Setup event bindings for interaction."""
        # Bind events to all components for consistent behavior
        components = [
            self,
            self.button_frame,
            self.content_frame,
            self.text_frame,
            self.text_label,
        ]

        if hasattr(self, "icon_label"):
            components.append(self.icon_label)
        if hasattr(self, "shortcut_label"):
            components.append(self.shortcut_label)

        for component in components:
            component.bind("<Button-1>", self._on_click)
            component.bind("<Enter>", self._on_enter)
            component.bind("<Leave>", self._on_leave)
            component.bind("<ButtonPress-1>", self._on_press)
            component.bind("<ButtonRelease-1>", self._on_release)
            component.bind("<FocusIn>", self._on_focus_in)
            component.bind("<FocusOut>", self._on_focus_out)

        # Make button focusable
        self.focus_set()
        self.bind("<Return>", self._on_click)
        self.bind("<space>", self._on_click)

    def _setup_tooltip(self) -> None:
        """Setup tooltip functionality."""
        self.tooltip_window = None

        def show_tooltip(event=None):
            if self.tooltip_window or not self.tooltip:
                return

            x = self.winfo_rootx() + 25
            y = self.winfo_rooty() + self.winfo_height() + 5

            self.tooltip_window = tk.Toplevel(self)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

            tooltip_label = tk.Label(
                self.tooltip_window,
                text=self.tooltip,
                bg=self.style.colors["surface_variant"],
                fg=self.style.colors["on_surface"],
                font=self.style.fonts["caption"],
                relief="solid",
                borderwidth=1,
                padx=ResponsiveSpacing.SMALL,
                pady=ResponsiveSpacing.TINY,
            )
            tooltip_label.pack()

        def hide_tooltip(event=None):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None

        self.bind("<Enter>", lambda e: self.after(500, show_tooltip))
        self.bind("<Leave>", hide_tooltip)

    def _on_enter(self, event=None) -> None:
        """Handle mouse enter event."""
        if not self.is_enabled:
            return

        self.is_hovered = True
        self._update_appearance()

    def _on_leave(self, event=None) -> None:
        """Handle mouse leave event."""
        self.is_hovered = False
        self.is_pressed = False
        self._update_appearance()

    def _on_press(self, event=None) -> None:
        """Handle button press event."""
        if not self.is_enabled:
            return

        self.is_pressed = True
        self._update_appearance()
        self._show_ripple_effect()

    def _on_release(self, event=None) -> None:
        """Handle button release event."""
        if not self.is_enabled:
            return

        self.is_pressed = False
        self._update_appearance()

    def _on_click(self, event=None) -> None:
        """Handle button click event."""
        if not self.is_enabled or not self.command:
            return

        try:
            self.command()
        except Exception as e:
            print(f"Button command error: {e}")

    def _on_focus_in(self, event=None) -> None:
        """Handle focus in event."""
        self.is_focused = True
        self.focus_indicator.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_appearance()

    def _on_focus_out(self, event=None) -> None:
        """Handle focus out event."""
        self.is_focused = False
        self.focus_indicator.pack_forget()
        self._update_appearance()

    def _update_appearance(self) -> None:
        """Update button appearance based on current state."""
        if not self.is_enabled:
            bg_color = self._adjust_opacity(self.current_style["bg"], 0.5)
            fg_color = self._adjust_opacity(self.current_style["fg"], 0.5)
        elif self.is_pressed:
            bg_color = self.current_style["active_bg"]
            fg_color = self.current_style["fg"]
        elif self.is_hovered:
            bg_color = self.current_style["hover_bg"]
            fg_color = self.current_style["fg"]
        else:
            bg_color = self.current_style["bg"]
            fg_color = self.current_style["fg"]

        # Update all components
        components_to_update = [
            self,
            self.button_frame,
            self.content_frame,
            self.text_frame,
            self.text_label,
        ]

        if hasattr(self, "icon_label"):
            components_to_update.append(self.icon_label)
        if hasattr(self, "shortcut_label"):
            components_to_update.append(self.shortcut_label)

        for component in components_to_update:
            try:
                component.configure(bg=bg_color)
                if hasattr(component, "configure") and "fg" in component.configure():
                    component.configure(fg=fg_color)
            except tk.TclError:
                pass  # Component might be destroyed

    def _show_ripple_effect(self) -> None:
        """Show ripple effect animation."""
        # Simple ripple effect simulation
        self.ripple_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.ripple_frame.configure(bg=self.current_style["active_bg"])

        # Fade out effect
        def fade_ripple(alpha=1.0):
            if alpha > 0:
                alpha -= 0.1
                # Simulate fade by adjusting background
                self.after(20, lambda: fade_ripple(alpha))
            else:
                self.ripple_frame.place_forget()

        self.after(50, lambda: fade_ripple())

    def set_enabled(self, enabled: bool) -> None:
        """Set button enabled state.

        Args:
            enabled: Whether button should be enabled
        """
        self.is_enabled = enabled
        self._update_appearance()

        if enabled:
            self.configure(cursor="hand2")
        else:
            self.configure(cursor="arrow")

    def set_style_variant(self, variant: str) -> None:
        """Change button style variant.

        Args:
            variant: New style variant
        """
        if variant in self.style_configs:
            self.style_variant = variant
            self.current_style = self.style_configs[variant]
            self.current_bg = self.current_style["bg"]
            self.current_fg = self.current_style["fg"]
            self._update_appearance()

    def _lighten_color(self, color: str, factor: float) -> str:
        """Lighten a color by a given factor.

        Args:
            color: Hex color string
            factor: Lightening factor (0.0 to 1.0)

        Returns:
            Lightened color hex string
        """
        # Simple color lightening (could be enhanced with proper color space conversion)
        if color.startswith("#"):
            color = color[1:]

        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))

            return f"#{r: 02x}{g: 02x}{b: 02x}"
        except (ValueError, IndexError):
            return color

    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a color by a given factor.

        Args:
            color: Hex color string
            factor: Darkening factor (0.0 to 1.0)

        Returns:
            Darkened color hex string
        """
        if color.startswith("#"):
            color = color[1:]

        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))

            return f"#{r: 02x}{g: 02x}{b: 02x}"
        except (ValueError, IndexError):
            return color

    def _adjust_opacity(self, color: str, opacity: float) -> str:
        """Adjust color opacity (simplified version).

        Args:
            color: Hex color string
            opacity: Opacity factor (0.0 to 1.0)

        Returns:
            Color with adjusted opacity
        """
        # For simplicity, we'll darken the color to simulate reduced opacity
        return self._darken_color(color, 1 - opacity)


class ButtonFactory:
    """Factory for creating standardized buttons."""

    @staticmethod
    def create_chart_button(
        parent, chart_type: str, command: Callable, layout_manager=None
    ) -> EnhancedButton:
        """Create a standardized chart button.

        Args:
            parent: Parent widget
            chart_type: Type of chart ('temperature', 'metrics', etc.)
            command: Command to execute
            layout_manager: Optional layout manager

        Returns:
            EnhancedButton instance
        """
        button_configs = {
            "temperature": {
                "text": "Temperature Trend",
                "icon": "📈",
                "shortcut": "Ctrl+1",
                "tooltip": "Show temperature trend chart over time",
            },
            "metrics": {
                "text": "Weather Metrics",
                "icon": "📊",
                "shortcut": "Ctrl+2",
                "tooltip": "Display comprehensive weather metrics",
            },
            "forecast": {
                "text": "5-Day Forecast",
                "icon": "🌤️",
                "shortcut": "Ctrl+3",
                "tooltip": "View extended weather forecast",
            },
            "humidity_pressure": {
                "text": "Humidity & Pressure",
                "icon": "💧",
                "shortcut": "Ctrl+4",
                "tooltip": "Monitor humidity and atmospheric pressure",
            },
        }

        config = button_configs.get(
            chart_type,
            {
                "text": chart_type.title(),
                "icon": "📊",
                "shortcut": "",
                "tooltip": f"Show {chart_type} chart",
            },
        )

        return EnhancedButton(
            parent,
            text=config["text"],
            command=command,
            icon=config["icon"],
            keyboard_shortcut=config["shortcut"],
            tooltip=config["tooltip"],
            style_variant="primary",
        )

    @staticmethod
    def create_action_button(
        parent, action_type: str, command: Callable
    ) -> EnhancedButton:
        """Create a standardized action button.

        Args:
            parent: Parent widget
            action_type: Type of action ('refresh', 'help', etc.)
            command: Command to execute

        Returns:
            EnhancedButton instance
        """
        action_configs = {
            "refresh": {
                "text": "Refresh All",
                "icon": "🔄",
                "shortcut": "Ctrl+R",
                "tooltip": "Refresh all weather data",
                "style": "secondary",
            },
            "help": {
                "text": "Help",
                "icon": "❓",
                "shortcut": "Ctrl+H",
                "tooltip": "Show help and keyboard shortcuts",
                "style": "accent",
            },
            "settings": {
                "text": "Settings",
                "icon": "⚙️",
                "shortcut": "Ctrl+,",
                "tooltip": "Open application settings",
                "style": "ghost",
            },
        }

        config = action_configs.get(
            action_type,
            {
                "text": action_type.title(),
                "icon": "🔧",
                "shortcut": "",
                "tooltip": f"Execute {action_type} action",
                "style": "secondary",
            },
        )

        return EnhancedButton(
            parent,
            text=config["text"],
            command=command,
            icon=config["icon"],
            keyboard_shortcut=config["shortcut"],
            tooltip=config["tooltip"],
            style_variant=config["style"],
        )
