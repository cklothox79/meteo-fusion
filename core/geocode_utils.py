import pandas as pd

def load_village_data():
    """
    Load daftar desa/kecamatan/kabupaten beserta koordinatnya.
    Ambil dari CSV publik di GitHub kamu.
    """
    url = "https://raw.githubusercontent.com/cklothoz79/kusuma-converter/main/kode_wilayah.csv"
    df = pd.read_csv(url)
    return df

def find_nearest_village(query):
    """
    Mencari nama desa/kecamatan yang paling cocok dengan input user.
    """
    df = load_village_data()
    q = query.lower().strip()
    match = df[df['nama_wilayah'].str.lower().str.contains(q)]

    if match.empty:
        return None

    row = match.iloc[0]
    return {
        "adm1": row.get("provinsi"),
        "adm2": row.get("kabupaten"),
        "adm3": row.get("kecamatan"),
        "adm4": row.get("desa"),
        "latitude": row.get("lat"),
        "longitude": row.get("lon")
    }
