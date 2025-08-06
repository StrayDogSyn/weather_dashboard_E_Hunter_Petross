"""Activity Suggester Tab with Gemini AI Integration."""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
import json
import re

from ..components.glassmorphic import GlassmorphicFrame
from ..components.glassmorphic.glass_button import GlassButton
from ...utils.error_wrapper import ensure_main_thread


class ActivitySuggesterTab(ctk.CTkFrame):
    """AI-powered activity suggester based on weather conditions."""
    
    def __init__(self, parent, weather_service, gemini_service=None):
        super().__init__(parent)
        self.weather_service = weather_service
        self.gemini_service = gemini_service
        self.suggestions = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components."""
        # Main container with glassmorphic styling
        try:
            self.container = GlassmorphicFrame(self)
        except:
            self.container = ctk.CTkFrame(self, fg_color=("#2b2b2b", "#1a1a1a"))
        
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header()
        
        # Control panel
        self.create_controls()
        
        # Suggestions display area
        self.create_suggestion_cards()
        
        # Load initial suggestions
        self.refresh_suggestions()
        
    def create_header(self):
        """Create the header section."""
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🤖 AI Activity Suggestions",
            font=("Segoe UI", 24, "bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        )
        title_label.pack(side="left")
        
        # Weather info display
        self.weather_info_label = ctk.CTkLabel(
            header_frame,
            text="Loading weather...",
            font=("Segoe UI", 12),
            text_color=("#CCCCCC", "#CCCCCC")
        )
        self.weather_info_label.pack(side="right")
        
    def create_controls(self):
        """Create control buttons and options."""
        controls_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Refresh button
        try:
            refresh_btn = GlassButton(
                controls_frame,
                text="🔄 Get New Suggestions",
                command=self.refresh_suggestions
            )
        except:
            refresh_btn = ctk.CTkButton(
                controls_frame,
                text="🔄 Get New Suggestions",
                command=self.refresh_suggestions,
                fg_color="#00D4FF",
                hover_color="#0099CC"
            )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Activity type filter
        self.activity_type = ctk.CTkOptionMenu(
            controls_frame,
            values=["All Activities", "Indoor", "Outdoor", "Sports", "Relaxation", "Social"],
            command=self.filter_suggestions
        )
        self.activity_type.pack(side="left", padx=10)
        
        # Duration filter
        self.duration_filter = ctk.CTkOptionMenu(
            controls_frame,
            values=["Any Duration", "< 30 min", "30-60 min", "1-2 hours", "2+ hours"],
            command=self.filter_suggestions
        )
        self.duration_filter.pack(side="left", padx=10)
        
    def create_suggestion_cards(self):
        """Create activity suggestion cards container."""
        # Scrollable frame for suggestions
        self.cards_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            height=400
        )
        self.cards_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
    @ensure_main_thread
    def refresh_suggestions(self):
        """Refresh activity suggestions based on current weather."""
        try:
            # Update weather info display
            self.update_weather_display()
            
            # Get suggestions (async if Gemini available, fallback otherwise)
            if self.gemini_service:
                # Run async suggestion generation
                asyncio.create_task(self.get_ai_suggestions())
            else:
                # Use fallback suggestions
                self.suggestions = self.get_fallback_suggestions()
                self.display_suggestions(self.suggestions)
                
        except Exception as e:
            print(f"Error refreshing suggestions: {e}")
            # Fallback to default suggestions
            self.suggestions = self.get_fallback_suggestions()
            self.display_suggestions(self.suggestions)
            
    def update_weather_display(self):
        """Update the weather information display."""
        try:
            weather = self.weather_service.get_current_weather()
            if weather:
                weather_text = f"🌡️ {weather.get('temperature', 'N/A')}°C | {weather.get('condition', 'Unknown')} | 💨 {weather.get('wind_speed', 'N/A')} km/h"
                self.weather_info_label.configure(text=weather_text)
            else:
                self.weather_info_label.configure(text="Weather data unavailable")
        except Exception as e:
            self.weather_info_label.configure(text="Weather data error")
            
    async def get_ai_suggestions(self):
        """Get AI-powered suggestions using Gemini."""
        try:
            weather = self.weather_service.get_current_weather()
            if not weather:
                self.suggestions = self.get_fallback_suggestions()
                self.display_suggestions(self.suggestions)
                return
                
            # Create detailed prompt for Gemini
            prompt = self.create_gemini_prompt(weather)
            
            # Get AI response
            response = await self.gemini_service.generate_content(prompt)
            
            # Parse and display suggestions
            self.suggestions = self.parse_ai_suggestions(response)
            self.display_suggestions(self.suggestions)
            
        except Exception as e:
            print(f"Error getting AI suggestions: {e}")
            # Fallback to default suggestions
            self.suggestions = self.get_fallback_suggestions()
            self.display_suggestions(self.suggestions)
            
    def create_gemini_prompt(self, weather):
        """Create a detailed prompt for Gemini AI."""
        current_time = datetime.now()
        time_of_day = "morning" if current_time.hour < 12 else "afternoon" if current_time.hour < 18 else "evening"
        
        prompt = f"""
