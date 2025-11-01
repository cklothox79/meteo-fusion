import requests

def get_openmeteo_forecast(lat, lon):
    """
    Mengambil prakiraan cuaca dari Open-Meteo API.
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,weathercode&timezone=Asia/Jakarta"
        )
        resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            return {"status": "error", "message": f"Open-Meteo API error {resp.status_code}"}

        data = resp.json()
        return {
            "sumber": "Open-Meteo",
            "koordinat": {"lat": lat, "lon": lon},
            "data": data
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
