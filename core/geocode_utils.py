import pandas as pd
from geopy.geocoders import Nominatim

def get_location(nama_wilayah, csv_path="data/kode_wilayah_jatim.csv"):
    df = pd.read_csv(csv_path)
    match = df[df['nama'].str.lower().str.contains(nama_wilayah.lower(), na=False)]
    if not match.empty:
        row = match.iloc[0]
        return {
            "nama": row['nama'],
            "lat": row.get('lat'),
            "lon": row.get('lon')
        }

    geolocator = Nominatim(user_agent="meteo_fusion")
    loc = geolocator.geocode(f"{nama_wilayah}, Jawa Timur, Indonesia")
    if loc:
        return {"nama": nama_wilayah, "lat": loc.latitude, "lon": loc.longitude}
    else:
        return None
