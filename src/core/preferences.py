import threading
from typing import Any
from typing import Callable
from typing import Dict


class PreferenceManager:
    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_instance():
        with PreferenceManager._lock:
            if PreferenceManager._instance is None:
                PreferenceManager._instance = PreferenceManager()
            return PreferenceManager._instance

    def __init__(self):
        if PreferenceManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.schema = self._default_schema()
        self.preferences = self._load_preferences()
        self.observers = []

    def _default_schema(self) -> Dict[str, Dict[str, Any]]:
        # Example schema; expand as needed
        return {
            "theme": {"type": str, "default": "light", "allowed": ["light", "dark"]},
            "auto_update": {"type": bool, "default": True},
            "refresh_interval": {"type": int, "default": 15, "min": 5, "max": 60},
            "schema_version": {"type": int, "default": 1},
        }

    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from storage.

        Returns:
            Dictionary of preference values
        """
        return {k: v["default"] for k, v in self.schema.items()}

    def save_preferences(self):
        """Save preferences to storage."""
        # Implementation pending
        pass

    def set(self, key: str, value: Any):
        """Set a preference value.

        Args:
            key: Preference key
            value: New value
        """
        # Implementation pending
        pass

    def get(self, key: str) -> Any:
        return self.preferences.get(key, self.schema[key]["default"])

    def add_observer(self, callback: Callable[[Dict[str, Any]], None]):
        self.observers.append(callback)

    def notify_observers(self):
        for cb in self.observers:
            cb(self.preferences)
