import pandas as pd
import requests
from pathlib import Path

DATA_CSV = Path(__file__).resolve().parents[1] / "data" / "Village_LongLat_Approx.csv"

class LocationNotFound(Exception):
    pass

def load_village_csv(path=DATA_CSV):
    df = pd.read_csv(path, sep=None, engine="python", dtype=str)
    df = df.fillna("")
    # Normalisasi kolom
    cols_lower = [c.lower() for c in df.columns]
    if not any("name" in c or "desa" in c or "village" in c for c in cols_lower):
        # Tambah kolom "name" pakai kolom pertama
        df.columns = ["name"] + list(df.columns[1:])
    else:
        for c in df.columns:
            if "name" in c.lower() or "desa" in c.lower() or "village" in c.lower():
                df = df.rename(columns={c: "name"})
                break
    df["name_search"] = df["name"].str.lower().str.strip()
    return df

def geocode_name(name):
    """
    Cari koordinat pakai Open-Meteo geocoding API (gratis & tanpa API key)
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=1&language=id&format=json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        j = r.json()
        if "results" in j and len(j["results"]) > 0:
            res = j["results"][0]
            return float(res["latitude"]), float(res["longitude"])
    except Exception:
        pass
    return None, None

_village_df_cache = None

def find_location(query):
    """
    Return (name, lat, lon)
    """
    global _village_df_cache
    if _village_df_cache is None:
        _village_df_cache = load_village_csv()
    df = _village_df_cache
    q = query.strip().lower()
    matches = df[df["name_search"].str.contains(q, na=False)]
    if matches.empty:
        raise LocationNotFound(f"Lokasi '{query}' tidak ditemukan di CSV data.")
    row = matches.iloc[0]
    name = row["name"]
    lat = float(row["lat"]) if "lat" in row and pd.notna(row["lat"]) else None
    lon = float(row["lon"]) if "lon" in row and pd.notna(row["lon"]) else None
    # Jika lat/lon tidak ada, geocode
    if lat is None or lon is None:
        lat, lon = geocode_name(name)
        if lat is None or lon is None:
            raise LocationNotFound(f"Tidak bisa menentukan koordinat untuk '{name}'.")
    return name, lat, lon
