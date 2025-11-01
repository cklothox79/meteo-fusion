import pandas as pd
from datetime import datetime, timedelta
from core.location_resolver import resolve_location
from core.bmkg_api import get_bmkg_forecast
from core.openmeteo_api import get_openmeteo_forecast
from core.formatter import format_forecast_output

def get_fusion_forecast(query: str):
    """
    Fusion antara BMKG + Open-Meteo berdasarkan nama wilayah/desa.
    Mengembalikan data lengkap termasuk DataFrame tren suhu dan hujan.
    """
    loc = resolve_location(query)
    lat, lon = loc.get("latitude"), loc.get("longitude")

    if not lat or not lon:
        return {"error": f"Koordinat tidak ditemukan untuk '{query}'."}

    # --- ambil data dari API
    try:
        bmkg_data = get_bmkg_forecast(lat, lon)
    except Exception as e:
        bmkg_data = {"error": f"Gagal ambil data BMKG: {e}"}

    try:
        openmeteo_data = get_openmeteo_forecast(lat, lon)
    except Exception as e:
        openmeteo_data = {"error": f"Gagal ambil data Open-Meteo: {e}"}

    # --- proses tren suhu & curah hujan dari Open-Meteo
    df_trend = None
    try:
        om = openmeteo_data.get("data", {})
        hourly = om.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        precs = hourly.get("precipitation", [])
        if times and temps:
            df_trend = pd.DataFrame({
                "time": pd.to_datetime(times),
                "temperature": temps,
                "precipitation": precs
            })
            # Hanya ambil 3 hari ke depan
            df_trend = df_trend[df_trend["time"] < datetime.now() + timedelta(days=3)]
    except Exception as e:
        print("Trend data parse error:", e)

    fusion_result = {
        "lokasi": loc,
        "bmkg": bmkg_data,
        "openmeteo": openmeteo_data,
        "trend": df_trend
    }

    fusion_result["ringkasan"] = format_forecast_output(fusion_result)
    return fusion_result
