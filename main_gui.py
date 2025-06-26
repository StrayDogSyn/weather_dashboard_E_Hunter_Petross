#!/usr/bin/env python3
"""
Weather Dashboard - Modern TKinter GUI Application

A comprehensive weather dashboard with glassmorphic design elements,
featuring current weather, forecasts, city comparison, weather journal,
activity suggestions, and weather poetry.
"""

if __name__ == "__main__":
    import sys
    import os
    from pathlib import Path
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Test simple import first
        import tkinter as tk
        
        print("🌤️ Weather Dashboard - Starting GUI...")
        print("✅ TKinter available")
        
        # Try to import our modules
        try:
            from config import config_manager
            print("✅ Config module loaded")
            
            from ui.gui_interface import WeatherDashboardGUI
            print("✅ GUI interface loaded")
            
            from app_gui import WeatherDashboardGUIApp
            print("✅ App controller loaded")
            
            # Start the application
            app = WeatherDashboardGUIApp()
            app.run()
            
        except ImportError as e:
            print(f"⚠️ Import issue with full app: {e}")
            print("🔄 Falling back to simple GUI...")
            
            # Simple fallback GUI
            root = tk.Tk()
            root.title("🌤️ Weather Dashboard")
            root.geometry("800x600")
            root.configure(bg="#0f0f0f")
            
            # Center window
            root.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (800 // 2)
            y = (root.winfo_screenheight() // 2) - (600 // 2)
            root.geometry(f"800x600+{x}+{y}")
            
            # Main frame
            main_frame = tk.Frame(root, bg="#1a1a1a", relief="flat", bd=1)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title_label = tk.Label(
                main_frame,
                text="🌤️ Weather Dashboard",
                font=("Segoe UI", 24, "bold"),
                fg="#ffffff",
                bg="#1a1a1a"
            )
            title_label.pack(pady=(30, 20))
            
            # Status message
            status_text = """🚀 GUI Framework Successfully Launched!

✅ TKinter Interface: Working
🔧 Backend Integration: In Progress
⚙️ Configuration: Needs Setup

To complete the setup:

1. Set up your API key:
   • Get a free key from openweathermap.org
   • Copy .env.example to .env
   • Set OPENWEATHER_API_KEY=your_key

2. Install dependencies:
   • pip install -r requirements.txt

3. Test the full application:
   • python main.py

This demonstrates the glassmorphic TKinter GUI is ready!"""

            status_label = tk.Label(
                main_frame,
                text=status_text,
                font=("Segoe UI", 12),
                fg="#b0b0b0",
                bg="#1a1a1a",
                justify=tk.LEFT
            )
            status_label.pack(pady=20, padx=30)
            
            # Start GUI
            root.mainloop()
            
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        
        # Emergency fallback
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror(
                "Weather Dashboard Error", 
                f"Failed to start Weather Dashboard:\n\n{e}\n\nPlease check:\n• Python dependencies\n• Configuration files\n• API keys"
            )
        except:
            print("Could not show error dialog")
