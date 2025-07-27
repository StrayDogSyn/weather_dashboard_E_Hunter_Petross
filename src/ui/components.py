"""
UI Components Module for Weather Dashboard.

This module contains reusable UI components including frames, buttons,
entries, and scrollable containers.
"""

import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import DANGER
from ttkbootstrap.constants import DARK
from ttkbootstrap.constants import INFO
from ttkbootstrap.constants import LIGHT
from ttkbootstrap.constants import PRIMARY
from ttkbootstrap.constants import SECONDARY

from src.services.sound_service import SoundType
from src.services.sound_service import play_sound

from .styling import GlassmorphicStyle


class GlassmorphicFrame(tk.Frame):
    """Custom frame with enhanced glassmorphic styling and 3D effects."""

    def __init__(
        self,
        parent,
        bg_color=None,
        border_color=None,
        elevated=False,
        gradient=False,
        blur_intensity=None,
        padding=None,
        **kwargs,
    ):
        # Remove custom parameters from kwargs to avoid passing them to tkinter
        if "blur_intensity" in kwargs:
            blur_intensity = kwargs.pop("blur_intensity")
        if "padding" in kwargs:
            padding = kwargs.pop("padding")

        super().__init__(parent, **kwargs)

        # Store padding for potential use in layout
        self.padding = padding or 0

        self.bg_color = bg_color or GlassmorphicStyle.GLASS_BG
        self.border_color = border_color or GlassmorphicStyle.GLASS_BORDER
        self.elevated = elevated
        self.gradient = gradient

        # Set blur intensity (higher value = more blur effect in border)
        blur_effect = 3  # Default
        if blur_intensity is not None:
            if blur_intensity > 10:
                blur_effect = 5  # High blur
            elif blur_intensity > 5:
                blur_effect = 4  # Medium blur

        # Enhanced styling with 3D effect and optional gradient
        if elevated:
            # Create elevated/raised appearance with shadow effect
            self.configure(
                bg=GlassmorphicStyle.GLASS_BG_LIGHT if gradient else self.bg_color,
                highlightbackground=GlassmorphicStyle.GLASS_BORDER_LIGHT,
                highlightcolor="#777777",
                highlightthickness=blur_effect,
                relief="raised",
                borderwidth=blur_effect,
            )
        else:
            # Enhanced standard glassmorphic styling with subtle 3D
            self.configure(
                bg=self.bg_color,
                highlightbackground=self.border_color,
                highlightcolor=GlassmorphicStyle.GLASS_BORDER_LIGHT,
                highlightthickness=2,
                relief="ridge",
                borderwidth=2,
            )


