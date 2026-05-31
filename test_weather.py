"""Tests for weather.py using mocked HTTP responses."""

import io
import sys
import unittest
from unittest.mock import patch

import weather


MOCK_GEO = {
    "results": [{"name": "London", "latitude": 51.5, "longitude": -0.1, "country": "United Kingdom"}]
}

MOCK_WEATHER = {
    "current": {
        "temperature_2m": 15.2,
        "apparent_temperature": 13.5,
        "relative_humidity_2m": 72,
        "precipitation": 0.0,
        "weather_code": 2,
        "wind_speed_10m": 18.4,
        "wind_direction_10m": 225,
    },
    "daily": {
        "time": ["2026-05-31", "2026-06-01", "2026-06-02", "2026-06-03", "2026-06-04"],
        "weather_code": [2, 61, 63, 1, 0],
        "temperature_2m_max": [17.0, 14.5, 12.0, 16.0, 19.0],
        "temperature_2m_min": [10.0, 9.5, 8.0, 11.0, 12.0],
        "precipitation_sum": [0.0, 3.2, 8.5, 0.0, 0.0],
        "wind_speed_10m_max": [20.0, 30.0, 25.0, 15.0, 12.0],
    },
}


class TestWeatherLogic(unittest.TestCase):

    def test_condition_known_code(self):
        self.assertEqual(weather.condition(0), "Clear sky")
        self.assertEqual(weather.condition(61), "Slight rain")
        self.assertEqual(weather.condition(95), "Thunderstorm")

    def test_condition_unknown_code(self):
        self.assertIn("99999", weather.condition(99999))

    def test_wind_dir(self):
        self.assertEqual(weather.wind_dir(0), "N")
        self.assertEqual(weather.wind_dir(90), "E")
        self.assertEqual(weather.wind_dir(180), "S")
        self.assertEqual(weather.wind_dir(270), "W")
        self.assertEqual(weather.wind_dir(225), "SW")

    def test_bar_length(self):
        b = weather.bar(10, 20, 0, 30)
        self.assertEqual(len(b), 20)

    def test_bar_full_range(self):
        b = weather.bar(0, 30, 0, 30)
        self.assertIn("=", b)

    def test_geocode(self):
        with patch("weather.fetch_json", return_value=MOCK_GEO):
            name, lat, lon, country = weather.geocode("London")
        self.assertEqual(name, "London")
        self.assertAlmostEqual(lat, 51.5)
        self.assertEqual(country, "United Kingdom")

    def test_geocode_not_found(self):
        with patch("weather.fetch_json", return_value={"results": []}):
            with self.assertRaises(ValueError):
                weather.geocode("Nonexistent City XYZ")

    def test_display_output(self):
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            weather.display("London", "United Kingdom", MOCK_WEATHER)
        output = captured.getvalue()
        self.assertIn("London", output)
        self.assertIn("15.2", output)
        self.assertIn("Partly cloudy", output)
        self.assertIn("2026-05-31", output)
        self.assertIn("2026-06-04", output)

    def test_main_with_arg(self):
        with patch("weather.geocode", return_value=("London", 51.5, -0.1, "United Kingdom")), \
             patch("weather.get_weather", return_value=MOCK_WEATHER), \
             patch("sys.argv", ["weather.py", "London"]):
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                weather.main()
        self.assertIn("London", captured.getvalue())

    def test_main_no_city_exits(self):
        with patch("sys.argv", ["weather.py"]), \
             patch("builtins.input", return_value=""):
            with self.assertRaises(SystemExit):
                weather.main()


if __name__ == "__main__":
    unittest.main()
