"""
Layout Management Module for Weather Dashboard.

This module contains classes for managing responsive layouts and modern
layout patterns.
"""

import logging
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk_bs

from .components import BootstrapButton, BootstrapFrame
from .styles.glassmorphic import GlassmorphicFrame
from .styling import GlassmorphicStyle


class ResponsiveLayout:
    """Helper class for responsive layout management."""

    @staticmethod
    def create_card_grid(parent, cards_per_row=2, spacing=10):
        """Create a responsive grid layout for cards."""
        container = BootstrapFrame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=spacing, pady=spacing)
        return container

    @staticmethod
    def create_button_toolbar(parent, buttons_config, spacing=5):
        """Create a modern button toolbar with proper spacing."""
        toolbar = BootstrapFrame(parent)
        toolbar.pack(fill=tk.X, pady=spacing)

        for config in buttons_config:
            btn = BootstrapButton(
                toolbar,
                text=config.get("text", ""),
                icon=config.get("icon", ""),
                style=config.get("style", "primary"),
                command=config.get("command", None),
            )
            btn.pack(side=tk.LEFT, padx=spacing)

            # Add separator if specified
            if config.get("separator", False):
                ttk_bs.Separator(toolbar, orient="vertical").pack(
                    side=tk.LEFT, fill=tk.Y, padx=spacing
                )

        return toolbar

    @staticmethod
    def create_info_card(parent, title, content, icon="ℹ️"):
        """Create a modern information card with Bootstrap styling."""
        card = ttk_bs.LabelFrame(parent, text=f"{icon} {title}", padding=15)
        card.pack(fill=tk.X, pady=10)

        content_label = ttk_bs.Label(
            card, text=content, font=("Segoe UI", 11), wraplength=400
        )
        content_label.pack(anchor=tk.W)

        return card


class ModernLayoutMixin:
    """Mixin to add modern layout capabilities to GUI classes."""

    def create_modern_sidebar(self, parent, width=300):
        """Create a modern sidebar with Bootstrap styling."""
        sidebar = BootstrapFrame(parent)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Add scrolling capability
        canvas = tk.Canvas(sidebar, width=width, highlightthickness=0)
        scrollbar = ttk_bs.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
        scrollable_frame = BootstrapFrame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        return scrollable_frame

    def create_modern_card(self, parent, title, icon="📄"):
        """Create a modern card layout with Bootstrap styling."""
        card = ttk_bs.LabelFrame(parent, text=f"{icon} {title}", padding=20)
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        return card

    def _add_team_data_info(self, parent_frame):
        """Add team data information to the comparison display."""
        try:
            # Check if we have access to team comparison service through callbacks
            callbacks = getattr(self, "callbacks", {})
            if "get_team_data_status" in callbacks:
                team_status = callbacks["get_team_data_status"]()

                # Create team data info frame
                team_info_frame = GlassmorphicFrame(
                    parent_frame,
                    bg_color=GlassmorphicStyle.GLASS_BG_LIGHT,
                    elevated=True,
                )
                team_info_frame.pack(fill=tk.X, padx=20, pady=(10, 20))

                # Team data header
                header_label = tk.Label(
                    team_info_frame,
                    text="📊 Team Data Information",
                    font=(
                        GlassmorphicStyle.FONT_FAMILY,
                        GlassmorphicStyle.FONT_SIZE_MEDIUM,
                        "bold",
                    ),
                    fg=GlassmorphicStyle.ACCENT,
                    bg=team_info_frame.bg_color,
                )
                header_label.pack(pady=(10, 5))

                # Status information
                if team_status.get("data_loaded", False):
                    cities_count = team_status.get("cities_available", 0)
                    status_text = (
                        f"✅ Team data loaded with {cities_count} cities available"
                    )
                    _ = GlassmorphicStyle.SUCCESS  # status_color not used

                    # Show available cities
                    city_list = team_status.get("city_list", [])
                    if city_list:
                        cities_text = f"Available cities: {', '.join(city_list[:5])}"
                        if len(city_list) > 5:
                            cities_text += f" (+{len(city_list) - 5} more)"

                        cities_label = tk.Label(
                            team_info_frame,
                            text=cities_text,
                            font=(
                                GlassmorphicStyle.FONT_FAMILY,
                                GlassmorphicStyle.FONT_SIZE_SMALL,
                            ),
                            fg=GlassmorphicStyle.TEXT_SECONDARY,
                            bg=team_info_frame.bg_color,
                            wraplength=600,
                        )
                        cities_label.pack(pady=(0, 5))

                    # Show data source information
                    data_source = team_status.get("data_source", {})
                    if data_source.get("repository"):
                        repo_text = f"Data source: {data_source.get('repository', 'GitHub Repository')}"
                        repo_label = tk.Label(
                            team_info_frame,
                            text=repo_text,
                            font=(
                                GlassmorphicStyle.FONT_FAMILY,
                                GlassmorphicStyle.FONT_SIZE_SMALL,
                            ),
                            fg=GlassmorphicStyle.TEXT_SECONDARY,
                            bg=team_info_frame.bg_color,
                        )
                        repo_label.pack(pady=(0, 5))

                    # Add refresh button
                    refresh_button = BootstrapButton(
                        team_info_frame,
                        text="🔄 Refresh Team Data",
                        command=self._refresh_team_data,
                        bootstyle="outline-info",
                    )
                    refresh_button.pack(pady=(5, 10))
                else:
                    status_text = "⚠️ Using API fallback - no team data available"
                    _ = GlassmorphicStyle.WARNING  # status_color not used

                status_label = tk.Label(
                    team_info_frame,
                    text=status_text,
                    font=(
                        GlassmorphicStyle.FONT_FAMILY,
                        GlassmorphicStyle.FONT_SIZE_SMALL,
                    ),
                    bg=team_info_frame.bg_color,
                )
                status_label.pack(pady=(0, 10))

        except Exception as e:
            # Silently handle errors - team data info is optional
            logging.debug(f"Could not display team data info: {e}")
            pass

    def _refresh_team_data(self):
        """Refresh team data from GitHub repository."""
        try:
            callbacks = getattr(self, "callbacks", {})
            if "refresh_team_data" in callbacks:
                callbacks["refresh_team_data"]()
            else:
                messagebox.showerror("Error", "Refresh functionality not available")
        except Exception as e:
            logging.error(f"Error refreshing team data: {e}")
            messagebox.showerror("Error", f"Error refreshing team data: {str(e)}")
