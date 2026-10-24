import requests

def get_coordinates(location_name: str):
    """Fetches latitude and longitude for a given location using Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    # Nominatim requires a User-Agent header to avoid rate limits
    headers = {
        "User-Agent": "GeoAI-Hackathon-App/1.0"
    }
    params = {
        "q": location_name,
        "format": "json",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return {
            "lat": float(data["lat"]), 
            "lon": float(data["lon"]), 
            "display_name": data["display_name"]
        }
    return None

def get_weather(lat: float, lon: float):
    """Fetches live weather data using Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    return None