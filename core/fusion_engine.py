def fuse_data(bmkg_data, openmeteo_data):
    """Gabungkan data dari BMKG & Open-Meteo"""
    fused = {}

    if bmkg_data:
        fused["cuaca"] = bmkg_data.get("weather", "Tidak tersedia")
        fused["suhu_min"] = bmkg_data.get("t_min")
        fused["suhu_max"] = bmkg_data.get("t_max")

    if openmeteo_data:
        hourly = openmeteo_data.get("hourly", {})
        fused["suhu_openmeteo"] = hourly.get("temperature_2m", [None])[:5]
        fused["hujan"] = hourly.get("precipitation", [None])[:5]
    
    return fused