class ModernButton(tk.Button):
    """Modern styled button with enhanced hover effects, 3D appearance, and animations."""

    def __init__(self, parent, style="primary", icon=None, **kwargs):
        self.style = style
        self.icon = icon
        self.default_bg = self._get_bg_color()
        self.hover_bg = self._get_hover_color()
        self.is_hovered = False

        # Prepare button text with icon if provided
        text = kwargs.get("text", "")
        if self.icon:
            text = f"{self.icon} {text}"
            kwargs["text"] = text

        super().__init__(
            parent,
            bg=self.default_bg,
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            relief="flat",  # Flat modern style
            borderwidth=0,  # No border for cleaner look
            padx=8,  # Reduced horizontal padding for more compact buttons
            pady=4,  # Reduced vertical padding for more compact look
            cursor="hand2",
            activebackground=self.hover_bg,
            activeforeground=GlassmorphicStyle.TEXT_PRIMARY,
            # Adding rounded corners effect with highlightbackground
            highlightbackground=self.default_bg,
            highlightcolor=self.default_bg,
            highlightthickness=1,
            **kwargs,
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_click(self, event):
        """Handle button click for modern pressed effect with animation and sound."""
        # Modern buttons use color and subtle scaling rather than relief changes
        click_color = self._get_click_color()
        self.configure(bg=click_color)
        # Add subtle shadow effect
        self.configure(highlightbackground=GlassmorphicStyle.GLASS_BORDER)
        # Play click sound
        play_sound(SoundType.BUTTON_CLICK)

    def _on_release(self, event):
        """Handle button release to restore appearance with modern style."""
        self.configure(bg=self.hover_bg if self.is_hovered else self.default_bg)
        # Restore highlight to match background for seamless look
        self.configure(
            highlightbackground=self.hover_bg if self.is_hovered else self.default_bg
        )

    def _get_bg_color(self):
        if self.style == "primary":
            return GlassmorphicStyle.ACCENT
        elif self.style == "secondary":
            return GlassmorphicStyle.ACCENT_SECONDARY
        elif self.style == "success":
            return GlassmorphicStyle.SUCCESS
        elif self.style == "warning":
            return GlassmorphicStyle.WARNING
        elif self.style == "error":
            return GlassmorphicStyle.ERROR
        else:
            return GlassmorphicStyle.GLASS_BG

    def _get_hover_color(self):
        # Slightly lighter version of the base color
        base = self._get_bg_color()
        if base == GlassmorphicStyle.ACCENT:
            return GlassmorphicStyle.ACCENT_LIGHT
        elif base == GlassmorphicStyle.ACCENT_SECONDARY:
            return GlassmorphicStyle.ACCENT_SECONDARY_LIGHT
        elif base == GlassmorphicStyle.SUCCESS:
            return GlassmorphicStyle.SUCCESS_LIGHT
        elif base == GlassmorphicStyle.WARNING:
            return GlassmorphicStyle.WARNING_LIGHT
        elif base == GlassmorphicStyle.ERROR:
            return GlassmorphicStyle.ERROR_LIGHT
        else:
            return GlassmorphicStyle.GLASS_BG_LIGHT

    def _get_click_color(self):
        # Darker version for click effect
        base = self._get_bg_color()
        if base == GlassmorphicStyle.ACCENT:
            return GlassmorphicStyle.ACCENT_DARK
        elif base == GlassmorphicStyle.ACCENT_SECONDARY:
            return GlassmorphicStyle.ACCENT_SECONDARY_DARK
        else:
            return base

    def _on_enter(self, event):
        self.is_hovered = True
        self.configure(bg=self.hover_bg)
        # Add subtle glow effect with matching highlight for seamless rounded corners
        self.configure(highlightbackground=self.hover_bg, highlightcolor=self.hover_bg)
        # Subtle text brightening for modern feedback
        self.configure(fg="#ffffff")
        # Play subtle hover sound - use BUTTON_CLICK at low volume
        play_sound(SoundType.BUTTON_CLICK, 0.1)

    def _on_leave(self, event):
        self.is_hovered = False
        self.configure(bg=self.default_bg)
        # Match highlight to background for seamless look
        self.configure(
            highlightbackground=self.default_bg, highlightcolor=self.default_bg
        )
        # Restore normal text
        self.configure(fg=GlassmorphicStyle.TEXT_PRIMARY)


class BootstrapButton(ttk_bs.Button):
    """Modern Bootstrap-style button using ttkbootstrap."""

    def __init__(self, parent, style="primary", icon=None, **kwargs):
        # Prepare button text with icon if provided
        text = kwargs.get("text", "")
        if icon:
            text = f"{icon} {text}"
            kwargs["text"] = text

        # Initialize with ttkbootstrap - it inherits from ttk.Button
        super().__init__(parent, **kwargs)


class BootstrapFrame(ttk_bs.Frame):
    """Modern Bootstrap-style frame using ttkbootstrap."""

    def __init__(self, parent, style="", **kwargs):
        super().__init__(parent, **kwargs)


class ModernEntry(tk.Entry):
    """Modern styled entry with glassmorphic design and placeholder support."""

    def __init__(self, parent, placeholder="", **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = GlassmorphicStyle.TEXT_SECONDARY
        self.normal_color = GlassmorphicStyle.TEXT_PRIMARY
        self.has_placeholder = True

        super().__init__(
            parent,
            bg=GlassmorphicStyle.GLASS_BG,
            fg=self.placeholder_color,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=0,
            highlightbackground=GlassmorphicStyle.GLASS_BORDER,
            highlightcolor=GlassmorphicStyle.ACCENT,
            highlightthickness=2,
            insertbackground=GlassmorphicStyle.TEXT_PRIMARY,
            **kwargs,
        )

        if self.placeholder:
            self.insert(0, self.placeholder)
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        """Handle focus in event to clear placeholder."""
        if self.has_placeholder and self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg=self.normal_color)
            self.has_placeholder = False

    def _on_focus_out(self, event):
        """Handle focus out event to restore placeholder if empty."""
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=self.placeholder_color)
            self.has_placeholder = True

    def get(self):
        """Override get to return empty string if placeholder is shown."""
        value = super().get()
        if self.has_placeholder and value == self.placeholder:
            return ""
        return value


class BootstrapEntry(ttk_bs.Entry):
    """Modern Bootstrap-style entry using ttkbootstrap."""

    def __init__(self, parent, style="primary", **kwargs):
        super().__init__(parent, **kwargs)


class ModernScrollableFrame(tk.Frame):
    """Scrollable frame with modern styling."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self, bg=GlassmorphicStyle.BACKGROUND, highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=GlassmorphicStyle.BACKGROUND)

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        self.bind_mousewheel()

    def bind_mousewheel(self):
        """Bind mouse wheel events for scrolling."""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind to all relevant widgets
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # For children widgets
        def bind_to_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_to_mousewheel(child)

        self.after(100, lambda: bind_to_mousewheel(self.scrollable_frame))
