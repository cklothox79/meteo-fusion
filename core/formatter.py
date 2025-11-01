def format_forecast_output(fusion_data):
    """
    Menyusun ringkasan prakiraan sederhana dari hasil fusion.
    """
    lokasi = fusion_data.get("lokasi", {})
    adm = f"{lokasi.get('adm4', '')}, {lokasi.get('adm3', '')}, {lokasi.get('adm2', '')}"

    bmkg = fusion_data.get("bmkg", {})
    openmeteo = fusion_data.get("openmeteo", {})

    summary = f"**Wilayah:** {adm}\n"

    if "error" in bmkg:
        summary += f"- BMKG: ❌ {bmkg['error']}\n"
    else:
        summary += f"- BMKG: ✅ Data tersedia\n"

    if "error" in openmeteo:
        summary += f"- Open-Meteo: ❌ {openmeteo['error']}\n"
    else:
        summary += f"- Open-Meteo: ✅ Data tersedia\n"

    summary += "\nGabungan kedua sumber memberikan gambaran cuaca aktual untuk wilayah terkait."
    return summary
