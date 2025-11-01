import requests

def get_openmeteo(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,relative_humidity_2m,"
        f"cloudcover,wind_speed_10m&timezone=Asia%2FJakarta"
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None
