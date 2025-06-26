#!/usr/bin/env python3
"""
Simple TKinter GUI Weather Dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class SimpleWeatherDashboard:
    """Simple Weather Dashboard GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_layout()
    
    def setup_window(self):
        """Setup main window."""
        self.root.title("🌤️ Weather Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f0f0f")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def create_layout(self):
        """Create the main layout."""
        # Header
        header_frame = tk.Frame(self.root, bg="#1a1a1a", relief="flat", bd=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            header_frame,
            text="🌤️ Weather Dashboard",
            font=("Segoe UI", 24, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#0f0f0f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Welcome message
        welcome_frame = tk.Frame(main_frame, bg="#1a1a1a", relief="flat", bd=1)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        welcome_label = tk.Label(
            welcome_frame,
            text="🌟 Welcome to Weather Dashboard!\\n\\nThis is a modern TKinter GUI with glassmorphic design.\\n\\nTo complete the integration, we need to:\\n• Install required dependencies\\n• Set up API configuration\\n• Connect backend services\\n\\nFor now, this demonstrates the GUI framework is working!",
            font=("Segoe UI", 14),
            fg="#b0b0b0",
            bg="#1a1a1a",
            justify=tk.CENTER
        )
        welcome_label.pack(expand=True, pady=50)
        
        # Sample button
        button_frame = tk.Frame(welcome_frame, bg="#1a1a1a")
        button_frame.pack(pady=20)
        
        sample_btn = tk.Button(
            button_frame,
            text="🚀 Launch Full App (Coming Soon)",
            font=("Segoe UI", 12),
            bg="#4a9eff",
            fg="#ffffff",
            relief="flat",
            padx=30,
            pady=15,
            cursor="hand2",
            command=self.show_info
        )
        sample_btn.pack()
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#1a1a1a", relief="flat", bd=1)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        status_label = tk.Label(
            status_frame,
            text="✅ GUI Framework Ready - Backend Integration In Progress",
            font=("Segoe UI", 10),
            fg="#4ade80",
            bg="#1a1a1a"
        )
        status_label.pack(side=tk.LEFT, padx=15, pady=8)
    
    def show_info(self):
        """Show info dialog."""
        messagebox.showinfo(
            "Weather Dashboard", 
            "🌤️ Weather Dashboard GUI Framework\\n\\n✅ TKinter GUI: Working\\n🔄 Backend Services: In Progress\\n🔧 API Integration: Pending\\n\\nNext steps:\\n• Fix import dependencies\\n• Configure API keys\\n• Test all features"
        )
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()

def main():
    """Main entry point."""
    print("🌤️ Starting Simple Weather Dashboard GUI...")
    
    try:
        app = SimpleWeatherDashboard()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        messagebox.showerror("Error", f"Failed to start GUI: {e}")

if __name__ == "__main__":
    main()
