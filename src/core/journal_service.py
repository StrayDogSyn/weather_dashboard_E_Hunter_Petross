"""
Weather Journal Service for Weather Dashboard.

This service provides functionality to create and manage weather journal entries.
"""

import json
import logging
import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ..interfaces.weather_interfaces import IDataStorage
from ..models.capstone_models import JournalEntry, MoodType
from ..models.weather_models import CurrentWeather


class WeatherJournalService:
    """Service for managing weather journal entries."""

    def __init__(self, storage: IDataStorage):
        """Initialize the journal service."""
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        self.journal_file = "journal_entries.json"

        # Load existing entries
        self.entries = self._load_entries()

    def _load_entries(self) -> List[JournalEntry]:
        """Load journal entries from storage."""
        try:
            data = self.storage.load_data(self.journal_file)
            if not data or "entries" not in data:
                return []

            entries = []
            for entry_data in data["entries"]:
                try:
                    date_str = entry_data.get("date", "")
                    created_at_str = entry_data.get(
                        "created_at", datetime.now().isoformat()
                    )

                    # Safely handle created_at parsing
                    created_at = datetime.now()
                    if created_at_str and created_at_str.strip():
                        try:
                            created_at = datetime.fromisoformat(created_at_str)
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Could not parse created_at '{created_at_str}': {e}, using current time")
                            created_at = datetime.now()

                    entry = JournalEntry(
                        date=self._validate_date(date_str),
                        location=entry_data.get("location", ""),
                        weather_summary=entry_data.get("weather_summary", ""),
                        temperature=float(entry_data.get("temperature", 0.0)),
                        condition=entry_data.get("condition", ""),
                        mood=self._validate_mood(entry_data.get("mood", "neutral")),
                        notes=entry_data.get("notes", ""),
                        activities=entry_data.get("activities", []),
                        created_at=created_at,
                    )
                except (ValueError, TypeError, AttributeError) as e:
                    self.logger.error(f"Error parsing journal entry: {e}")
                    continue
                entries.append(entry)

            self.logger.info(f"Loaded {len(entries)} journal entries")
            return entries

        except Exception as e:
            self.logger.error(f"Error loading journal entries: {e}")
            return []

    def _save_entries(self) -> bool:
        """Save journal entries to storage."""
        try:
            data = {"entries": [self._serialize_entry(entry) for entry in self.entries]}

            success = self.storage.save_data(data, self.journal_file)
            if success:
                self.logger.info(f"Saved {len(self.entries)} journal entries")
            else:
                self.logger.error("Failed to save journal entries")

            return success

        except Exception as e:
            self.logger.error(f"Error saving journal entries: {e}")
            return False

    def create_entry(
        self,
        weather: CurrentWeather,
        mood: MoodType,
        notes: str,
        activities: Optional[List[str]] = None,
    ) -> JournalEntry:
        """
        Create a new journal entry for today.

        Args:
            weather: Current weather data
            mood: User's mood
            notes: User's notes
            activities: List of activities done today

        Returns:
            Created JournalEntry
        """
        if activities is None:
            activities = []

        entry = JournalEntry(
            date=date.today(),
            location=weather.location.display_name,
            weather_summary=weather.description.title(),
            temperature=weather.temperature.to_celsius(),
            condition=weather.description,
            mood=mood,
            notes=notes,
            activities=activities,
        )

        # Check if entry for today already exists
        today_entry = self.get_entry_by_date(date.today())
        if today_entry:
            # Update existing entry
            self.entries.remove(today_entry)

        self.entries.append(entry)
        self._save_entries()

        self.logger.info(f"Created journal entry for {entry.formatted_date}")
        return entry

    def get_entry_by_date(self, entry_date: date) -> Optional[JournalEntry]:
        """
        Get journal entry for a specific date.

        Args:
            entry_date: Date to search for

        Returns:
            JournalEntry or None if not found
        """
        for entry in self.entries:
            if entry.date == entry_date:
                return entry
        return None

    def get_recent_entries(self, limit: int = 10) -> List[JournalEntry]:
        """
        Get recent journal entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent JournalEntry objects
        """
        sorted_entries = sorted(self.entries, key=lambda e: e.date, reverse=True)
        return sorted_entries[:limit]

    def get_entries_by_mood(self, mood: MoodType) -> List[JournalEntry]:
        """
        Get all entries with a specific mood.

        Args:
            mood: Mood to filter by

        Returns:
            List of JournalEntry objects with the specified mood
        """
        return [entry for entry in self.entries if entry.mood == mood]

    def get_mood_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about mood patterns.

        Returns:
            Dictionary with mood statistics
        """
        if not self.entries:
            return {}

        mood_counts: Dict[str, int] = {}
        for entry in self.entries:
            mood_counts[entry.mood.value] = mood_counts.get(entry.mood.value, 0) + 1

        total_entries = len(self.entries)
        mood_percentages = {
            mood: (count / total_entries) * 100 for mood, count in mood_counts.items()
        }

        most_common_mood = max(mood_counts.items(), key=lambda x: x[1])

        return {
            "total_entries": total_entries,
            "mood_counts": mood_counts,
            "mood_percentages": mood_percentages,
            "most_common_mood": most_common_mood[0],
            "most_common_mood_count": most_common_mood[1],
        }

    def search_entries(self, query: str) -> List[JournalEntry]:
        """
        Search journal entries by text in notes or activities.

        Args:
            query: Search query

        Returns:
            List of matching JournalEntry objects
        """
        query = query.lower()
        matching_entries = []

        for entry in self.entries:
            # Search in notes
            if query in entry.notes.lower():
                matching_entries.append(entry)
                continue

            # Search in activities
            for activity in entry.activities:
                if query in activity.lower():
                    matching_entries.append(entry)
                    break

            # Search in location
            if query in entry.location.lower():
                matching_entries.append(entry)

        return matching_entries

    def delete_entry(self, entry_date: date) -> bool:
        """
        Delete a journal entry by date.

        Args:
            entry_date: Date of entry to delete

        Returns:
            True if deleted, False if not found
        """
        entry = self.get_entry_by_date(entry_date)
        if entry:
            self.entries.remove(entry)
            self._save_entries()
            self.logger.info(f"Deleted journal entry for {entry_date}")
            return True

        self.logger.warning(f"No journal entry found for {entry_date}")
        return False

    def export_entries_to_text(self, filename: Optional[str] = None) -> str:
        """
        Export all journal entries to a readable text format.

        Args:
            filename: Optional filename to save to

        Returns:
            Formatted text content
        """
        if not self.entries:
            return "No journal entries found."

        lines = []
        lines.append("Weather Journal Export")
        lines.append("=" * 50)
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Total entries: {len(self.entries)}")
        lines.append("")

        # Sort entries by date
        sorted_entries = sorted(self.entries, key=lambda e: e.date)

        for entry in sorted_entries:
            lines.append(f"Date: {entry.formatted_date}")
            lines.append(f"Location: {entry.location}")
            lines.append(
                f"Weather: {entry.weather_summary} ({entry.temperature:.1f}°C)"
            )
            lines.append(f"Mood: {entry.mood_emoji} {entry.mood.value.title()}")
            lines.append(f"Notes: {entry.notes}")

            if entry.activities:
                lines.append(f"Activities: {', '.join(entry.activities)}")

            lines.append("-" * 30)
            lines.append("")

        content = "\n".join(lines)

        # Save to file if filename provided
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.logger.info(f"Exported journal to {filename}")
            except Exception as e:
                self.logger.error(f"Error exporting to {filename}: {e}")

        return content

    def _validate_date(self, date_obj: Any) -> date:
        """
        Validate and convert date object.

        Args:
            date_obj: Date object or string to validate

        Returns:
            datetime.date object

        Raises:
            ValueError if date is invalid
        """
        if isinstance(date_obj, date):
            return date_obj
        elif isinstance(date_obj, datetime):
            return date_obj.date()
        elif isinstance(date_obj, str):
            # Handle empty strings gracefully
            if not date_obj or date_obj.strip() == "":
                return date.today()  # Return today's date for empty strings
            try:
                return datetime.fromisoformat(date_obj).date()
            except ValueError:
                # Try alternative date formats
                try:
                    return datetime.strptime(date_obj, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        return datetime.strptime(date_obj, "%m/%d/%Y").date()
                    except ValueError:
                        self.logger.warning(f"Could not parse date '{date_obj}', using today's date")
                        return date.today()
        else:
            self.logger.warning(f"Invalid date type: {type(date_obj)}, using today's date")
            return date.today()

    def _validate_mood(self, mood_value: Any) -> MoodType:
        """
        Validate and convert mood value.

        Args:
            mood_value: Mood value to validate

        Returns:
            MoodType enum value
        """
        if isinstance(mood_value, MoodType):
            return mood_value
        elif isinstance(mood_value, str):
            # Handle common mood variations
            mood_lower = mood_value.lower().strip()
            mood_mapping = {
                'happy': MoodType.HAPPY,
                'confident': MoodType.MOTIVATED,
                'excited': MoodType.EXCITED,
                'calm': MoodType.PEACEFUL,
                'relaxed': MoodType.RELAXED,
                'sad': MoodType.SAD,
                'worried': MoodType.ANXIOUS,
                'stressed': MoodType.ANXIOUS,
                'angry': MoodType.ANXIOUS,  # Map to anxious as closest match
                'frustrated': MoodType.ANXIOUS,  # Map to anxious as closest match
                'neutral': MoodType.CONTENT,  # Map neutral to content
            }
            
            # Try direct mapping first
            if mood_lower in mood_mapping:
                return mood_mapping[mood_lower]
            
            # Try to match with existing MoodType values
            try:
                return MoodType(mood_lower)
            except ValueError:
                # Try to find a close match
                for mood_type in MoodType:
                    if mood_type.value.lower() == mood_lower:
                        return mood_type
                
                self.logger.warning(f"Could not parse mood '{mood_value}', using content")
                return MoodType.CONTENT
        else:
            self.logger.warning(f"Invalid mood type: {type(mood_value)}, using content")
            return MoodType.CONTENT

    def _serialize_entry(self, entry: JournalEntry) -> Dict[str, Any]:
        """
        Safely serialize a journal entry to dictionary.

        Args:
            entry: JournalEntry to serialize

        Returns:
            Dictionary representation of the entry
        """
        try:
            # Safely handle date serialization
            date_str = ""
            if entry.date:
                try:
                    date_str = entry.date.isoformat()
                except (AttributeError, ValueError) as e:
                    self.logger.warning(f"Error serializing date: {e}, using today's date")
                    date_str = date.today().isoformat()
            else:
                date_str = date.today().isoformat()
            
            # Safely handle created_at serialization
            created_at_str = ""
            if entry.created_at:
                try:
                    created_at_str = entry.created_at.isoformat()
                except (AttributeError, ValueError) as e:
                    self.logger.warning(f"Error serializing created_at: {e}, using current time")
                    created_at_str = datetime.now().isoformat()
            else:
                created_at_str = datetime.now().isoformat()

            return {
                "date": date_str,
                "location": entry.location or "",
                "weather_summary": entry.weather_summary or "",
                "temperature": (
                    entry.temperature if entry.temperature is not None else 0.0
                ),
                "condition": entry.condition or "",
                "mood": entry.mood.value if entry.mood else "neutral",
                "notes": entry.notes or "",
                "activities": entry.activities or [],
                "created_at": created_at_str,
            }
        except Exception as e:
            self.logger.error(f"Error serializing entry: {e}")
            raise
