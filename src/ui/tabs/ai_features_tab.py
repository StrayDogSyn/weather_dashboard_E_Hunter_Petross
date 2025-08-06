import customtkinter as ctk
from ..components.glassmorphic import GlassPanel
from ..components.common.loading_spinner import LoadingSpinner
from ...services.ai.ai_manager import AIManager
import threading
import logging

logger = logging.getLogger(__name__)

class AIFeaturesTab(ctk.CTkFrame):
    """Enhanced consolidated AI Features tab with all AI functionality."""
    
    def __init__(self, parent, weather_service, gemini_service):
        super().__init__(parent, fg_color="transparent")
        self.weather_service = weather_service
        self.gemini_service = gemini_service
        self.ai_manager = None
        self.current_feature = "analysis"
        self.setup_ui()
        self.initialize_ai_manager()

    def setup_ui(self):
        """Create unified AI features interface"""
        # Main container
        self.main_container = GlassPanel(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Feature selector (tabs within tab)
        self.create_feature_selector()
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Load default feature
        self.show_weather_analysis()

    def create_header(self):
        """Create unified header"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🤖 AI Weather Features",
            font=("Arial", 24, "bold"),
            text_color="#00D4FF"
        )
        title_label.pack(side="left")
        
        # Status indicator
        self.ai_status = ctk.CTkLabel(
            header_frame,
            text="✅ AI Ready",
            font=("Arial", 12),
            text_color="#4ECDC4"
        )
        self.ai_status.pack(side="right", padx=20)

    def create_feature_selector(self):
        """Create feature selection buttons"""
        selector_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        selector_frame.pack(fill="x", padx=20, pady=10)
        
        # Feature buttons
        self.feature_buttons = {}
        features = [
            ("🔍 Weather Analysis", "analysis", self.show_weather_analysis),
            ("🎯 Activity Suggestions", "activities", self.show_activity_suggestions),
            ("🎭 Weather Poetry", "poetry", self.show_weather_poetry),
            ("📊 Weather Insights", "insights", self.show_weather_insights),
            ("🎵 Weather Stories", "stories", self.show_weather_stories)
        ]
        
        for text, key, command in features:
            btn = ctk.CTkButton(
                selector_frame,
                text=text,
                command=command,
                fg_color="#2B2B2B",
                hover_color="#00D4FF",
                height=40,
                font=("Arial", 12)
            )
            btn.pack(side="left", padx=5, fill="x", expand=True)
            self.feature_buttons[key] = btn
        
        # Highlight active feature
        self.set_active_feature("analysis")

    def set_active_feature(self, feature_key):
        """Highlight active feature button"""
        self.current_feature = feature_key
        for key, btn in self.feature_buttons.items():
            if key == feature_key:
                btn.configure(fg_color="#00D4FF", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="#2B2B2B", text_color="#FFFFFF")

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def initialize_ai_manager(self):
        """Initialize AI manager for enhanced features"""
        try:
            # Get API key from gemini service instead of passing the service object
            api_key = getattr(self.gemini_service, 'api_key', None) if self.gemini_service else None
            self.ai_manager = AIManager(api_key)
            self.ai_status.configure(text="✅ AI Ready", text_color="#4ECDC4")
        except Exception as e:
            logger.error(f"Failed to initialize AI manager: {e}")
            self.ai_status.configure(text="❌ AI Unavailable", text_color="#FF6B6B")

    def show_weather_analysis(self):
        """Show weather analysis feature"""
        self.set_active_feature("analysis")
        self.clear_content()
        
        # Create analysis interface
        analysis_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
        analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            analysis_frame,
            text="🔍 AI Weather Analysis",
            font=("Arial", 18, "bold"),
            text_color="#00D4FF"
        )
        title.pack(pady=20)
        
        # Analysis content
        self.create_analysis_content(analysis_frame)

    def show_activity_suggestions(self):
        """Show activity suggestions feature"""
        self.set_active_feature("activities")
        self.clear_content()
        
        # Create activities interface
        activities_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
        activities_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            activities_frame,
            text="🎯 AI Activity Suggestions",
            font=("Arial", 18, "bold"),
            text_color="#00D4FF"
        )
        title.pack(pady=20)
        
        # Activities content
        self.create_activities_content(activities_frame)

    def show_weather_poetry(self):
        """Show weather poetry feature"""
        self.set_active_feature("poetry")
        self.clear_content()
        
        # Create poetry interface
        poetry_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
        poetry_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            poetry_frame,
            text="🎭 AI Weather Poetry",
            font=("Arial", 18, "bold"),
            text_color="#00D4FF"
        )
        title.pack(pady=20)
        
        # Poetry content
        self.create_poetry_content(poetry_frame)

    def show_weather_insights(self):
        """Show weather insights feature"""
        self.set_active_feature("insights")
        self.clear_content()
        
        # Create insights interface
        insights_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
        insights_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            insights_frame,
            text="📊 AI Weather Insights",
            font=("Arial", 18, "bold"),
            text_color="#00D4FF"
        )
        title.pack(pady=20)
        
        # Insights content
        self.create_insights_content(insights_frame)

    def show_weather_stories(self):
        """Show weather stories feature"""
        self.set_active_feature("stories")
        self.clear_content()
        
        # Create stories interface
        stories_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
        stories_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            stories_frame,
            text="🎵 AI Weather Stories",
            font=("Arial", 18, "bold"),
            text_color="#00D4FF"
        )
        title.pack(pady=20)
        
        # Stories content
        self.create_stories_content(stories_frame)

    def create_analysis_content(self, parent):
        """Create weather analysis content"""
        # Analysis input
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        analysis_label = ctk.CTkLabel(
            input_frame,
            text="Ask AI to analyze current weather conditions:",
            font=("Arial", 12)
        )
        analysis_label.pack(anchor="w", pady=(0, 5))
        
        self.analysis_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="e.g., What should I wear today?",
            height=40,
            font=("Arial", 12)
        )
        self.analysis_entry.pack(fill="x", pady=(0, 10))
        
        analyze_btn = ctk.CTkButton(
            input_frame,
            text="🔍 Analyze Weather",
            command=self.perform_weather_analysis,
            fg_color="#00D4FF",
            hover_color="#0099CC",
            height=40
        )
        analyze_btn.pack(pady=5)
        
        # Results area
        self.analysis_results = ctk.CTkTextbox(
            parent,
            height=300,
            font=("Arial", 11),
            wrap="word"
        )
        self.analysis_results.pack(fill="both", expand=True, padx=20, pady=10)
        self.analysis_results.insert("1.0", "AI weather analysis results will appear here...")

    def create_activities_content(self, parent):
        """Create activity suggestions content"""
        # Activity preferences
        prefs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        prefs_frame.pack(fill="x", padx=20, pady=10)
        
        prefs_label = ctk.CTkLabel(
            prefs_frame,
            text="Activity Preferences:",
            font=("Arial", 12, "bold")
        )
        prefs_label.pack(anchor="w", pady=(0, 5))
        
        # Activity type selector
        self.activity_type = ctk.CTkComboBox(
            prefs_frame,
            values=["Outdoor", "Indoor", "Sports", "Relaxation", "Adventure", "Cultural"],
            height=35
        )
        self.activity_type.pack(fill="x", pady=(0, 10))
        self.activity_type.set("Outdoor")
        
        suggest_btn = ctk.CTkButton(
            prefs_frame,
            text="🎯 Get AI Suggestions",
            command=self.generate_activity_suggestions,
            fg_color="#4ECDC4",
            hover_color="#3BA99C",
            height=40
        )
        suggest_btn.pack(pady=5)
        
        # Suggestions area
        self.activities_results = ctk.CTkTextbox(
            parent,
            height=300,
            font=("Arial", 11),
            wrap="word"
        )
        self.activities_results.pack(fill="both", expand=True, padx=20, pady=10)
        self.activities_results.insert("1.0", "AI activity suggestions will appear here...")

    def create_poetry_content(self, parent):
        """Create weather poetry content"""
        # Poetry style selector
        style_frame = ctk.CTkFrame(parent, fg_color="transparent")
        style_frame.pack(fill="x", padx=20, pady=10)
        
        style_label = ctk.CTkLabel(
            style_frame,
            text="Poetry Style:",
            font=("Arial", 12, "bold")
        )
        style_label.pack(anchor="w", pady=(0, 5))
        
        self.poetry_style = ctk.CTkComboBox(
            style_frame,
            values=["Haiku", "Sonnet", "Free Verse", "Limerick", "Acrostic"],
            height=35
        )
        self.poetry_style.pack(fill="x", pady=(0, 10))
        self.poetry_style.set("Haiku")
        
        generate_btn = ctk.CTkButton(
            style_frame,
            text="🎭 Generate Poetry",
            command=self.generate_weather_poetry,
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            height=40
        )
        generate_btn.pack(pady=5)
        
        # Poetry display
        self.poetry_results = ctk.CTkTextbox(
            parent,
            height=300,
            font=("Arial", 12),
            wrap="word"
        )
        self.poetry_results.pack(fill="both", expand=True, padx=20, pady=10)
        self.poetry_results.insert("1.0", "AI-generated weather poetry will appear here...")

    def create_insights_content(self, parent):
        """Create weather insights content"""
        # Insights controls
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        insights_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Generate Weather Insights",
            command=self.generate_weather_insights,
            fg_color="#E67E22",
            hover_color="#D35400",
            height=40
        )
        insights_btn.pack(pady=5)
        
        # Insights display
        self.insights_results = ctk.CTkTextbox(
            parent,
            height=300,
            font=("Arial", 11),
            wrap="word"
        )
        self.insights_results.pack(fill="both", expand=True, padx=20, pady=10)
        self.insights_results.insert("1.0", "AI weather insights will appear here...")

    def create_stories_content(self, parent):
        """Create weather stories content"""
        # Story controls
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        story_label = ctk.CTkLabel(
            controls_frame,
            text="Story Theme:",
            font=("Arial", 12, "bold")
        )
        story_label.pack(anchor="w", pady=(0, 5))
        
        self.story_theme = ctk.CTkComboBox(
            controls_frame,
            values=["Adventure", "Mystery", "Romance", "Fantasy", "Sci-Fi"],
            height=35
        )
        self.story_theme.pack(fill="x", pady=(0, 10))
        self.story_theme.set("Adventure")
        
        story_btn = ctk.CTkButton(
            controls_frame,
            text="🎵 Create Weather Story",
            command=self.generate_weather_story,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            height=40
        )
        story_btn.pack(pady=5)
        
        # Story display
        self.stories_results = ctk.CTkTextbox(
            parent,
            height=300,
            font=("Arial", 11),
            wrap="word"
        )
        self.stories_results.pack(fill="both", expand=True, padx=20, pady=10)
        self.stories_results.insert("1.0", "AI-generated weather stories will appear here...")

    def generate_activity_suggestions(self):
        """Generate AI activity suggestions"""
        if not self.ai_manager:
            self.activities_results.delete("1.0", "end")
            self.activities_results.insert("1.0", "❌ AI service unavailable. Please check your configuration.")
            return
        
        activity_type = self.activity_type.get()
        self.activities_results.delete("1.0", "end")
        self.activities_results.insert("1.0", "🔄 Generating activity suggestions...")
        
        def generate():
            try:
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    suggestions = loop.run_until_complete(self.ai_manager.get_activity_suggestions(weather_data))
                    
                    # Format the result for display
                    if isinstance(suggestions, dict) and 'suggestions' in suggestions:
                        formatted_result = "🎯 **Activity Suggestions:**\n\n"
                        for activity in suggestions['suggestions'][:5]:  # Show top 5
                            formatted_result += f"• **{activity.get('name', 'Activity')}**\n"
                            formatted_result += f"  {activity.get('description', 'No description')}\n\n"
                    else:
                        formatted_result = str(suggestions)
                    
                    self.after(0, lambda: self.display_activities_result(formatted_result))
                else:
                    self.after(0, lambda: self.display_activities_result("❌ No weather data available for suggestions."))
            except Exception as activity_error:
                logger.error(f"Activity suggestion error: {activity_error}")
                self.after(0, lambda: self.display_activities_result(f"❌ Suggestion failed: {str(activity_error)}"))
        
        threading.Thread(target=generate, daemon=True).start()

    def perform_weather_analysis(self):
        """Perform AI weather analysis"""
        if not self.ai_manager:
            self.analysis_results.delete("1.0", "end")
            self.analysis_results.insert("1.0", "❌ AI service unavailable. Please check your configuration.")
            return
        
        query = self.analysis_entry.get().strip()
        if not query:
            query = "Analyze the current weather conditions"
        
        self.analysis_results.delete("1.0", "end")
        self.analysis_results.insert("1.0", "🔄 Analyzing weather conditions...")
        
        def analyze():
            try:
                # Get current weather data
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    analysis = loop.run_until_complete(self.ai_manager.get_weather_insights(weather_data))
                    self.after(0, lambda: self.display_analysis_result(analysis))
                else:
                    self.after(0, lambda: self.display_analysis_result("❌ No weather data available for analysis."))
            except Exception as analysis_error:
                logger.error(f"Weather analysis error: {analysis_error}")
                self.after(0, lambda: self.display_analysis_result(f"❌ Analysis failed: {str(analysis_error)}"))
        
        threading.Thread(target=analyze, daemon=True).start()

    def display_analysis_result(self, result):
        """Display analysis result"""
        self.analysis_results.delete("1.0", "end")
        self.analysis_results.insert("1.0", result)

    def display_activities_result(self, result):
        """Display activities result"""
        self.activities_results.delete("1.0", "end")
        self.activities_results.insert("1.0", result)

    def generate_weather_poetry(self):
        """Generate AI weather poetry"""
        if not self.ai_manager:
            self.poetry_results.delete("1.0", "end")
            self.poetry_results.insert("1.0", "❌ AI service unavailable. Please check your configuration.")
            return
        
        style = self.poetry_style.get()
        self.poetry_results.delete("1.0", "end")
        self.poetry_results.insert("1.0", "🔄 Composing weather poetry...")
        
        def generate():
            try:
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    poetry = loop.run_until_complete(self.ai_manager.generate_weather_poetry(style.lower(), weather_data))
                    
                    # Format the result for display
                    if isinstance(poetry, dict) and 'poem' in poetry:
                        formatted_result = f"🎭 **{poetry.get('style', 'Poetry').title()}**\n\n{poetry['poem']}"
                    else:
                        formatted_result = str(poetry)
                    
                    self.after(0, lambda: self.display_poetry_result(formatted_result))
                else:
                    self.after(0, lambda: self.display_poetry_result("❌ No weather data available for poetry."))
            except Exception as poetry_error:
                logger.error(f"Poetry generation error: {poetry_error}")
                self.after(0, lambda: self.display_poetry_result(f"❌ Poetry generation failed: {str(poetry_error)}"))
        
        threading.Thread(target=generate, daemon=True).start()

    def display_poetry_result(self, result):
        """Display poetry result"""
        self.poetry_results.delete("1.0", "end")
        self.poetry_results.insert("1.0", result)

    def generate_weather_insights(self):
        """Generate AI weather insights"""
        if not self.ai_manager:
            self.insights_results.delete("1.0", "end")
            self.insights_results.insert("1.0", "❌ AI service unavailable. Please check your configuration.")
            return
        
        self.insights_results.delete("1.0", "end")
        self.insights_results.insert("1.0", "🔄 Generating weather insights...")
        
        def generate():
            try:
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    insights = loop.run_until_complete(self.ai_manager.get_weather_insights(weather_data))
                    self.after(0, lambda: self.display_insights_result(insights))
                else:
                    self.after(0, lambda: self.display_insights_result("❌ No weather data available for insights."))
            except Exception as insights_error:
                logger.error(f"Insights generation error: {insights_error}")
                self.after(0, lambda: self.display_insights_result(f"❌ Insights generation failed: {str(insights_error)}"))
        
        threading.Thread(target=generate, daemon=True).start()

    def display_insights_result(self, result):
        """Display insights result"""
        self.insights_results.delete("1.0", "end")
        self.insights_results.insert("1.0", result)

    def generate_weather_story(self):
        """Generate AI weather story"""
        if not self.ai_manager:
            self.stories_results.delete("1.0", "end")
            self.stories_results.insert("1.0", "❌ AI service unavailable. Please check your configuration.")
            return
        
        theme = self.story_theme.get()
        self.stories_results.delete("1.0", "end")
        self.stories_results.insert("1.0", "🔄 Creating weather story...")
        
        def generate():
            try:
                weather_data = self.weather_service.get_current_weather()
                if weather_data:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    story = loop.run_until_complete(self.ai_manager.generate_weather_story(weather_data, "short"))
                    
                    # Format the result for display
                    if isinstance(story, dict) and 'story' in story:
                        formatted_result = f"📖 **Weather Story**\n\n{story['story']}"
                    else:
                        formatted_result = str(story)
                    
                    self.after(0, lambda: self.display_stories_result(formatted_result))
                else:
                    self.after(0, lambda: self.display_stories_result("❌ No weather data available for story."))
            except Exception as story_error:
                logger.error(f"Story generation error: {story_error}")
                self.after(0, lambda: self.display_stories_result(f"❌ Story generation failed: {str(story_error)}"))
        
        threading.Thread(target=generate, daemon=True).start()

    def display_stories_result(self, result):
        """Display stories result"""
        self.stories_results.delete("1.0", "end")
        self.stories_results.insert("1.0", result)