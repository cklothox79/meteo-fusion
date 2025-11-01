#!/usr/bin/env python3
# generate_village_csv.py
"""
Buat Village_LongLat_Approx.csv untuk Provinsi Jawa Timur.
Pendekatan: ambil daftar desa/kecamatan/kabupaten dari sumber CSV publik (GitHub/BPS),
lalu assign koordinat perkiraan sebagai centroid kecamatan (geocoding),
dan ambil elevasi dari Open-Elevation (atau fallback).
Script menyimpan cache geocode & elevation agar aman diulang.
"""

import os
import time
import requests
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus

# ---------------------------
# CONFIG
# ---------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = DATA_DIR / "Village_LongLat_Approx.csv"
CACHE_GEOCODE = DATA_DIR / "cache_geocode_kec.csv"
CACHE_ELEV = DATA_DIR / "cache_elev.csv"

# Sumber daftar administratif (fallback ke repo GitHub yang umum)
# Jika kamu sudah punya daftar BPS lokal (.csv/.xlsx) ganti URL atau path di bawah.
# Note: ini mencoba beberapa sumber; jika gagal, ubah ke lokal kamu.
GITHUB_CSV = "https://raw.githubusercontent.com/guzfirdaus/Wilayah-Administrasi-Indonesia/master/Wilayah-Administrasi-Indonesia.csv"

# User-Agent header untuk polite requests
HEADERS = {"User-Agent": "meteo-fusion/1.0 (+https://github.com/cklothoz79/meteo-fusion)"}

# ---------------------------
# HELPERS: load administrative list
# ---------------------------
def load_admin_list():
    # Prefer local file if exists (daftar kode BPS yang kamu punya)
    local_candidates = [
        DATA_DIR / "daftar_kode_wilayah_jatim.csv",
        DATA_DIR / "master_desa_jatim.csv"
    ]
    for p in local_candidates:
        if p.exists():
            print(f"[load_admin_list] Menggunakan file lokal: {p}")
            return pd.read_csv(p, dtype=str)
    # else try GitHub raw
    try:
        print("[load_admin_list] Mengunduh daftar administrasi dari GitHub...")
        df = pd.read_csv(GITHUB_CSV, dtype=str)
        return df
    except Exception as e:
        raise RuntimeError(f"Gagal memuat daftar administratif: {e}")

# ---------------------------
# HELPERS: normalisasi kolom
# ---------------------------
def normalize_admin_df(df):
    # Try to find best-fit column names and normalize
    cols = [c.lower().strip() for c in df.columns]
    mapping = {}
    # heuristik nama kolom umum
    for c in df.columns:
        lc = c.lower()
        if "kode" in lc and "desa" in lc or "kode"==lc:
            mapping[c] = "kode_wilayah"
        elif any(x in lc for x in ["desa", "kelurahan", "village", "nm_desa", "nama"]):
            mapping[c] = "desa"
        elif "kecamatan" in lc or "kec" in lc:
            mapping[c] = "kecamatan"
        elif any(x in lc for x in ["kabupaten","kab","kota","regency","kab/kota"]):
            mapping[c] = "kabupaten"
        elif "provinsi" in lc or "province" in lc:
            mapping[c] = "provinsi"
        # latitude/longitude (if present)
        elif "lat" == lc or "latitude" in lc:
            mapping[c] = "latitude"
        elif "lon" == lc or "lng" in lc or "longitude" in lc:
            mapping[c] = "longitude"
    df = df.rename(columns=mapping)
    # Ensure required columns exist
    for req in ["kode_wilayah","provinsi","kabupaten","kecamatan","desa"]:
        if req not in df.columns:
            # create empty
            df[req] = ""
    # filter provinsi jawa timur (kode 35 or name contains 'jawa timur')
    cond = df["provinsi"].astype(str).str.contains("35|jawa timur", case=False, na=False) | \
           df["kode_wilayah"].astype(str).str.startswith("35")
    # If none matched by provinsi, also try by kabupaten names present and assume input already Jatim
    if cond.sum() == 0:
        # fallback: keep all and filter later by manual check (we'll attempt to guess provinsi col)
        print("[normalize_admin_df] Tidak terdeteksi provinsi 35. Mengambil seluruh dataset dan filter manual.")
        return df
    else:
        return df[cond].copy().reset_index(drop=True)

# ---------------------------
# GEOCODING (centroid kecamatan) with Nominatim (cached)
# ---------------------------
def load_cache_geocode():
    if CACHE_GEOCODE.exists():
        return pd.read_csv(CACHE_GEOCODE, dtype=str).set_index("query").to_dict(orient="index")
    return {}

