"""
Weather Poetry Service for Weather Dashboard.

This service generates weather-inspired poetry and creative phrases using both
template-based generation and AI-powered creation for unique content.
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional

import google.generativeai as genai
import requests

from ..config import config_manager
from ..models.capstone_models import WeatherPoem
from ..models.weather_models import CurrentWeather, WeatherCondition


class WeatherPoetryService:
    """Service for generating weather-inspired poetry and phrases."""

    def __init__(self):
        """Initialize the poetry service."""
        self.logger = logging.getLogger(__name__)
        self.config = config_manager.config.api
        self._load_poetry_templates()

        # AI API settings - Gemini Pro as primary, OpenAI as fallback
        self.gemini_enabled = bool(self.config.gemini_api_key)
        self.openai_enabled = bool(self.config.openai_api_key)
        self.ai_enabled = self.gemini_enabled or self.openai_enabled
        self.ai_fallback_chance = (
            self.config.ai_fallback_chance
        )  # Chance to use AI when available

        if self.gemini_enabled:
            self.logger.info(
                "Weather poetry service initialized with Gemini Pro (primary) + OpenAI (fallback)"
                if self.openai_enabled
                else "Weather poetry service initialized with Gemini Pro only"
            )
        elif self.openai_enabled:
            self.logger.info("Weather poetry service initialized with OpenAI only")
        else:
            self.logger.info(
                "Weather poetry service initialized with template-based generation"
            )
            self.logger.debug(
                "AI enhancement disabled - no Gemini or OpenAI API keys configured"
            )

    def _load_poetry_templates(self):
        """Load poetry templates and word banks."""
        # Haiku templates for different weather conditions
        self.haiku_templates = {
            WeatherCondition.CLEAR: [
                "Golden sunlight gleams / Across the cloudless blue sky / Nature's perfect day",
                "Bright rays kiss the earth / Azure dome stretches endless / Peaceful day unfolds",
                "Crystal clear blue sky / Sunshine warms the gentle breeze / Perfect day awaits",
                "Brilliant sunshine glows / Not a cloud in sight today / Pure sky overhead",
            ],
            WeatherCondition.CLOUDS: [
                "Fluffy clouds drift by / Painting pictures in the sky / Nature's art gallery",
                "Cotton ball clouds float / Across the canvas of sky / Ever-changing shapes",
                "Gray clouds gather near / Soft light filters through the mist / Peaceful overcast",
                "Cloudy skies above / Gentle light through silver veils / Calm and cozy day",
            ],
            WeatherCondition.RAIN: [
                "Raindrops dance on leaves / Nature's symphony begins / Earth drinks gratefully",
                "Gentle rain descends / Washing the world fresh and clean / Life renewed again",
                "Pitter-patter sounds / Rain taps rhythm on the roof / Nature's lullaby",
                "Silver rain cascades / From clouds heavy with their gift / Earth's thirst satisfied",
            ],
            WeatherCondition.SNOW: [
                "Snowflakes gently fall / Blanketing the world in white / Winter's peaceful hush",
                "Crystalline snow drifts / Each flake unique and perfect / Nature's frozen art",
                "White snow covers all / Silent world in winter dress / Pure and serene scene",
                "Soft snowflakes descend / Dancing in the winter air / Magical white day",
            ],
            WeatherCondition.THUNDERSTORM: [
                "Thunder rolls across / Lightning illuminates sky / Nature's power shows",
                "Storm clouds gather dark / Electric energy builds / Sky's dramatic dance",
                "Lightning splits the night / Thunder echoes through the air / Storm's magnificent show",
                "Dark storm approaches / Nature's fury unleashed wild / Electric sky blazes",
            ],
            WeatherCondition.FOG: [
                "Misty fog rolls in / Wrapping world in soft gray silk / Mystery surrounds",
                "Foggy morning veils / The landscape in gentle mist / Ethereal dawn",
                "Soft fog drifts along / Blurring edges of the world / Dreamlike atmosphere",
                "Morning mist rises / Creating a mystical scene / Fog's enchanting spell",
            ],
        }

        # Fun phrases for different weather conditions
        self.weather_phrases = {
            WeatherCondition.CLEAR: [
                "It's a picture-perfect day! ☀️",
                "Sunshine is nature's spotlight today! 🌞",
                "Blue skies and bright vibes! ✨",
                "What a gloriously sunny day! 🌈",
                "The sun is putting on quite a show! 🎭",
            ],
            WeatherCondition.CLOUDS: [
                "Clouds are nature's mood ring today! ☁️",
                "The sky is wearing its fluffy pajamas! 🌥️",
                "Cotton candy clouds are floating by! 🍭",
                "Nature's doing some cloud sculpting! 🎨",
                "The sky is feeling pleasantly dramatic! 🎭",
            ],
            WeatherCondition.RAIN: [
                "It's a splash-tastic day! 💧",
                "Nature's taking a refreshing shower! 🚿",
                "The sky is having a good cry (happy tears)! 😭",
                "Perfect weather for puddle jumping! 🦘",
                "Rain, rain, here to stay... and that's okay! ☔",
            ],
            WeatherCondition.SNOW: [
                "Snow day magic is in the air! ❄️",
                "Winter is sprinkling fairy dust! ✨",
                "Nature's having a pillow fight! 🪶",
                "The world's getting a cozy white blanket! 🤍",
                "Snowflakes are nature's confetti! 🎉",
            ],
            WeatherCondition.THUNDERSTORM: [
                "Nature's putting on a light show! ⚡",
                "The sky is having a dramatic moment! 🎭",
                "Thor is doing some cloud bowling! 🎳",
                "Electric atmosphere, literally! ⚡",
                "Mother Nature's sound and light spectacular! 🎆",
            ],
            WeatherCondition.FOG: [
                "It's a mysteriously beautiful day! 🌫️",
                "Nature's created a dreamy filter! 📸",
                "The world's wearing a soft gray sweater! 🧥",
                "Fog is nature's way of being mysterious! 🕵️",
                "Low-hanging cloud hugs for everyone! 🤗",
            ],
        }

        # Temperature-based descriptors
        self.temperature_descriptors = {
            "freezing": ["bone-chilling", "arctic", "icy", "frosty", "frozen"],
            "cold": ["crisp", "cool", "chilly", "brisk", "nippy"],
            "mild": ["pleasant", "comfortable", "gentle", "moderate", "agreeable"],
            "warm": ["cozy", "balmy", "pleasant", "delightful", "inviting"],
            "hot": ["scorching", "blazing", "sweltering", "tropical", "sizzling"],
        }

    def get_temperature_range(self, temperature: float) -> str:
        """Get temperature range category."""
        if temperature < 0:
            return "freezing"
        elif temperature < 10:
            return "cold"
        elif temperature < 20:
            return "mild"
        elif temperature < 30:
            return "warm"
        else:
            return "hot"

    def generate_haiku(self, weather: CurrentWeather) -> WeatherPoem:
        """
        Generate a haiku based on current weather conditions.

        Args:
            weather: Current weather data

        Returns:
            WeatherPoem with haiku
        """
        condition = weather.condition
        temp_range = self.get_temperature_range(weather.temperature.to_celsius())
        haiku_text = None

        # Try AI generation first if enabled and random chance triggers
        if self.ai_enabled and random.random() < self.ai_fallback_chance:
            ai_haiku = self._generate_ai_haiku(weather)
            if ai_haiku:
                haiku_text = ai_haiku
                api_used = "Gemini Pro" if self.gemini_enabled else "OpenAI"
                self.logger.info(
                    f"Generated AI haiku using {api_used} for {weather.location.display_name}"
                )

        # Fallback to template-based generation
        if not haiku_text:
            # Get haiku templates for the weather condition
            templates = self.haiku_templates.get(
                condition, self.haiku_templates[WeatherCondition.CLEAR]
            )
            haiku_text = random.choice(templates)

            # Sometimes create a custom haiku based on temperature
            if random.random() < 0.3:  # 30% chance for temperature-focused haiku
                temp_descriptor = random.choice(
                    self.temperature_descriptors[temp_range]
                )
                custom_haikus = self._create_temperature_haiku(
                    temp_descriptor, condition
                )
                if custom_haikus:
                    haiku_text = random.choice(custom_haikus)

            self.logger.info(
                f"Generated template haiku for {weather.location.display_name}"
            )

        poem = WeatherPoem(
            text=haiku_text,
            poem_type="haiku",
            weather_condition=condition,
            temperature_range=temp_range,
        )

        return poem

    def generate_fun_phrase(self, weather: CurrentWeather) -> WeatherPoem:
        """
        Generate a fun phrase based on current weather conditions.

        Args:
            weather: Current weather data

        Returns:
            WeatherPoem with fun phrase
        """
        condition = weather.condition
        temp_range = self.get_temperature_range(weather.temperature.to_celsius())
        phrase_text = None

        # Try AI generation first if enabled and random chance triggers
        if self.ai_enabled and random.random() < self.ai_fallback_chance:
            ai_phrase = self._generate_ai_phrase(weather)
            if ai_phrase:
                phrase_text = ai_phrase
                api_used = "Gemini Pro" if self.gemini_enabled else "OpenAI"
                self.logger.info(
                    f"Generated AI phrase using {api_used} for {weather.location.display_name}"
                )

        # Fallback to template-based generation
        if not phrase_text:
            # Get phrases for the weather condition
            phrases = self.weather_phrases.get(
                condition, self.weather_phrases[WeatherCondition.CLEAR]
            )
            phrase_text = random.choice(phrases)

            # Add temperature flavor 20% of the time
            if random.random() < 0.2:
                temp_descriptor = random.choice(
                    self.temperature_descriptors[temp_range]
                )
                phrase_text = f"{phrase_text[:-2]} with {temp_descriptor} vibes! 🌡️"

            self.logger.info(
                f"Generated template phrase for {weather.location.display_name}"
            )

        poem = WeatherPoem(
            text=phrase_text,
            poem_type="phrase",
            weather_condition=condition,
            temperature_range=temp_range,
        )

        return poem

    def generate_limerick(self, weather: CurrentWeather) -> WeatherPoem:
        """
        Generate a limerick based on current weather conditions.

        Args:
            weather: Current weather data

        Returns:
            WeatherPoem with limerick
        """
        condition = weather.condition
        temp_range = self.get_temperature_range(weather.temperature.to_celsius())
        city_name = weather.location.name
        limerick_text = None

        # Try AI generation first if enabled and random chance triggers
        if self.ai_enabled and random.random() < self.ai_fallback_chance:
            ai_limerick = self._generate_ai_limerick(weather)
            if ai_limerick:
                limerick_text = ai_limerick
                api_used = "Gemini Pro" if self.gemini_enabled else "OpenAI"
                self.logger.info(
                    f"Generated AI limerick using {api_used} for {weather.location.display_name}"
                )

        # Fallback to template-based generation
        if not limerick_text:
            # Basic limerick templates
            limericks = {
                WeatherCondition.CLEAR: [
                    f"There once was a day so bright, / When {city_name} basked in sunlight, / The sky was so blue, / With not a cloud too, / A truly magnificent sight!",
                    f"The sun over {city_name} did gleam, / Like something out of a dream, / So golden and warm, / In perfect good form, / A day that made spirits beam!",
                ],
                WeatherCondition.RAIN: [
                    f"The rain in {city_name} came down, / Making puddles all over town, / Each drop was a gift, / Giving spirits a lift, / No reason at all for a frown!",
                    f"There once was some rain from above, / That {city_name} welcomed with love, / It pattered and played, / A wet serenade, / As gentle as song of a dove!",
                ],
                WeatherCondition.SNOW: [
                    f"The snow over {city_name} fell white, / Creating a magical sight, / Each flake was so pure, / So gentle and sure, / A winter wonderland delight!",
                    f"In {city_name} the snowflakes dance, / Giving winter a fighting chance, / They swirl and they play, / All throughout the day, / In nature's white winter romance!",
                ],
            }

            templates = limericks.get(condition, limericks[WeatherCondition.CLEAR])
            limerick_text = random.choice(templates)
            self.logger.info(
                f"Generated template limerick for {weather.location.display_name}"
            )

        poem = WeatherPoem(
            text=limerick_text,
            poem_type="limerick",
            weather_condition=condition,
            temperature_range=temp_range,
        )

        return poem

    def _create_temperature_haiku(
        self, temp_descriptor: str, condition: WeatherCondition
    ) -> List[str]:
        """Create temperature-focused haiku."""
        temp_haikus = {
            "arctic": [
                "Arctic air descends / Breathing out white puffs of frost / Winter's icy grip",
                "Frozen world around / Each breath forms crystal vapor / Arctic beauty reigns",
            ],
            "crisp": [
                "Crisp morning air waits / Invigorating and fresh / Nature's wake-up call",
                "Cool crisp breeze blows by / Refreshing the weary soul / Perfect temperature",
            ],
            "pleasant": [
                "Pleasant breeze flows through / Comfortable and just right / Perfect day for all",
                "Gentle pleasant air / Neither too hot nor too cold / Nature's sweet balance",
            ],
            "scorching": [
                "Scorching sun beats down / Heat waves shimmer in the air / Summer's fiery breath",
                "Blazing heat surrounds / Seeking shade becomes a must / Hot day intensifies",
            ],
        }
        return temp_haikus.get(temp_descriptor, [])

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """
        Call Gemini Pro API to generate creative content.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Generated text or None if API call fails
        """
        if not self.gemini_enabled:
            return None

        try:
            import google.generativeai as genai

            # Configure Gemini
            genai.configure(api_key=self.config.gemini_api_key)
            model = genai.GenerativeModel(self.config.gemini_model)

            # Create generation config
            generation_config = genai.types.GenerationConfig(
                temperature=self.config.ai_temperature,
                max_output_tokens=self.config.ai_max_tokens,
            )

            # Enhanced system prompt for weather poetry
            enhanced_prompt = f"""You are a creative weather poet who writes beautiful, unique poetry about weather conditions. Your poems should be weather-themed, creative, and capture the essence of the moment.

