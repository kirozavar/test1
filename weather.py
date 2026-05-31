#!/usr/bin/env python3
"""Weather app using Open-Meteo (free, no API key needed)."""

import sys
import urllib.request
import urllib.parse
import json


WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}

WIND_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


def geocode(city: str) -> tuple[str, float, float, str]:
    """Return (name, lat, lon, country) for a city name."""
    params = urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"})
    data = fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?{params}")
    results = data.get("results")
    if not results:
        raise ValueError(f"City not found: {city!r}")
    r = results[0]
    return r["name"], r["latitude"], r["longitude"], r.get("country", "")


def get_weather(lat: float, lon: float) -> dict:
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "weather_code", "wind_speed_10m", "wind_direction_10m",
        ]),
        "daily": ",".join([
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "wind_speed_10m_max",
        ]),
        "timezone": "auto",
        "forecast_days": 5,
    })
    return fetch_json(f"https://api.open-meteo.com/v1/forecast?{params}")


def wind_dir(degrees: float) -> str:
    return WIND_DIRS[round(degrees / 45) % 8]


def condition(code: int) -> str:
    return WMO_CODES.get(code, f"Unknown ({code})")


def bar(temp_min: float, temp_max: float, abs_min: float, abs_max: float, width: int = 20) -> str:
    span = abs_max - abs_min or 1
    lo = int((temp_min - abs_min) / span * width)
    hi = int((temp_max - abs_min) / span * width)
    return " " * lo + "=" * max(hi - lo, 1) + " " * (width - hi)


def display(city: str, country: str, data: dict) -> None:
    cur = data["current"]
    daily = data["daily"]

    t = cur["temperature_2m"]
    feels = cur["apparent_temperature"]
    humidity = cur["relative_humidity_2m"]
    precip = cur["precipitation"]
    ws = cur["wind_speed_10m"]
    wd = cur["wind_direction_10m"]
    code = cur["weather_code"]

    location = f"{city}, {country}" if country else city
    print(f"\n{'─' * 50}")
    print(f"  {location}")
    print(f"{'─' * 50}")
    print(f"  Condition  : {condition(code)}")
    print(f"  Temp       : {t:.1f}°C  (feels like {feels:.1f}°C)")
    print(f"  Humidity   : {humidity}%")
    print(f"  Wind       : {ws:.1f} km/h {wind_dir(wd)}")
    print(f"  Precip     : {precip:.1f} mm")

    print(f"\n  5-Day Forecast")
    print(f"  {'Date':<12} {'Lo':>5} {'Hi':>5}  {'Bar':<22} Condition")
    print(f"  {'─'*12} {'─'*5} {'─'*5}  {'─'*22} {'─'*20}")

    maxes = daily["temperature_2m_max"]
    mins = daily["temperature_2m_min"]
    abs_min = min(mins)
    abs_max = max(maxes)

    for i, date in enumerate(daily["time"]):
        lo, hi = mins[i], maxes[i]
        b = bar(lo, hi, abs_min, abs_max)
        c = condition(daily["weather_code"][i])
        print(f"  {date:<12} {lo:>4.1f} {hi:>4.1f}  [{b}] {c}")

    print(f"{'─' * 50}\n")


def main() -> None:
    city = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not city:
        city = input("Enter city name: ").strip()
    if not city:
        print("No city provided.", file=sys.stderr)
        sys.exit(1)

    try:
        name, lat, lon, country = geocode(city)
        data = get_weather(lat, lon)
        display(name, country, data)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
