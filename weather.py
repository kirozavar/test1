import urllib.request
import json
import sys

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search?name={}&count=1&language=en&format=json"
WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode"
    "&temperature_unit=celsius"
)

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
}


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def get_weather(city):
    geo = fetch_json(GEOCODE_URL.format(urllib.parse.quote(city)))
    if not geo.get("results"):
        print(f"City '{city}' not found.")
        return

    r = geo["results"][0]
    name, lat, lon = r["name"], r["latitude"], r["longitude"]
    country = r.get("country", "")

    data = fetch_json(WEATHER_URL.format(lat=lat, lon=lon))
    cur = data["current"]

    code = cur["weathercode"]
    condition = WMO_CODES.get(code, f"Code {code}")

    print(f"\nWeather in {name}, {country}")
    print(f"  Condition : {condition}")
    print(f"  Temp      : {cur['temperature_2m']} °C")
    print(f"  Humidity  : {cur['relative_humidity_2m']} %")
    print(f"  Wind      : {cur['wind_speed_10m']} km/h")


if __name__ == "__main__":
    import urllib.parse
    city = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "London"
    get_weather(city)
