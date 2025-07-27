"""Animation effects for the Weather Dashboard UI.

This module provides smooth animations and visual effects for enhanced
user experience including fade effects, pulse animations, and text effects.
"""

import tkinter as tk
from typing import Optional

from ..styles.glassmorphic import GlassmorphicStyle


class AnimationHelper:
    """Helper class for creating smooth animations and visual effects."""

    @staticmethod
    def fade_in(widget: tk.Widget, duration: int = 500) -> None:
        """Create a fade-in effect for widget.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
        """
        try:
            widget.configure(fg=GlassmorphicStyle.TEXT_SECONDARY)
            steps = 20
            step_time = duration // steps

            def animate_step(step: int) -> None:
                if step <= steps:
                    # Calculate alpha value (simulated with color intensity)
                    alpha = step / steps
                    color_intensity = int(
                        176 + (255 - 176) * alpha
                    )  # From gray to white
                    color = f"#{color_intensity:02x}{color_intensity:02x}{color_intensity:02x}"
                    try:
                        widget.configure(fg=color)
                    except tk.TclError:
                        # Widget doesn't support fg option, skip color animation
                        pass
                    widget.after(step_time, lambda: animate_step(step + 1))
                else:
                    try:
                        widget.configure(fg=GlassmorphicStyle.TEXT_PRIMARY)
                    except tk.TclError:
                        # Widget doesn't support fg option
                        pass

            animate_step(0)
        except tk.TclError:
            # Widget doesn't support fg option, skip animation
            pass

    @staticmethod
    def pulse_effect(
        widget: tk.Widget, color: Optional[str] = None, duration: int = 1000
    ) -> None:
        """Create a pulsing effect on widget.

        Args:
            widget: Widget to animate
            color: Pulse color (defaults to accent color)
            duration: Animation duration in milliseconds
        """
        original_bg = widget.cget("bg")
        pulse_color = color or GlassmorphicStyle.ACCENT

        def pulse_step(increasing: bool = True, step: int = 0) -> None:
            if step < 50:
                # Calculate intermediate color
                ratio = step / 50.0 if increasing else (50 - step) / 50.0
                # Simple color interpolation (in real implementation, would be more sophisticated)
                widget.configure(bg=pulse_color if ratio > 0.5 else original_bg)
                widget.after(duration // 100, lambda: pulse_step(increasing, step + 1))
            elif increasing:
                pulse_step(False, 0)
            else:
                widget.configure(bg=original_bg)
                # Repeat pulse
                widget.after(duration, lambda: pulse_step(True, 0))

        pulse_step()

    @staticmethod
    def text_glow_effect(
        widget: tk.Widget, glow_color: Optional[str] = None, duration: int = 2000
    ) -> None:
        """Create a text glow effect by cycling through related colors.

        Args:
            widget: Widget to animate
            glow_color: Glow color (defaults to accent color)
            duration: Animation duration in milliseconds
        """
        glow_color = glow_color or GlassmorphicStyle.ACCENT
        original_color = widget.cget("fg")

        # Create a list of colors for the glow effect
        glow_colors = [
            original_color,
            glow_color,
            GlassmorphicStyle.TEXT_PRIMARY,
            glow_color,
            original_color,
        ]

        def cycle_colors(color_index: int = 0, step: int = 0) -> None:
            if step >= len(glow_colors):
                step = 0

            widget.configure(fg=glow_colors[step])
            widget.after(
                duration // len(glow_colors),
                lambda: cycle_colors(color_index, (step + 1) % len(glow_colors)),
            )

        cycle_colors()

    @staticmethod
    def rainbow_text_effect(widget: tk.Widget, duration: int = 3000) -> None:
        """Create a subtle rainbow effect on text.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
        """
        colors = [
            GlassmorphicStyle.ACCENT,
            GlassmorphicStyle.ACCENT_SECONDARY,
            GlassmorphicStyle.SUCCESS,
            GlassmorphicStyle.WARNING,
            GlassmorphicStyle.TEXT_PRIMARY,
        ]

        def cycle_rainbow(color_index: int = 0) -> None:
            widget.configure(fg=colors[color_index])
            next_index = (color_index + 1) % len(colors)
            widget.after(duration // len(colors), lambda: cycle_rainbow(next_index))

        cycle_rainbow()

    @staticmethod
    def slide_in(
        widget: tk.Widget,
        direction: str = "left",
        distance: int = 100,
        duration: int = 500,
    ) -> None:
        """Slide widget in from specified direction.

        Args:
            widget: Widget to animate
            direction: Direction to slide from ('left', 'right', 'top', 'bottom')
            distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
        """
        steps = 20
        step_time = duration // steps

        # Get current position
        current_x = widget.winfo_x()
        current_y = widget.winfo_y()

        # Calculate start position based on direction
        if direction == "left":
            start_x, start_y = current_x - distance, current_y
        elif direction == "right":
            start_x, start_y = current_x + distance, current_y
        elif direction == "top":
            start_x, start_y = current_x, current_y - distance
        elif direction == "bottom":
            start_x, start_y = current_x, current_y + distance
        else:
            start_x, start_y = current_x, current_y

        # Set initial position
        widget.place(x=start_x, y=start_y)

        def animate_step(step: int) -> None:
            if step <= steps:
                progress = step / steps
                new_x = start_x + (current_x - start_x) * progress
                new_y = start_y + (current_y - start_y) * progress
                widget.place(x=int(new_x), y=int(new_y))
                widget.after(step_time, lambda: animate_step(step + 1))
            else:
                widget.place(x=current_x, y=current_y)

        animate_step(0)

    @staticmethod
    def scale_effect(
        widget: tk.Widget, scale_factor: float = 1.1, duration: int = 200
    ) -> None:
        """Create a scaling effect on widget (simulated with font size changes).

        Args:
            widget: Widget to animate
            scale_factor: Scale multiplier
            duration: Animation duration in milliseconds
        """
        try:
            original_font = widget.cget("font")
            if isinstance(original_font, tuple) and len(original_font) >= 2:
                family, size = original_font[0], original_font[1]
                scaled_size = int(size * scale_factor)

                # Scale up
                widget.configure(font=(family, scaled_size))

                # Scale back down after duration
                widget.after(duration, lambda: widget.configure(font=original_font))
        except (tk.TclError, IndexError, TypeError):
            # Fallback for widgets that don't support font changes
            pass

    @staticmethod
    def pulse(widget: tk.Widget, duration: int = 1000) -> None:
        """Create a pulse animation on widget (alias for pulse_effect).

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
        """
        AnimationHelper.pulse_effect(widget, duration=duration)

    @staticmethod
    def glow_effect(
        widget: tk.Widget, color: Optional[str] = None, duration: int = 2000
    ) -> None:
        """Create a glow effect on widget (alias for text_glow_effect).

        Args:
            widget: Widget to animate
            color: Glow color (defaults to accent color)
            duration: Animation duration in milliseconds
        """
        AnimationHelper.text_glow_effect(widget, color, duration)

    @staticmethod
    def text_glow(
        widget: tk.Widget, color: Optional[str] = None, duration: int = 2000
    ) -> None:
        """Create a text glow effect on widget (alias for text_glow_effect).

        Args:
            widget: Widget to animate
            color: Glow color (defaults to accent color)
            duration: Animation duration in milliseconds
        """
        AnimationHelper.text_glow_effect(widget, color, duration)