{prompt}"""

            response = model.generate_content(
                enhanced_prompt, generation_config=generation_config
            )

            if response.text:
                return response.text.strip()
            else:
                self.logger.warning("Gemini API returned empty response")

        except ImportError:
            self.logger.error(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            )
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")

        return None

    def _call_openai_api(self, prompt: str) -> Optional[str]:
        """
        Call OpenAI API to generate creative content (fallback).

        Args:
            prompt: The prompt to send to OpenAI

        Returns:
            Generated text or None if API call fails
        """
        if not self.openai_enabled:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.config.openai_api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.config.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a creative weather poet who writes beautiful, unique poetry about weather conditions. Your poems should be weather-themed, creative, and capture the essence of the moment.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": self.config.ai_max_tokens,
                "temperature": self.config.ai_temperature,
                "top_p": 1,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.3,
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
            else:
                self.logger.warning(
                    f"OpenAI API request failed with status {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")

        return None

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """
        Call AI API with Gemini Pro as primary and OpenAI as fallback.

        Args:
            prompt: The prompt to send to the AI

        Returns:
            Generated text or None if all API calls fail
        """
        if not self.ai_enabled:
            return None

        # Try Gemini Pro first (primary)
        if self.gemini_enabled:
            result = self._call_gemini_api(prompt)
            if result:
                self.logger.debug("Successfully generated content using Gemini Pro")
                return result
            else:
                self.logger.warning("Gemini Pro API failed, trying OpenAI fallback")

        # Fallback to OpenAI if Gemini fails or is not available
        if self.openai_enabled:
            result = self._call_openai_api(prompt)
            if result:
                self.logger.debug(
                    "Successfully generated content using OpenAI (fallback)"
                )
                return result
            else:
                self.logger.warning("OpenAI API also failed")

        self.logger.error("All AI APIs failed to generate content")
        return None

    def _generate_ai_haiku(self, weather: CurrentWeather) -> Optional[str]:
        """Generate AI-powered haiku about the weather."""
        temp_celsius = weather.temperature.to_celsius()
        condition_name = weather.condition.name.lower().replace("_", " ")
        location = weather.location.name

        prompt = f"""Write a beautiful haiku (5-7-5 syllable pattern) about the current weather in {location}.

