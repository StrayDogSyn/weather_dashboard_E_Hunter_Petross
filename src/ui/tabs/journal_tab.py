"""Weather Journal Tab with Rich Text Editor."""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import customtkinter as ctk

from ...services.database.database_service import DatabaseService
from ..components.glassmorphic import GlassmorphicFrame
from ..components.glassmorphic.glass_button import GlassButton
from ...utils.error_wrapper import ensure_main_thread


class WeatherJournalTab(ctk.CTkFrame):
    """Weather Journal Tab with rich text editing capabilities."""
    
    def __init__(self, parent, weather_service):
        """Initialize the weather journal tab."""
        super().__init__(parent)
        self.weather_service = weather_service
        self.db_service = DatabaseService()
        self.entries = []
        self.current_entry_id = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()
        self.load_entries()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container with glassmorphic styling
        try:
            self.container = GlassmorphicFrame(self)
        except:
            # Fallback to regular frame if GlassmorphicFrame not available
            self.container = ctk.CTkFrame(self, fg_color="transparent")
        
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)
        
        # Create sections
        self.create_entry_section()
        self.create_search_section()
        self.create_entries_list()
    
    def create_entry_section(self):
        """Create rich text entry section with weather auto-population."""
        entry_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        entry_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            entry_frame, 
            text="📝 Weather Journal", 
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        # Entry title input
        self.title_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Entry Title...",
            height=40,
            font=("Arial", 16)
        )
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Rich text editor frame
        text_frame = ctk.CTkFrame(entry_frame)
        text_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Rich text editor
        self.text_editor = scrolledtext.ScrolledText(
            text_frame,
            height=10,
            wrap=tk.WORD,
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="white",
            insertbackground="white",
            selectbackground="#404040",
            relief="flat",
            borderwidth=0
        )
        self.text_editor.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Mood selector and weather info frame
        info_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        info_frame.grid(row=3, column=0, sticky="ew", pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Mood selector
        mood_label = ctk.CTkLabel(info_frame, text="Mood:", font=("Arial", 12))
        mood_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.mood_var = tk.StringVar(value="neutral")
        moods = ["😊 Happy", "😐 Neutral", "😢 Sad", "😎 Excited", "😴 Tired"]
        
        mood_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        mood_frame.grid(row=0, column=1, sticky="w")
        
        for i, mood in enumerate(moods):
            btn = ctk.CTkRadioButton(
                mood_frame,
                text=mood,
                variable=self.mood_var,
                value=mood.split()[1].lower()
            )
            btn.grid(row=0, column=i, padx=5, sticky="w")
        
        # Weather info display
        self.weather_info_label = ctk.CTkLabel(
            info_frame, 
            text="Weather: Loading...", 
            font=("Arial", 10),
            text_color="gray"
        )
        self.weather_info_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Update weather info
        self.update_weather_info()
        
        # Buttons frame
        button_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        # Save button
        try:
            save_btn = GlassButton(
                button_frame,
                text="💾 Save Entry",
                command=self.save_entry
            )
        except:
            # Fallback to regular button
            save_btn = ctk.CTkButton(
                button_frame,
                text="💾 Save Entry",
                command=self.save_entry,
                height=35
            )
        save_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Clear button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_entry_form,
            height=35,
            fg_color="#8B0000",
            hover_color="#A52A2A"
        )
        clear_btn.grid(row=0, column=1, padx=10)
        
        # Auto-populate weather button
        weather_btn = ctk.CTkButton(
            button_frame,
            text="🌤️ Add Weather",
            command=self.add_weather_to_entry,
            height=35,
            fg_color="#4A90E2",
            hover_color="#357ABD"
        )
        weather_btn.grid(row=0, column=2, padx=10)
    
    def create_search_section(self):
        """Create search and filter section."""
        search_frame = ctk.CTkFrame(self.container)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        search_label = ctk.CTkLabel(search_frame, text="🔍 Search:", font=("Arial", 12))
        search_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search entries by title, content, or mood...",
            height=35
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.filter_entries)
        
        # Filter by mood
        mood_filter_label = ctk.CTkLabel(search_frame, text="Filter:", font=("Arial", 12))
        mood_filter_label.grid(row=0, column=2, padx=(20, 5), pady=10, sticky="w")
        
        self.mood_filter = ctk.CTkComboBox(
            search_frame,
            values=["All", "happy", "neutral", "sad", "excited", "tired"],
            command=self.filter_entries,
            width=120
        )
        self.mood_filter.set("All")
        self.mood_filter.grid(row=0, column=3, padx=5, pady=10)
    
    def create_entries_list(self):
        """Create entries list section."""
        # List frame
        list_frame = ctk.CTkFrame(self.container)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # List title
        list_title = ctk.CTkLabel(
            list_frame, 
            text="📚 Journal Entries", 
            font=("Arial", 16, "bold")
        )
        list_title.grid(row=0, column=0, pady=10, sticky="w", padx=10)
        
        # Scrollable entries list
        self.entries_scrollable = ctk.CTkScrollableFrame(list_frame)
        self.entries_scrollable.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.entries_scrollable.grid_columnconfigure(0, weight=1)
    
    @ensure_main_thread
    def update_weather_info(self):
        """Update weather information display."""
        try:
            if self.weather_service:
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    weather_text = f"Weather: {weather_data.get('temperature', 'N/A')}°C, {weather_data.get('condition', 'N/A')} in {weather_data.get('location', 'Unknown')}"
                    self.weather_info_label.configure(text=weather_text)
                else:
                    self.weather_info_label.configure(text="Weather: Unable to fetch current weather")
            else:
                self.weather_info_label.configure(text="Weather: Service not available")
        except Exception as e:
            self.weather_info_label.configure(text=f"Weather: Error - {str(e)}")
    
    def add_weather_to_entry(self):
        """Add current weather information to the text entry."""
        try:
            if self.weather_service:
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    weather_text = f"\n\n🌤️ Weather Update ({datetime.now().strftime('%Y-%m-%d %H:%M')}):\n"
                    weather_text += f"Temperature: {weather_data.get('temperature', 'N/A')}°C\n"
                    weather_text += f"Condition: {weather_data.get('condition', 'N/A')}\n"
                    weather_text += f"Location: {weather_data.get('location', 'Unknown')}\n"
                    weather_text += f"Humidity: {weather_data.get('humidity', 'N/A')}%\n"
                    weather_text += f"Wind: {weather_data.get('wind_speed', 'N/A')} km/h\n"
                    
                    # Insert at current cursor position
                    self.text_editor.insert(tk.INSERT, weather_text)
                else:
                    messagebox.showwarning("Weather", "Unable to fetch current weather data")
            else:
                messagebox.showwarning("Weather", "Weather service not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add weather data: {str(e)}")
    
    def save_entry(self):
        """Save journal entry with weather data."""
        try:
            title = self.title_entry.get().strip()
            content = self.text_editor.get("1.0", tk.END).strip()
            mood = self.mood_var.get()
            
            if not title:
                messagebox.showwarning("Validation", "Please enter a title for your entry")
                return
            
            if not content:
                messagebox.showwarning("Validation", "Please enter some content for your entry")
                return
            
            # Get current weather data
            weather_data = {}
            try:
                if self.weather_service:
                    current_weather = self.weather_service.get_current_weather()
                    if current_weather:
                        weather_data = {
                            "temperature": current_weather.get('temperature'),
                            "condition": current_weather.get('condition'),
                            "location": current_weather.get('location'),
                            "humidity": current_weather.get('humidity'),
                            "wind_speed": current_weather.get('wind_speed')
                        }
            except Exception as e:
                print(f"Warning: Could not fetch weather data: {e}")
            
            # Create entry
            entry = {
                "id": self.current_entry_id or str(uuid.uuid4()),
                "title": title,
                "content": content,
                "mood": mood,
                "timestamp": datetime.now().isoformat(),
                "weather": weather_data
            }
            
            # Save to database
            if self.current_entry_id:
                # Update existing entry
                self.db_service.update_journal_entry(entry)
                messagebox.showinfo("Success", "Entry updated successfully!")
            else:
                # Save new entry
                self.db_service.save_journal_entry(entry)
                messagebox.showinfo("Success", "Entry saved successfully!")
            
            # Refresh entries list and clear form
            self.load_entries()
            self.clear_entry_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {str(e)}")
    
    def clear_entry_form(self):
        """Clear the entry form."""
        self.title_entry.delete(0, tk.END)
        self.text_editor.delete("1.0", tk.END)
        self.mood_var.set("neutral")
        self.current_entry_id = None
        self.update_weather_info()
    
    def load_entries(self):
        """Load and display journal entries."""
        try:
            self.entries = self.db_service.get_journal_entries()
            self.display_entries()
        except Exception as e:
            print(f"Error loading entries: {e}")
            self.entries = []
            self.display_entries()
    
    def display_entries(self, filtered_entries=None):
        """Display entries in the scrollable list."""
        # Clear existing entries
        for widget in self.entries_scrollable.winfo_children():
            widget.destroy()
        
        entries_to_show = filtered_entries if filtered_entries is not None else self.entries
        
        if not entries_to_show:
            no_entries_label = ctk.CTkLabel(
                self.entries_scrollable,
                text="No entries found. Create your first journal entry!",
                font=("Arial", 14),
                text_color="gray"
            )
            no_entries_label.grid(row=0, column=0, pady=50)
            return
        
        # Sort entries by timestamp (newest first)
        entries_to_show.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        for i, entry in enumerate(entries_to_show):
            self.create_entry_card(entry, i)
    
    def create_entry_card(self, entry, row):
        """Create a card for displaying an entry."""
        # Entry card frame
        card_frame = ctk.CTkFrame(self.entries_scrollable)
        card_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Mood emoji
        mood_emoji = {
            "happy": "😊",
            "neutral": "😐",
            "sad": "😢",
            "excited": "😎",
            "tired": "😴"
        }.get(entry.get('mood', 'neutral'), "😐")
        
        mood_label = ctk.CTkLabel(
            card_frame,
            text=mood_emoji,
            font=("Arial", 24)
        )
        mood_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        
        # Entry info frame
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            info_frame,
            text=entry.get('title', 'Untitled'),
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew")
        
        # Timestamp
        try:
            timestamp = datetime.fromisoformat(entry.get('timestamp', ''))
            time_text = timestamp.strftime('%Y-%m-%d %H:%M')
        except:
            time_text = entry.get('timestamp', 'Unknown time')
        
        time_label = ctk.CTkLabel(
            info_frame,
            text=time_text,
            font=("Arial", 10),
            text_color="gray",
            anchor="w"
        )
        time_label.grid(row=1, column=0, sticky="ew")
        
        # Content preview
        content = entry.get('content', '')
        preview = content[:100] + "..." if len(content) > 100 else content
        preview = preview.replace('\n', ' ')  # Remove line breaks for preview
        
        content_label = ctk.CTkLabel(
            info_frame,
            text=preview,
            font=("Arial", 11),
            text_color="lightgray",
            anchor="w",
            wraplength=400
        )
        content_label.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        # Weather info
        weather = entry.get('weather', {})
        if weather and weather.get('temperature'):
            weather_text = f"🌤️ {weather.get('temperature')}°C, {weather.get('condition', 'N/A')}"
            weather_label = ctk.CTkLabel(
                info_frame,
                text=weather_text,
                font=("Arial", 9),
                text_color="lightblue",
                anchor="w"
            )
            weather_label.grid(row=3, column=0, sticky="ew", pady=(2, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Edit",
            command=lambda e=entry: self.edit_entry(e),
            width=60,
            height=30
        )
        edit_btn.grid(row=0, column=0, pady=2)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            command=lambda e=entry: self.delete_entry(e),
            width=60,
            height=30,
            fg_color="#8B0000",
            hover_color="#A52A2A"
        )
        delete_btn.grid(row=1, column=0, pady=2)
    
    def edit_entry(self, entry):
        """Load entry for editing."""
        self.current_entry_id = entry.get('id')
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, entry.get('title', ''))
        
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", entry.get('content', ''))
        
        self.mood_var.set(entry.get('mood', 'neutral'))
        
        # Scroll to top
        self.container.focus_set()
    
    def delete_entry(self, entry):
        """Delete an entry after confirmation."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{entry.get('title', 'this entry')}'?"):
            try:
                self.db_service.delete_journal_entry(entry.get('id'))
                self.load_entries()
                messagebox.showinfo("Success", "Entry deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entry: {str(e)}")
    
    def filter_entries(self, event=None):
        """Filter entries based on search and mood filter."""
        search_text = self.search_entry.get().lower().strip()
        mood_filter = self.mood_filter.get()
        
        filtered = []
        for entry in self.entries:
            # Check search text
            if search_text:
                title_match = search_text in entry.get('title', '').lower()
                content_match = search_text in entry.get('content', '').lower()
                mood_match = search_text in entry.get('mood', '').lower()
                
                if not (title_match or content_match or mood_match):
                    continue
            
            # Check mood filter
            if mood_filter != "All" and entry.get('mood') != mood_filter:
                continue
            
            filtered.append(entry)
        
        self.display_entries(filtered)