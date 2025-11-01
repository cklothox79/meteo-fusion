import pandas as pd
import requests
import time
from pathlib import Path

INPUT_FILE = Path("kode_wilayah.csv")
OUTPUT_FILE = Path("data/Village_LongLat_Approx.csv")

def geocode_name(name):
    """Gunakan Open-Meteo geocoding API (gratis tanpa API key)"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=1&language=id&format=json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        j = r.json()
        if "results" in j and len(j["results"]) > 0:
            res = j["results"][0]
            return float(res["latitude"]), float(res["longitude"])
    except Exception as e:
        print(f"  ⚠️  Gagal geocode {name}: {e}")
    return None, None

def main():
    if not INPUT_FILE.exists():
        print(f"❌ File {INPUT_FILE} tidak ditemukan.")
        return
    df = pd.read_csv(INPUT_FILE, sep=None, engine="python", dtype=str)
    df = df.fillna("")
    # deteksi nama desa
    name_col = None
    for c in df.columns:
        if "nama" in c.lower() or "desa" in c.lower() or "village" in c.lower():
            name_col = c
            break
    if name_col is None:
        print("❌ Tidak ditemukan kolom nama desa.")
        return

    df_out = []
    for i, row in df.iterrows():
        name = row[name_col].strip()
        if not name:
            continue
        code = row[df.columns[0]]
        print(f"[{i+1}/{len(df)}] Geocoding {name} ...", end=" ")
        lat, lon = geocode_name(name)
        if lat is not None and lon is not None:
            print(f"✅ {lat:.4f}, {lon:.4f}")
        else:
            print("❌ gagal")
        df_out.append({"kode_wilayah": code, "name": name, "lat": lat, "lon": lon})
        time.sleep(1.2)  # batas aman agar tidak diblokir (1 req/s)

    out = pd.DataFrame(df_out)
    out.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Selesai! File disimpan di: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    main()
