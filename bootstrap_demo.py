#!/usr/bin/env python3
"""
Bootstrap Styling Demo for Weather Dashboard
Shows the improved GUI with ttkbootstrap styling
"""

import tkinter as tk
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import PRIMARY, SECONDARY, SUCCESS, INFO, WARNING, DANGER

def create_demo_window():
    """Create a demo window showing the Bootstrap styling improvements."""
    
    # Initialize ttkbootstrap with a modern dark theme
    style = ttk_bs.Style(theme="superhero")
    root = style.master
    
    root.title("Weather Dashboard - Bootstrap Styling Demo")
    root.geometry("800x600")
    
    # Main container
    main_frame = ttk_bs.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk_bs.Label(
        main_frame,
        text="🌤️ Weather Dashboard - Bootstrap Styled UI",
        font=("Segoe UI", 18, "bold")
    )
    title_label.pack(pady=(0, 20))
    
    # Button showcase section
    button_frame = ttk_bs.LabelFrame(main_frame, text="Button Styles", padding=15)
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Row 1 - Primary buttons
    row1 = ttk_bs.Frame(button_frame)
    row1.pack(fill=tk.X, pady=5)
    
    ttk_bs.Button(row1, text="🔍 Search").pack(side=tk.LEFT, padx=5)
    ttk_bs.Button(row1, text="🔄 Refresh").pack(side=tk.LEFT, padx=5)
    ttk_bs.Button(row1, text="⏱️ Auto").pack(side=tk.LEFT, padx=5)
    ttk_bs.Button(row1, text="📊 Charts").pack(side=tk.LEFT, padx=5)
    
    # Row 2 - Secondary buttons  
    row2 = ttk_bs.Frame(button_frame)
    row2.pack(fill=tk.X, pady=5)
    
    ttk_bs.Button(row2, text="⭐ Add Favorite").pack(side=tk.LEFT, padx=5)
    ttk_bs.Button(row2, text="📍 Current Location").pack(side=tk.LEFT, padx=5)
    ttk_bs.Button(row2, text="🎲 Random City").pack(side=tk.LEFT, padx=5)
    
    # Entry showcase
    entry_frame = ttk_bs.LabelFrame(main_frame, text="Input Fields", padding=15)
    entry_frame.pack(fill=tk.X, pady=(0, 20))
    
    ttk_bs.Label(entry_frame, text="City Search:").pack(anchor=tk.W)
    city_entry = ttk_bs.Entry(entry_frame, font=("Segoe UI", 12))
    city_entry.pack(fill=tk.X, pady=5)
    city_entry.insert(0, "Enter city name...")
    
    # Progress and other widgets
    widget_frame = ttk_bs.LabelFrame(main_frame, text="Additional Widgets", padding=15)
    widget_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Progress bar
    ttk_bs.Label(widget_frame, text="Loading Weather Data:").pack(anchor=tk.W)
    progress = ttk_bs.Progressbar(widget_frame, length=400)
    progress.pack(fill=tk.X, pady=5)
    progress['value'] = 70
    
    # Scale/slider
    ttk_bs.Label(widget_frame, text="Temperature Range:").pack(anchor=tk.W, pady=(10, 0))
    scale = ttk_bs.Scale(widget_frame, from_=0, to=100, orient=tk.HORIZONTAL)
    scale.pack(fill=tk.X, pady=5)
    scale.set(23)
    
    # Notebook/tabs demo
    notebook_frame = ttk_bs.LabelFrame(main_frame, text="Tabbed Interface", padding=15)
    notebook_frame.pack(fill=tk.BOTH, expand=True)
    
    notebook = ttk_bs.Notebook(notebook_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Weather tab
    tab1 = ttk_bs.Frame(notebook)
    notebook.add(tab1, text="🌤️ Current Weather")
    ttk_bs.Label(tab1, text="Current weather information would go here...", 
                font=("Segoe UI", 12)).pack(pady=20)
    
    # Forecast tab
    tab2 = ttk_bs.Frame(notebook)
    notebook.add(tab2, text="📅 Forecast")
    ttk_bs.Label(tab2, text="Weather forecast data would be displayed here...", 
                font=("Segoe UI", 12)).pack(pady=20)
    
    # Journal tab
    tab3 = ttk_bs.Frame(notebook)
    notebook.add(tab3, text="📝 Journal")
    ttk_bs.Label(tab3, text="Weather journal entries would be shown here...", 
                font=("Segoe UI", 12)).pack(pady=20)
    
    return root

if __name__ == "__main__":
    demo_root = create_demo_window()
    demo_root.mainloop()
