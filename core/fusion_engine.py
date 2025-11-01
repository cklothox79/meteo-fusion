# core/fusion_engine.py
import pandas as pd
from core.location_resolver import resolve_location
from core.bmkg_api import get_bmkg_forecast
from core.openmeteo_api import get_openmeteo_forecast
from core.formatter import format_forecast_output

def get_fusion_forecast(query: str):
    """
    Menggabungkan hasil prakiraan dari BMKG dan Open-Meteo
    berdasarkan input nama wilayah atau desa.
    """

    # 1️⃣ Terjemahkan nama wilayah ke koordinat & ADM
    loc = resolve_location(query)
    lat, lon = loc.get("latitude"), loc.get("longitude")

    if not lat or not lon:
        return {"error": f"Koordinat tidak ditemukan untuk '{query}'."}

    # 2️⃣ Ambil data prakiraan dari BMKG dan Open-Meteo
    try:
        bmkg_data = get_bmkg_forecast(lat, lon)
    except Exception as e:
        bmkg_data = {"error": f"Gagal ambil data BMKG: {e}"}

    try:
        openmeteo_data = get_openmeteo_forecast(lat, lon)
    except Exception as e:
        openmeteo_data = {"error": f"Gagal ambil data Open-Meteo: {e}"}

    # 3️⃣ Gabungkan hasil dengan format yang rapi
    fusion_result = {
        "lokasi": loc,
        "bmkg": bmkg_data,
        "openmeteo": openmeteo_data
    }

    # 4️⃣ Format hasil akhir agar mudah dibaca
    fusion_result["ringkasan"] = format_forecast_output(fusion_result)

    return fusion_result


if __name__ == "__main__":
    # Contoh uji mandiri (opsional)
    query = "Simogirang"
    hasil = get_fusion_forecast(query)
    print(pd.Series(hasil))
