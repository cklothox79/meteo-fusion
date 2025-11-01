import requests

def get_bmkg_forecast(lat, lon):
    """
    Ambil prakiraan cuaca dari API BMKG berbasis titik koordinat.
    (Simulasi: karena API publik BMKG belum terbuka penuh)
    """
    try:
        # Contoh dummy / fallback (simulasi)
        url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?lat={lat}&lon={lon}"
        resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            return {"status": "error", "message": f"BMKG API error {resp.status_code}"}

        data = resp.json()
        return {
            "sumber": "BMKG",
            "koordinat": {"lat": lat, "lon": lon},
            "data": data.get("data", data)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
