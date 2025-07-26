"""Responsive layout management and improved spacing system.

This module provides enhanced layout management with standardized spacing,
responsive design patterns, and improved button placement for the weather dashboard.
"""

import tkinter as tk
from typing import Callable, Dict, Optional, Tuple

from ..styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from ..widgets.modern_button import ModernButton


class ResponsiveSpacing:
    """Standardized spacing system for consistent layouts."""

    # Base spacing units (multiples of 4 for consistency)
    UNIT = 4

    # Spacing scale
    TINY = UNIT * 1  # 4px
    SMALL = UNIT * 2  # 8px
    MEDIUM = UNIT * 3  # 12px
    LARGE = UNIT * 4  # 16px
    XLARGE = UNIT * 5  # 20px
    XXLARGE = UNIT * 6  # 24px
    XXXLARGE = UNIT * 8  # 32px

    # Component-specific spacing
    BUTTON_PADDING_X = LARGE
    BUTTON_PADDING_Y = MEDIUM
    BUTTON_SPACING = MEDIUM
    BUTTON_GROUP_SPACING = XLARGE

    CONTAINER_PADDING = LARGE
    SECTION_SPACING = XLARGE
    ELEMENT_SPACING = MEDIUM

    # Responsive breakpoints
    COMPACT_PADDING = SMALL
    NORMAL_PADDING = MEDIUM
    SPACIOUS_PADDING = LARGE


class ResponsiveLayoutManager:
    """Manages responsive layout based on window size."""

    def __init__(self, root_window: tk.Tk):
        """Initialize responsive layout manager.

        Args:
            root_window: Main application window
        """
        self.root = root_window
        self.current_layout = "desktop"
        self.layout_callbacks: Dict[str, Callable] = {}

        # Responsive breakpoints
        self.breakpoints = {"mobile": 600, "tablet": 900, "desktop": 1200}

        # Bind resize event
        self.root.bind("<Configure>", self._on_window_resize)

        # Initial layout determination
        self.root.after(100, self._initial_layout_check)

    def register_layout_callback(self, layout_type: str, callback: Callable) -> None:
        """Register callback for specific layout type.

        Args:
            layout_type: Layout type ('mobile', 'tablet', 'desktop')
            callback: Function to call when switching to this layout
        """
        self.layout_callbacks[layout_type] = callback

    def _initial_layout_check(self) -> None:
        """Perform initial layout check after window is fully initialized."""
        width = self.root.winfo_width()
        if width > 1:  # Ensure window is properly initialized
            layout_type = self._determine_layout(width)
            self._apply_layout(layout_type)

    def _on_window_resize(self, event: tk.Event) -> None:
        """Handle window resize events.

        Args:
            event: Tkinter event object
        """
        if event.widget == self.root:
            width = event.width
            new_layout = self._determine_layout(width)

            if new_layout != self.current_layout:
                self.current_layout = new_layout
                self._apply_layout(new_layout)

    def _determine_layout(self, width: int) -> str:
        """Determine layout type based on width.

        Args:
            width: Window width in pixels

        Returns:
            Layout type string
        """
        if width < self.breakpoints["mobile"]:
            return "mobile"
        elif width < self.breakpoints["tablet"]:
            return "tablet"
        else:
            return "desktop"

    def _apply_layout(self, layout_type: str) -> None:
        """Apply layout-specific configurations.

        Args:
            layout_type: Type of layout to apply
        """
        if layout_type in self.layout_callbacks:
            self.layout_callbacks[layout_type]()

    def get_current_layout(self) -> str:
        """Get current layout type.

        Returns:
            Current layout type
        """
        return self.current_layout

    def get_spacing_for_layout(
        self, layout_type: Optional[str] = None
    ) -> Dict[str, int]:
        """Get spacing values appropriate for layout type.

        Args:
            layout_type: Layout type, uses current if None

        Returns:
            Dictionary of spacing values
        """
        layout = layout_type or self.current_layout

        if layout == "mobile":
            return {
                "container_padding": ResponsiveSpacing.COMPACT_PADDING,
                "button_spacing": ResponsiveSpacing.SMALL,
                "section_spacing": ResponsiveSpacing.MEDIUM,
                "element_spacing": ResponsiveSpacing.SMALL,
            }
        elif layout == "tablet":
            return {
                "container_padding": ResponsiveSpacing.NORMAL_PADDING,
                "button_spacing": ResponsiveSpacing.MEDIUM,
                "section_spacing": ResponsiveSpacing.LARGE,
                "element_spacing": ResponsiveSpacing.MEDIUM,
            }
        else:  # desktop
            return {
                "container_padding": ResponsiveSpacing.SPACIOUS_PADDING,
                "button_spacing": ResponsiveSpacing.LARGE,
                "section_spacing": ResponsiveSpacing.XLARGE,
                "element_spacing": ResponsiveSpacing.LARGE,
            }