Suggest 6 diverse activities for the following weather conditions:

Weather Details:
- Temperature: {weather.get('temperature', 'Unknown')}°C
- Condition: {weather.get('condition', 'Unknown')}
- Wind Speed: {weather.get('wind_speed', 'Unknown')} km/h
- Humidity: {weather.get('humidity', 'Unknown')}%
- Time: {current_time.strftime('%H:%M')} ({time_of_day})
- Season: {self.get_season()}

Please provide suggestions in this exact JSON format:
[
  {{
    "name": "Activity Name",
    "duration": "30-60 minutes",
    "type": "indoor/outdoor",
    "difficulty": "easy/moderate/challenging",
    "required_items": ["item1", "item2"],
    "description": "Brief description of the activity",
    "weather_reason": "Why this activity is perfect for current weather",
    "tips": ["tip1", "tip2"]
  }}
]

Consider:
- Indoor and outdoor options
- Different activity types (sports, creative, social, relaxation)
- Varying difficulty levels
- Time of day appropriateness
- Safety considerations for weather conditions
"""
        return prompt
        
    def get_season(self):
        """Determine current season."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
            
    def parse_ai_suggestions(self, response):
        """Parse AI response into structured suggestions."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions_data = json.loads(json_match.group())
                return suggestions_data
            else:
                # Fallback parsing if JSON not found
                return self.parse_text_suggestions(response)
        except Exception as e:
            print(f"Error parsing AI suggestions: {e}")
            return self.get_fallback_suggestions()
            
    def parse_text_suggestions(self, text):
        """Parse text-based suggestions as fallback."""
        suggestions = []
        lines = text.split('\n')
        current_suggestion = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('- Activity name:') or line.startswith('Activity:'):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {
                    'name': line.split(':', 1)[1].strip(),
                    'duration': 'Variable',
                    'type': 'general',
                    'difficulty': 'moderate',
                    'required_items': [],
                    'description': '',
                    'weather_reason': '',
                    'tips': []
                }
            elif line.startswith('- Duration:') and current_suggestion:
                current_suggestion['duration'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Required items:') and current_suggestion:
                items = line.split(':', 1)[1].strip().split(',')
                current_suggestion['required_items'] = [item.strip() for item in items]
            elif line.startswith('- Why') and current_suggestion:
                current_suggestion['weather_reason'] = line.split(':', 1)[1].strip()
                
        if current_suggestion:
            suggestions.append(current_suggestion)
            
        return suggestions[:6]  # Limit to 6 suggestions
        
    def get_fallback_suggestions(self):
        """Provide fallback suggestions when AI is unavailable."""
        try:
            weather = self.weather_service.get_current_weather()
            temp = weather.get('temperature', 20) if weather else 20
            condition = weather.get('condition', '').lower() if weather else ''
            
            suggestions = []
            
            # Temperature-based suggestions
            if temp < 0:
                suggestions.extend([
                    {
                        'name': '❄️ Hot Chocolate & Reading',
                        'duration': '1-2 hours',
                        'type': 'indoor',
                        'difficulty': 'easy',
                        'required_items': ['Hot chocolate', 'Cozy blanket', 'Good book'],
                        'description': 'Perfect cozy indoor activity for cold weather',
                        'weather_reason': 'Stay warm and comfortable indoors',
                        'tips': ['Choose a comfortable reading spot', 'Add marshmallows to hot chocolate']
                    },
                    {
                        'name': '🏠 Indoor Workout',
                        'duration': '30-45 minutes',
                        'type': 'indoor',
                        'difficulty': 'moderate',
                        'required_items': ['Exercise mat', 'Water bottle'],
                        'description': 'Stay active and warm with indoor exercises',
                        'weather_reason': 'Generate body heat while staying indoors',
                        'tips': ['Start with warm-up exercises', 'Stay hydrated']
                    }
                ])
            elif temp > 25:
                suggestions.extend([
                    {
                        'name': '🏊 Swimming or Water Activities',
                        'duration': '1-2 hours',
                        'type': 'outdoor',
                        'difficulty': 'easy',
                        'required_items': ['Swimwear', 'Sunscreen', 'Towel'],
                        'description': 'Cool off with refreshing water activities',
                        'weather_reason': 'Perfect temperature for water activities',
                        'tips': ['Apply sunscreen regularly', 'Stay hydrated']
                    },
                    {
                        'name': '🌳 Shaded Park Walk',
                        'duration': '45-60 minutes',
                        'type': 'outdoor',
                        'difficulty': 'easy',
                        'required_items': ['Water bottle', 'Hat', 'Comfortable shoes'],
                        'description': 'Enjoy nature while staying cool in shade',
                        'weather_reason': 'Avoid direct sun while enjoying outdoors',
                        'tips': ['Choose shaded paths', 'Take breaks as needed']
                    }
                ])
            else:
                suggestions.extend([
                    {
                        'name': '🚶 Nature Walk',
                        'duration': '45-90 minutes',
                        'type': 'outdoor',
                        'difficulty': 'easy',
                        'required_items': ['Comfortable shoes', 'Water bottle'],
                        'description': 'Enjoy the pleasant weather with a nature walk',
                        'weather_reason': 'Perfect temperature for outdoor activities',
                        'tips': ['Choose scenic routes', 'Bring a camera']
                    },
                    {
                        'name': '☕ Outdoor Café Visit',
                        'duration': '1-2 hours',
                        'type': 'outdoor',
                        'difficulty': 'easy',
                        'required_items': ['Light jacket (optional)'],
                        'description': 'Enjoy coffee or tea at an outdoor café',
                        'weather_reason': 'Comfortable temperature for outdoor dining',
                        'tips': ['Choose a café with outdoor seating', 'Try local specialties']
                    }
                ])
                
            # Weather condition-based suggestions
            if 'rain' in condition:
                suggestions.append({
                    'name': '🎨 Indoor Creative Project',
                    'duration': '2-3 hours',
                    'type': 'indoor',
                    'difficulty': 'moderate',
                    'required_items': ['Art supplies', 'Craft materials'],
                    'description': 'Perfect time for creative indoor activities',
                    'weather_reason': 'Rainy weather is ideal for focused creative work',
                    'tips': ['Set up a dedicated workspace', 'Play relaxing music']
                })
            elif 'sun' in condition:
                suggestions.append({
                    'name': '📸 Photography Walk',
                    'duration': '1-2 hours',
                    'type': 'outdoor',
                    'difficulty': 'easy',
                    'required_items': ['Camera or smartphone', 'Comfortable shoes'],
                    'description': 'Capture beautiful moments in great lighting',
                    'weather_reason': 'Sunny weather provides excellent lighting',
                    'tips': ['Golden hour lighting is best', 'Experiment with angles']
                })
                
            # Always include these versatile options
            suggestions.extend([
                {
                    'name': '🧘 Meditation & Mindfulness',
                    'duration': '15-30 minutes',
                    'type': 'indoor',
                    'difficulty': 'easy',
                    'required_items': ['Quiet space', 'Comfortable cushion'],
                    'description': 'Practice mindfulness and relaxation',
                    'weather_reason': 'Good for any weather, promotes well-being',
                    'tips': ['Find a quiet space', 'Start with short sessions']
                },
                {
                    'name': '👥 Video Call with Friends',
                    'duration': '30-60 minutes',
                    'type': 'indoor',
                    'difficulty': 'easy',
                    'required_items': ['Device with camera', 'Good internet connection'],
                    'description': 'Connect with friends and family virtually',
                    'weather_reason': 'Weather-independent social activity',
                    'tips': ['Schedule in advance', 'Prepare conversation topics']
                }
            ])
            
            return suggestions[:6]  # Return up to 6 suggestions
            
        except Exception as e:
            print(f"Error generating fallback suggestions: {e}")
            return [{
                'name': '📱 Explore New Apps',
                'duration': '30-60 minutes',
                'type': 'indoor',
                'difficulty': 'easy',
                'required_items': ['Smartphone or tablet'],
                'description': 'Discover new apps and digital tools',
                'weather_reason': 'Perfect indoor activity for any weather',
                'tips': ['Check app store recommendations', 'Read reviews before downloading']
            }]
            
    def filter_suggestions(self, filter_value=None):
        """Filter suggestions based on selected criteria."""
        if not self.suggestions:
            return
            
        filtered = self.suggestions.copy()
        
        # Filter by activity type
        activity_filter = self.activity_type.get()
        if activity_filter != "All Activities":
            if activity_filter == "Indoor":
                filtered = [s for s in filtered if s.get('type') == 'indoor']
            elif activity_filter == "Outdoor":
                filtered = [s for s in filtered if s.get('type') == 'outdoor']
            elif activity_filter == "Sports":
                filtered = [s for s in filtered if 'sport' in s.get('name', '').lower() or 'workout' in s.get('name', '').lower()]
            elif activity_filter == "Relaxation":
                filtered = [s for s in filtered if any(word in s.get('name', '').lower() for word in ['relax', 'meditation', 'read', 'coffee', 'tea'])]
            elif activity_filter == "Social":
                filtered = [s for s in filtered if any(word in s.get('name', '').lower() for word in ['friend', 'social', 'call', 'visit', 'café'])]
                
        # Filter by duration
        duration_filter = self.duration_filter.get()
        if duration_filter != "Any Duration":
            # This is a simplified filter - in a real app, you'd parse duration strings more carefully
            if duration_filter == "< 30 min":
                filtered = [s for s in filtered if '15' in s.get('duration', '') or '30' in s.get('duration', '')]
            elif duration_filter == "30-60 min":
                filtered = [s for s in filtered if '30' in s.get('duration', '') or '45' in s.get('duration', '') or '60' in s.get('duration', '')]
                
        self.display_suggestions(filtered)
        
    def display_suggestions(self, suggestions: List[Dict]):
        """Display suggestion cards with glassmorphic styling."""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
            
        if not suggestions:
            no_results_label = ctk.CTkLabel(
                self.cards_frame,
                text="No suggestions match your filters. Try adjusting the criteria.",
                font=("Helvetica", 14),
                text_color="#CCCCCC"
            )
            no_results_label.pack(pady=50)
            return
            
        # Create cards for each suggestion
        for i, suggestion in enumerate(suggestions):
            card = self.create_activity_card(suggestion, i)
            card.pack(fill="x", padx=10, pady=8)
            
    def create_activity_card(self, suggestion: Dict, index: int):
        """Create an individual activity suggestion card."""
        # Main card frame
        try:
            card = GlassmorphicFrame(self.cards_frame)
        except:
            card = ctk.CTkFrame(
                self.cards_frame,
                fg_color=("#2b2b2b", "#1a1a1a"),
                corner_radius=15
            )
            
        # Card content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header with name and type
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Activity name
        name_label = ctk.CTkLabel(
            header_frame,
            text=suggestion.get('name', 'Unknown Activity'),
            font=("Helvetica", 16, "bold"),
            text_color="#00D4FF"
        )
        name_label.pack(side="left")
        
        # Activity type badge
        type_color = "#00FF88" if suggestion.get('type') == 'outdoor' else "#FF6B6B"
        # Create a blended background color for transparency effect
        def blend_color_with_bg(color: str, opacity: float = 0.125) -> str:
            """Blend color with dark background to simulate transparency."""
            try:
                color = color.lstrip("#")
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
                
                # Blend with dark background
                bg_r, bg_g, bg_b = 26, 26, 26  # Dark background
                new_r = int(r * opacity + bg_r * (1 - opacity))
                new_g = int(g * opacity + bg_g * (1 - opacity))
                new_b = int(b * opacity + bg_b * (1 - opacity))
                
                return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
            except (ValueError, IndexError):
                return "#1a1a1a"
        
        type_label = ctk.CTkLabel(
            header_frame,
            text=f"🏠 {suggestion.get('type', 'general').title()}",
            font=("Helvetica", 10),
            text_color=type_color,
            fg_color=blend_color_with_bg(type_color),
            corner_radius=10
        )
        type_label.pack(side="right", padx=(10, 0))
        
        # Duration and difficulty
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 10))
        
        duration_label = ctk.CTkLabel(
            info_frame,
            text=f"⏱️ {suggestion.get('duration', 'Variable')}",
            font=("Helvetica", 12),
            text_color="#CCCCCC"
        )
        duration_label.pack(side="left")
        
        difficulty_label = ctk.CTkLabel(
            info_frame,
            text=f"📊 {suggestion.get('difficulty', 'moderate').title()}",
            font=("Helvetica", 12),
            text_color="#CCCCCC"
        )
        difficulty_label.pack(side="right")
        
        # Description
        if suggestion.get('description'):
            desc_label = ctk.CTkLabel(
                content_frame,
                text=suggestion['description'],
                font=("Helvetica", 12),
                text_color="#E0E0E0",
                wraplength=400,
                justify="left"
            )
            desc_label.pack(fill="x", pady=(0, 10))
            
        # Weather reason
        if suggestion.get('weather_reason'):
            weather_label = ctk.CTkLabel(
                content_frame,
                text=f"🌤️ {suggestion['weather_reason']}",
                font=("Helvetica", 11, "italic"),
                text_color="#B0B0B0",
                wraplength=400,
                justify="left"
            )
            weather_label.pack(fill="x", pady=(0, 10))
            
        # Required items
        if suggestion.get('required_items'):
            items_text = "📋 " + ", ".join(suggestion['required_items'])
            items_label = ctk.CTkLabel(
                content_frame,
                text=items_text,
                font=("Helvetica", 11),
                text_color="#A0A0A0",
                wraplength=400,
                justify="left"
            )
            items_label.pack(fill="x", pady=(0, 10))
            
        # Tips (expandable)
        if suggestion.get('tips'):
            tips_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            tips_frame.pack(fill="x", pady=(5, 0))
            
            tips_text = "💡 " + " • ".join(suggestion['tips'])
            tips_label = ctk.CTkLabel(
                tips_frame,
                text=tips_text,
                font=("Helvetica", 10),
                text_color="#909090",
                wraplength=400,
                justify="left"
            )
            tips_label.pack(fill="x")
            
        return card