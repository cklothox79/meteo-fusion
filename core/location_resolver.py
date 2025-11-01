from core.geocode_utils import find_nearest_village

def resolve_location(query):
    """
    Mengubah nama wilayah menjadi koordinat + struktur administrasi.
    """
    lokasi = find_nearest_village(query)
    if lokasi:
        return lokasi
    else:
        return {
            "adm1": None,
            "adm2": None,
            "adm3": None,
            "adm4": query,
            "latitude": None,
            "longitude": None
        }
