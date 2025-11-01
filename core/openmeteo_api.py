import requests
from datetime import datetime, timezone

OPENMETEO_BASE = "https://api.open-meteo.com/v1/forecast"

def fetch_openmeteo_forecast(lat, lon, timezone="auto"):
    """
    Returns a dict with:
      - source: "open-meteo"
      - fetched_at: ISO time
      - current_weather: {...}
      - daily: {...}
      - raw: raw API JSON
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": timezone
    }
    r = requests.get(OPENMETEO_BASE, params=params, timeout=15)
    r.raise_for_status()
    j = r.json()
    return {
        "source": "open-meteo",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "current_weather": j.get("current_weather"),
        "daily": j.get("daily"),
        "raw": j
    }