def save_cache_geocode(cache):
    df = pd.DataFrame([
        {"query": q, "lat": v["lat"], "lon": v["lon"]} for q, v in cache.items()
    ])
    df.to_csv(CACHE_GEOCODE, index=False)

def geocode_kecamatan(keckey):
    """
    keckey: string like "Kecamatan X, Kabupaten Y, Jawa Timur, Indonesia"
    returns (lat, lon) or (None, None)
    """
    # Nominatim endpoint
    url = f"https://nominatim.openstreetmap.org/search?q={quote_plus(keckey)}&format=json&limit=1&addressdetails=0"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        j = r.json()
        if j:
            return float(j[0]["lat"]), float(j[0]["lon"])
    except Exception as e:
        print(f"[geocode_kecamatan] Gagal geocode {keckey}: {e}")
    return None, None

# ---------------------------
# ELEVATION (Open-Elevation) cached
# ---------------------------
def load_cache_elev():
    if CACHE_ELEV.exists():
        return pd.read_csv(CACHE_ELEV, dtype=str).set_index("loc").to_dict(orient="index")
    return {}

def save_cache_elev(cache):
    df = pd.DataFrame([
        {"loc": k, "elev": v["elev"]} for k, v in cache.items()
    ])
    df.to_csv(CACHE_ELEV, index=False)

def query_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        j = r.json()
        if "results" in j and j["results"]:
            return float(j["results"][0].get("elevation", None))
    except Exception as e:
        print(f"[query_elevation] open-elev error: {e}")
    return None

# ---------------------------
# MAIN
# ---------------------------
def main():
    print("Mulai pembuatan Village_LongLat_Approx.csv (Jawa Timur) ...")
    df_raw = load_admin_list()
    df = normalize_admin_df(df_raw)
    print(f"Jumlah baris terfilter: {len(df)}")
    # If dataset contains one row per desa, great. Otherwise we'll treat rows as desa entries.
    # Build unique kecamatan list to geocode centroid
    df["kecamatan_key"] = df["kecamatan"].astype(str).str.strip() + "||" + df["kabupaten"].astype(str).str.strip()
    unique_kec = df["kecamatan_key"].unique().tolist()
    print(f"Unique kecamatan: {len(unique_kec)}")

    geocode_cache = load_cache_geocode()
    elev_cache = load_cache_elev()

    # Geocode each kecamatan if not cached
    for i, k in enumerate(unique_kec):
        if not k or k == "||":
            continue
        if k in geocode_cache and geocode_cache[k]["lat"] not in [None,"nan",""]:
            continue
        kec_name, kab_name = k.split("||")
        query = f"{kec_name}, {kab_name}, Jawa Timur, Indonesia"
        lat, lon = geocode_kecamatan(query)
        if lat is None:
            # try shorter query without 'Kecamatan' word
            altq = f"{kec_name} {kab_name}, Jawa Timur, Indonesia"
            lat, lon = geocode_kecamatan(altq)
        geocode_cache[k] = {"lat": lat, "lon": lon}
        print(f"[{i+1}/{len(unique_kec)}] geocode {k} -> {lat},{lon}")
        save_cache_geocode(geocode_cache)
        time.sleep(1.1)  # politeness (nominatim)

    # Now set lat/lon per desa as kecamatan centroid
    lat_list = []
    lon_list = []
    elev_list = []
    for idx, row in df.iterrows():
        k = row["kecamatan_key"]
        lat = geocode_cache.get(k, {}).get("lat")
        lon = geocode_cache.get(k, {}).get("lon")
        lat_list.append(lat)
        lon_list.append(lon)

        # elevation per location (cached)
        loc_key = f"{lat},{lon}"
        elev = None
        if lat is not None and lon is not None:
            if loc_key in elev_cache:
                elev = elev_cache[loc_key]["elev"]
            else:
                elev = query_elevation(lat, lon)
                elev_cache[loc_key] = {"elev": elev}
                save_cache_elev(elev_cache)
                time.sleep(1.0)
        elev_list.append(elev)

    df["latitude"] = lat_list
    df["longitude"] = lon_list
    df["elevasi"] = elev_list

    # Select & rename output columns
    out = df.rename(columns={
        "kode_wilayah": "kode_wilayah",
        "provinsi": "provinsi",
        "kabupaten": "kabupaten",
        "kecamatan": "kecamatan",
        "desa": "desa"
    })
    out_cols = ["kode_wilayah","provinsi","kabupaten","kecamatan","desa","latitude","longitude","elevasi"]
    for c in out_cols:
        if c not in out.columns:
            out[c] = ""

    out = out[out_cols]
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"Selesai. File disimpan di: {OUTPUT_CSV}")
    print("Cache geocode:", CACHE_GEOCODE, "Cache elev:", CACHE_ELEV)

if __name__ == "__main__":
    main()