Weather details:
- Condition: {condition_name}
- Temperature: {temp_celsius: .1f}°C
- Description: {weather.description}
- Location: {location}

The haiku should capture the mood and feeling of this weather. Make it evocative and poetic.
Only return the haiku, nothing else."""

        return self._call_ai_api(prompt)

    def _generate_ai_limerick(self, weather: CurrentWeather) -> Optional[str]:
        """Generate AI-powered limerick about the weather."""
        temp_celsius = weather.temperature.to_celsius()
        condition_name = weather.condition.name.lower().replace("_", " ")
        location = weather.location.name

        prompt = f"""Write a playful limerick (AABBA rhyme scheme) about the current weather in {location}.

Weather details:
- Condition: {condition_name}
- Temperature: {temp_celsius: .1f}°C
- Description: {weather.description}
- Location: {location}

The limerick should be light-hearted, fun, and weather-themed. Make it clever and entertaining.
Only return the limerick, nothing else."""

        return self._call_ai_api(prompt)

    def _generate_ai_phrase(self, weather: CurrentWeather) -> Optional[str]:
        """Generate AI-powered creative phrase about the weather."""
        temp_celsius = weather.temperature.to_celsius()
        condition_name = weather.condition.name.lower().replace("_", " ")
        location = weather.location.name

        prompt = f"""Write a creative, fun phrase or short poem about the current weather in {location}.

