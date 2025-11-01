import pandas as pd
from core.location_resolver import resolve_location
from core.bmkg_api import get_bmkg_forecast
from core.openmeteo_api import get_openmeteo_forecast
from core.formatter import format_forecast_output

def get_fusion_forecast(query: str):
    """
    Fusion antara BMKG + Open-Meteo berdasarkan nama wilayah/desa.
    """
    loc = resolve_location(query)
    lat, lon = loc.get("latitude"), loc.get("longitude")

    if not lat or not lon:
        return {"error": f"Koordinat tidak ditemukan untuk '{query}'."}

    try:
        bmkg_data = get_bmkg_forecast(lat, lon)
    except Exception as e:
        bmkg_data = {"error": f"Gagal ambil data BMKG: {e}"}

    try:
        openmeteo_data = get_openmeteo_forecast(lat, lon)
    except Exception as e:
        openmeteo_data = {"error": f"Gagal ambil data Open-Meteo: {e}"}

    fusion_result = {
        "lokasi": loc,
        "bmkg": bmkg_data,
        "openmeteo": openmeteo_data
    }

    fusion_result["ringkasan"] = format_forecast_output(fusion_result)
    return fusion_result
