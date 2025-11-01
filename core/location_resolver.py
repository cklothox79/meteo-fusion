import pandas as pd
from pathlib import Path

DATA_CSV = Path(__file__).resolve().parents[1] / "data" / "Village_LongLat_Approx.csv"

class LocationNotFound(Exception):
    pass

def load_village_csv(path=DATA_CSV):
    df = pd.read_csv(path, dtype=str)
    # Expect columns: name, lat, lon (if different update accordingly)
    # Normalize columns
    cols_lower = [c.lower() for c in df.columns]
    mapping = {}
    if "name" in cols_lower:
        mapping[cols_lower.index("name")] = "name"
    else:
        # try common alternatives
        for c in df.columns:
            if "village" in c.lower() or "desa" in c.lower() or "name" in c.lower():
                mapping[0] = c
                break
    # Try lat/lon columns
    lat_col = None
    lon_col = None
    for c in df.columns:
        if "lat" == c.lower() or "latitude" in c.lower():
            lat_col = c
        if "lon" == c.lower() or "longitude" in c.lower():
            lon_col = c
    if lat_col is None or lon_col is None:
        raise ValueError("CSV must contain latitude and longitude columns (named like lat/lon/latitude/longitude).")
    # rename to standard
    rename_map = {}
    # find name column index found earlier
    for c in df.columns:
        if c.lower() in ("name", "village", "desa", "kecamatan", "kota", "kabupaten"):
            rename_map[c] = "name"
            break
    rename_map[lat_col] = "lat"
    rename_map[lon_col] = "lon"
    df = df.rename(columns=rename_map)
    # ensure lat/lon numeric
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    df["name_search"] = df["name"].str.lower()
    return df

_village_df_cache = None

def find_location(query):
    """
    Return (name, lat, lon) for the best match. Raises LocationNotFound if none.
    Uses case-insensitive partial match.
    """
    global _village_df_cache
    if _village_df_cache is None:
        _village_df_cache = load_village_csv()
    df = _village_df_cache
    q = query.strip().lower()
    # Exact match first
    exact = df[df["name_search"] == q]
    if not exact.empty:
        row = exact.iloc[0]
        return row["name"], float(row["lat"]), float(row["lon"])
    # Partial contains
    contains = df[df["name_search"].str.contains(q, na=False)]
    if not contains.empty:
        row = contains.iloc[0]
        return row["name"], float(row["lat"]), float(row["lon"])
    # Fuzzy fallback: startswith
    starts = df[df["name_search"].str.startswith(q)]
    if not starts.empty:
        row = starts.iloc[0]
        return row["name"], float(row["lat"]), float(row["lon"])
    raise LocationNotFound(f"Lokasi '{query}' tidak ditemukan di CSV data.")