Weather details:
- Condition: {condition_name}
- Temperature: {temp_celsius: .1f}°C
- Description: {weather.description}
- Location: {location}

The phrase should be engaging, unique, and capture the essence of this weather moment.
It can be poetic, whimsical, or playful. Keep it to 1-2 sentences.
Only return the phrase, nothing else."""

        return self._call_ai_api(prompt)

    def generate_weather_poetry(
        self, weather: CurrentWeather, poetry_type: str = "random"
    ) -> WeatherPoem:
        """
        Generate weather poetry of specified type or random.

        Args:
            weather: Current weather data
            poetry_type: Type of poetry ("haiku", "phrase", "limerick", "random")

        Returns:
            WeatherPoem object
        """
        if poetry_type == "random":
            poetry_type = random.choice(["haiku", "phrase", "limerick"])

        if poetry_type == "haiku":
            return self.generate_haiku(weather)
        elif poetry_type == "phrase":
            return self.generate_fun_phrase(weather)
        elif poetry_type == "limerick":
            return self.generate_limerick(weather)
        else:
            # Default to fun phrase if unknown type
            return self.generate_fun_phrase(weather)

    def create_poetry_collection(
        self, weather: CurrentWeather, count: int = 3
    ) -> List[WeatherPoem]:
        """
        Create a collection of different poetry types for the weather.

        Args:
            weather: Current weather data
            count: Number of poems to generate

        Returns:
            List of WeatherPoem objects
        """
        poems = []
        types = ["haiku", "phrase", "limerick"]

        for i in range(min(count, len(types))):
            poem = self.generate_weather_poetry(weather, types[i])
            poems.append(poem)

        # If more poems requested, generate random ones
        while len(poems) < count:
            poem = self.generate_weather_poetry(weather, "random")
            poems.append(poem)

        self.logger.info(
            f"Generated {len(poems)} poems for {weather.location.display_name}"
        )
        return poems

    def format_poetry_display(self, poem: WeatherPoem) -> str:
        """
        Format a poem for display with appropriate styling.

        Args:
            poem: WeatherPoem to format

        Returns:
            Formatted string for display
        """
        lines = []

        if poem.poem_type == "haiku":
            lines.append("🌸 Weather Haiku")
            lines.append("-" * 20)
            lines.append(poem.formatted_text)
        elif poem.poem_type == "phrase":
            lines.append("💭 Weather Wisdom")
            lines.append("-" * 20)
            lines.append(poem.text)
        elif poem.poem_type == "limerick":
            lines.append("🎵 Weather Limerick")
            lines.append("-" * 20)
            lines.append(poem.text)

        return "\n".join(lines)
