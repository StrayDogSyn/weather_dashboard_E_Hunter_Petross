"""Location detection service using browser-based geolocation and IP fallback."""

import json
import logging
import subprocess
import sys
from typing import Optional, Tuple

import requests


class LocationDetectionService:
    """Service for detecting user's current location."""

    def __init__(self):
        """Initialize the location detection service."""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "WeatherDashboard/1.0"})

    def get_current_location(self) -> Optional[Tuple[float, float, str]]:
        """
        Get current location coordinates and city name.

        Returns:
            Tuple of (latitude, longitude, city_name) or None if failed
        """
        # Try IP-based geolocation first as it's most reliable
        location = self._get_location_by_ip()
        if location:
            return location

        # If IP geolocation fails, try browser geolocation
        location = self._get_location_by_browser()
        if location:
            return location

        logging.warning("All location detection methods failed")
        return None

    def _get_location_by_ip(self) -> Optional[Tuple[float, float, str]]:
        """Get location using IP-based geolocation."""
        try:
            # Using ipapi.co for IP geolocation (free tier available)
            response = self.session.get("http://ipapi.co/json/", timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("latitude") and data.get("longitude"):
                latitude = float(data["latitude"])
                longitude = float(data["longitude"])
                city = data.get("city", "Unknown City")

                logging.info(f"IP geolocation found: {city} ({latitude}, {longitude})")
                return latitude, longitude, city

        except Exception as e:
            logging.error(f"IP geolocation failed: {e}")

        return None

    def _get_location_by_browser(self) -> Optional[Tuple[float, float, str]]:
        """Get location using browser geolocation API via a simple HTML page."""
        try:
            # Create a simple HTML file that uses browser geolocation
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Location Detection</title>
</head>
<body>
    <div id="result">Getting location...</div>
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            } else {
                document.getElementById("result").innerHTML = "ERROR: Geolocation not supported";
            }
        }
        
        function showPosition(position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;
            document.getElementById("result").innerHTML = "SUCCESS:" + lat + "," + lon;
        }
        
        function showError(error) {
            document.getElementById("result").innerHTML = "ERROR: " + error.message;
        }
        
        getLocation();
    </script>
</body>
</html>
            """


            # Write HTML to temp file
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as f:
                f.write(html_content)
                html_file = f.name

            try:
                # Open browser to get location (this would require user interaction)
                # For now, we'll skip this method as it's complex in a desktop app
                logging.info("Browser geolocation requires user interaction - skipping")
                return None
            finally:
                # Clean up temp file
                try:
                    os.unlink(html_file)
                except Exception:
                    pass

        except Exception as e:
            logging.error(f"Browser geolocation failed: {e}")

        return None

    def get_city_name_from_coordinates(self, latitude: float, longitude: float) -> str:
        """
        Get city name from coordinates using reverse geocoding.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            City name or 'Unknown Location'
        """
        try:
            # Use OpenStreetMap Nominatim for reverse geocoding (free)
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 10,
                "addressdetails": 1,
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract city name from address components
            address = data.get("address", {})
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
                or "Unknown Location"
            )

            return city

        except Exception as e:
            logging.error(f"Reverse geocoding failed: {e}")
            return "Unknown Location"