class ImprovedButtonGroup(tk.Frame):
    """Enhanced button group with proper spacing and visual hierarchy."""

    def __init__(
        self, parent, layout_manager: Optional[ResponsiveLayoutManager] = None, **kwargs
    ):
        """Initialize improved button group.

        Args:
            parent: Parent widget
            layout_manager: Optional responsive layout manager
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        self.layout_manager = layout_manager
        self.style = GlassmorphicStyle()
        self.buttons: Dict[str, ModernButton] = {}
        self.button_groups: Dict[str, tk.Frame] = {}

        # Configure frame styling
        self.configure(bg=self.style.colors["surface"])

    def create_button_group(self, group_name: str, buttons_config: list) -> tk.Frame:
        """Create a group of buttons with proper spacing.

        Args:
            group_name: Name of the button group
            buttons_config: List of button configuration dictionaries

        Returns:
            Frame containing the button group
        """
        # Get current spacing values
        spacing = self._get_current_spacing()

        # Create group frame
        group_frame = tk.Frame(self, bg=self.style.colors["surface"])
        group_frame.pack(
            side=tk.LEFT,
            padx=spacing["button_spacing"],
            pady=spacing["element_spacing"],
        )

        self.button_groups[group_name] = group_frame

        # Create buttons in group
        for i, btn_config in enumerate(buttons_config):
            button = ModernButton(
                group_frame,
                text=btn_config.get("text", ""),
                command=btn_config.get("command"),
                style_variant=btn_config.get("style", "primary"),
            )

            # Apply responsive spacing
            button.pack(
                side=tk.LEFT,
                padx=(0 if i == 0 else spacing["button_spacing"], 0),
                pady=0,
            )

            # Store button reference
            button_id = btn_config.get("id", f"{group_name}_{i}")
            self.buttons[button_id] = button

        return group_frame

    def add_separator(self, width: int = 2) -> None:
        """Add visual separator between button groups.

        Args:
            width: Width of separator in pixels
        """
        spacing = self._get_current_spacing()

        separator = tk.Frame(self, width=width, bg=self.style.colors["border"])
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=spacing["section_spacing"])

    def _get_current_spacing(self) -> Dict[str, int]:
        """Get current spacing values based on layout.

        Returns:
            Dictionary of spacing values
        """
        if self.layout_manager:
            return self.layout_manager.get_spacing_for_layout()
        else:
            # Default spacing
            return {
                "container_padding": ResponsiveSpacing.CONTAINER_PADDING,
                "button_spacing": ResponsiveSpacing.BUTTON_SPACING,
                "section_spacing": ResponsiveSpacing.SECTION_SPACING,
                "element_spacing": ResponsiveSpacing.ELEMENT_SPACING,
            }

    def update_layout(self) -> None:
        """Update button group layout based on current responsive settings."""
        spacing = self._get_current_spacing()

        # Update group spacing
        for group_frame in self.button_groups.values():
            group_frame.pack_configure(
                padx=spacing["button_spacing"], pady=spacing["element_spacing"]
            )

        # Update individual button spacing within groups
        for group_name, group_frame in self.button_groups.items():
            buttons = [
                child
                for child in group_frame.winfo_children()
                if isinstance(child, ModernButton)
            ]

            for i, button in enumerate(buttons):
                button.pack_configure(
                    padx=(0 if i == 0 else spacing["button_spacing"], 0)
                )


class ResponsiveMainLayout(GlassmorphicFrame):
    """Enhanced main layout with responsive design patterns."""

    def __init__(self, parent, layout_manager: ResponsiveLayoutManager, **kwargs):
        """Initialize responsive main layout.

        Args:
            parent: Parent widget
            layout_manager: Responsive layout manager
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, elevated=True, **kwargs)
        self.layout_manager = layout_manager
        self.style = GlassmorphicStyle()

        # Register layout callbacks
        self.layout_manager.register_layout_callback(
            "mobile", self._apply_mobile_layout
        )
        self.layout_manager.register_layout_callback(
            "tablet", self._apply_tablet_layout
        )
        self.layout_manager.register_layout_callback(
            "desktop", self._apply_desktop_layout
        )

        # Initialize layout
        self._setup_responsive_grid()

    def _setup_responsive_grid(self) -> None:
        """Set up responsive grid configuration."""
        # Configure grid weights for responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=250)  # Sidebar minimum
        self.grid_columnconfigure(1, weight=3)  # Main content gets more space

    def _apply_mobile_layout(self) -> None:
        """Apply mobile-specific layout adjustments."""
        # Stack components vertically on mobile
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Adjust padding for mobile
        spacing = self.layout_manager.get_spacing_for_layout("mobile")
        self._update_component_spacing(spacing)

    def _apply_tablet_layout(self) -> None:
        """Apply tablet-specific layout adjustments."""
        # Balanced layout for tablet
        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=2)

        # Adjust padding for tablet
        spacing = self.layout_manager.get_spacing_for_layout("tablet")
        self._update_component_spacing(spacing)

    def _apply_desktop_layout(self) -> None:
        """Apply desktop-specific layout adjustments."""
        # Optimal desktop layout
        self.grid_columnconfigure(0, weight=1, minsize=300)
        self.grid_columnconfigure(1, weight=3)

        # Adjust padding for desktop
        spacing = self.layout_manager.get_spacing_for_layout("desktop")
        self._update_component_spacing(spacing)

    def _update_component_spacing(self, spacing: Dict[str, int]) -> None:
        """Update spacing for all child components.

        Args:
            spacing: Dictionary of spacing values
        """
        # Update padding for all child widgets
        for child in self.winfo_children():
            if hasattr(child, "pack_info") and child.pack_info():
                child.pack_configure(
                    padx=spacing["container_padding"], pady=spacing["element_spacing"]
                )
            elif hasattr(child, "grid_info") and child.grid_info():
                child.grid_configure(
                    padx=spacing["container_padding"], pady=spacing["element_spacing"]
                )


