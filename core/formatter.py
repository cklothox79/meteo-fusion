def format_output(nama, lat, lon, data):
    text = f"📍 {nama}\n"
    text += f"Koordinat: {lat}, {lon}\n\n"
    text += f"🌦️ Cuaca: {data.get('cuaca', 'Belum tersedia')}\n"
    text += f"🌡️ Suhu BMKG: {data.get('suhu_min', '?')}–{data.get('suhu_max', '?')}°C\n"
    text += f"🌡️ Suhu Open-Meteo: {data.get('suhu_openmeteo', ['?'])[0]}°C\n"
    text += f"💧 Hujan (mm): {data.get('hujan', ['?'])[0]}"
    return text
