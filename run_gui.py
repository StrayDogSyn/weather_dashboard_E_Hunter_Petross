#!/usr/bin/env python3
"""
Weather Dashboard - TKinter GUI Launcher
Simple launcher that works with any Python installation
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def main():
    """Launch the Weather Dashboard GUI."""
    
    print("🌤️ Weather Dashboard TKinter GUI")
    print("=" * 40)
    print("✅ Python:", sys.version.split()[0])
    
    try:
        # Test TKinter
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("✅ TKinter: Available")
        
        # Launch the GUI
        launch_gui()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            messagebox.showerror("Error", f"Failed to start GUI: {e}")
        except:
            pass

def launch_gui():
    """Launch the main GUI application."""
    
    class WeatherDashboardGUI:
        def __init__(self):
            self.root = tk.Tk()
            self.setup_window()
            self.create_interface()
        
        def setup_window(self):
            """Setup the main window."""
            self.root.title("🌤️ Weather Dashboard")
            self.root.geometry("1200x800")
            self.root.configure(bg="#0f0f0f")
            
            # Center the window
            self.root.update_idletasks()
            width = 1200
            height = 800
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        def create_interface(self):
            """Create the main interface."""
            
            # Main container (glassmorphic style)
            main_frame = tk.Frame(
                self.root, 
                bg="#1a1a1a", 
                relief="flat", 
                bd=1,
                highlightbackground="#333333",
                highlightthickness=1
            )
            main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Header section
            self.create_header(main_frame)
            
            # Content area with tabs
            self.create_content_area(main_frame)
            
            # Status bar
            self.create_status_bar(main_frame)
        
        def create_header(self, parent):
            """Create the header section."""
            header_frame = tk.Frame(parent, bg="#1a1a1a")
            header_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Title
            title_label = tk.Label(
                header_frame,
                text="🌤️ Weather Dashboard",
                font=("Segoe UI", 28, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            )
            title_label.pack()
            
            # Subtitle
            subtitle_label = tk.Label(
                header_frame,
                text="Modern TKinter GUI with Glassmorphic Design & Capstone Features",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a"
            )
            subtitle_label.pack(pady=(5, 20))
        
        def create_content_area(self, parent):
            """Create the main content area with tabs."""
            from tkinter import ttk
            
            # Notebook for tabs
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure dark theme for notebook
            style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
            style.configure('TNotebook.Tab', 
                           background='#2a2a2a',
                           foreground='#b0b0b0', 
                           padding=[20, 10],
                           borderwidth=0)
            style.map('TNotebook.Tab',
                     background=[('selected', '#4a9eff')],
                     foreground=[('selected', '#ffffff')])
            
            notebook = ttk.Notebook(parent)
            notebook.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Create tabs for capstone features
            self.create_weather_tab(notebook)
            self.create_comparison_tab(notebook)
            self.create_journal_tab(notebook)
            self.create_activities_tab(notebook)
            self.create_poetry_tab(notebook)
            self.create_favorites_tab(notebook)
        
        def create_weather_tab(self, notebook):
            """Create the main weather tab."""
            frame = tk.Frame(notebook, bg="#0f0f0f")
            notebook.add(frame, text="🌤️ Current Weather")
            
            # Weather card
            card = tk.Frame(frame, bg="#1a1a1a", relief="flat", bd=1)
            card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                card,
                text="🌡️ Weather Display",
                font=("Segoe UI", 18, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            ).pack(pady=(30, 10))
            
            tk.Label(
                card,
                text="Enter a city name and get real-time weather data\nwith detailed metrics and forecasts",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.CENTER
            ).pack(pady=10)
            
            # Sample weather display
            sample_frame = tk.Frame(card, bg="#2a2a2a", relief="flat", bd=1)
            sample_frame.pack(pady=20, padx=40, fill=tk.X)
            
            tk.Label(sample_frame, text="New York, NY", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#2a2a2a").pack(pady=(15, 5))
            tk.Label(sample_frame, text="22°C", font=("Segoe UI", 24, "bold"), fg="#4a9eff", bg="#2a2a2a").pack()
            tk.Label(sample_frame, text="Partly Cloudy", font=("Segoe UI", 12), fg="#b0b0b0", bg="#2a2a2a").pack(pady=(0, 15))
        
        def create_comparison_tab(self, notebook):
            """Create the city comparison tab."""
            frame = tk.Frame(notebook, bg="#0f0f0f")
            notebook.add(frame, text="🌍 Compare Cities")
            
            content = tk.Frame(frame, bg="#1a1a1a", relief="flat", bd=1)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                content,
                text="🌍 City Weather Comparison",
                font=("Segoe UI", 18, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            ).pack(pady=(30, 20))
            
            tk.Label(
                content,
                text="Compare weather conditions between two cities\nSide-by-side analysis with detailed metrics",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.CENTER
            ).pack(pady=20)
        
        def create_journal_tab(self, notebook):
            """Create the weather journal tab."""
            frame = tk.Frame(notebook, bg="#0f0f0f")
            notebook.add(frame, text="📔 Journal")
            
            content = tk.Frame(frame, bg="#1a1a1a", relief="flat", bd=1)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                content,
                text="📔 Weather Journal",
                font=("Segoe UI", 18, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            ).pack(pady=(30, 20))
            
            tk.Label(
                content,
                text="Track daily weather observations with mood and activity logging\nCreate personal weather memories and insights",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.CENTER
            ).pack(pady=20)
        
        def create_activities_tab(self, notebook):
            """Create the activities tab."""
            frame = tk.Frame(notebook, bg="#0f0f0f")
            notebook.add(frame, text="🎯 Activities")
            
            content = tk.Frame(frame, bg="#1a1a1a", relief="flat", bd=1)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                content,
                text="🎯 Activity Suggestions",
                font=("Segoe UI", 18, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            ).pack(pady=(30, 20))
            
            tk.Label(
                content,
                text="Get personalized activity recommendations based on current weather\nIndoor and outdoor suggestions with suitability scores",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.CENTER
            ).pack(pady=20)
        
        def create_poetry_tab(self, notebook):
            """Create the poetry tab."""
            frame = tk.Frame(notebook, bg="#0f0f0f")
            notebook.add(frame, text="🎨 Poetry")
            
            content = tk.Frame(frame, bg="#1a1a1a", relief="flat", bd=1)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                content,
                text="🎨 Weather Poetry",
                font=("Segoe UI", 18, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            ).pack(pady=(30, 20))
            
            tk.Label(
                content,
                text="AI-generated poems inspired by current weather conditions\nHaikus, phrases, and limericks celebrating the atmosphere",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.CENTER
            ).pack(pady=20)
        
        def create_favorites_tab(self, notebook):
            """Create the favorites tab."""
            frame = tk.Frame(notebook, bg="#0f0f0f")
            notebook.add(frame, text="⭐ Favorites")
            
            content = tk.Frame(frame, bg="#1a1a1a", relief="flat", bd=1)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                content,
                text="⭐ Favorite Cities",
                font=("Segoe UI", 18, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            ).pack(pady=(30, 20))
            
            tk.Label(
                content,
                text="Save and manage your preferred locations\nQuick access to weather for cities you care about",
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.CENTER
            ).pack(pady=20)
        
        def create_status_bar(self, parent):
            """Create the status bar."""
            status_frame = tk.Frame(parent, bg="#333333", relief="flat", bd=1)
            status_frame.pack(fill=tk.X, pady=(10, 0))
            
            tk.Label(
                status_frame,
                text="✅ TKinter GUI Framework Active | Capstone Features Ready | Need API Key for Full Functionality",
                font=("Segoe UI", 10),
                fg="#4ade80",
                bg="#333333"
            ).pack(pady=8)
        
        def run(self):
            """Start the GUI event loop."""
            print("🚀 Launching TKinter GUI...")
            self.root.mainloop()
    
    # Create and run the application
    app = WeatherDashboardGUI()
    app.run()

if __name__ == "__main__":
    main()