def create_improved_dashboard_controls(
    parent,
    chart_callbacks: Dict[str, Callable],
    layout_manager: Optional[ResponsiveLayoutManager] = None,
) -> ImprovedButtonGroup:
    """Create improved dashboard controls with better spacing and organization.

    Args:
        parent: Parent widget
        chart_callbacks: Dictionary mapping chart IDs to callback functions
        layout_manager: Optional responsive layout manager

    Returns:
        ImprovedButtonGroup instance
    """
    # Create main controls container
    controls_frame = GlassmorphicFrame(parent, elevated=True)
    controls_frame.pack(fill=tk.X, pady=(0, ResponsiveSpacing.LARGE))

    # Create button group
    button_group = ImprovedButtonGroup(controls_frame, layout_manager)
    button_group.pack(pady=ResponsiveSpacing.LARGE)

    # Primary chart buttons
    chart_buttons_config = [
        {
            "id": "temperature",
            "text": "📈 Temperature Trend\n(Ctrl+1)",
            "command": lambda: chart_callbacks.get("temperature", lambda: None)(),
            "style": "primary",
        },
        {
            "id": "metrics",
            "text": "📊 Weather Metrics\n(Ctrl+2)",
            "command": lambda: chart_callbacks.get("metrics", lambda: None)(),
            "style": "primary",
        },
        {
            "id": "forecast",
            "text": "🌤️ 5-Day Forecast\n(Ctrl+3)",
            "command": lambda: chart_callbacks.get("forecast", lambda: None)(),
            "style": "primary",
        },
        {
            "id": "humidity_pressure",
            "text": "💧 Humidity & Pressure\n(Ctrl+4)",
            "command": lambda: chart_callbacks.get("humidity_pressure", lambda: None)(),
            "style": "primary",
        },
    ]

    # Create primary button group
    button_group.create_button_group("charts", chart_buttons_config)

    # Add separator
    button_group.add_separator()

    # Secondary action buttons
    action_buttons_config = [
        {
            "id": "refresh",
            "text": "🔄 Refresh All\n(Ctrl+R)",
            "command": chart_callbacks.get("refresh_all", lambda: None),
            "style": "secondary",
        },
        {
            "id": "help",
            "text": "❓ Help\n(Ctrl+H)",
            "command": chart_callbacks.get("show_help", lambda: None),
            "style": "accent",
        },
    ]

    # Create secondary button group
    button_group.create_button_group("actions", action_buttons_config)

    return button_group
