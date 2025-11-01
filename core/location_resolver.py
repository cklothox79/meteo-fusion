# core/location_resolver.py
import pandas as pd
from core.geocode_utils import get_coordinates

def resolve_location(query: str):
    # Coba cari di file CSV lokal
    url = "https://raw.githubusercontent.com/cklothoz79/kusuma-converter/main/kode_wilayah.csv"
    df = pd.read_csv(url)
    result = df[df['nama'].str.contains(query, case=False, na=False)]

    if not result.empty:
        row = result.iloc[0]
        return {
            "adm1": row.get("provinsi", ""),
            "adm2": row.get("kabupaten", ""),
            "adm3": row.get("kecamatan", ""),
            "adm4": row.get("desa", ""),
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", "")
        }
    
    # Jika tidak ditemukan di CSV, fallback ke API geocode
    lat, lon = get_coordinates(query)
    return {
        "adm1": "",
        "adm2": "",
        "adm3": "",
        "adm4": query,
        "latitude": lat,
        "longitude": lon
    }
