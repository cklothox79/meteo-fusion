import streamlit as st
from core.geocode_utils import get_location
from core.openmeteo_api import get_openmeteo
from core.bmkg_api import get_bmkg
from core.fusion_engine import fuse_data
from core.formatter import format_output

st.set_page_config(page_title="Meteo Fusion Jatim", page_icon="🌦️", layout="centered")

st.title("🌦️ Meteo Fusion — Prakiraan Cuaca Jawa Timur")
st.write("Masukkan nama desa/kecamatan untuk melihat prakiraan cuaca fusion BMKG + Open-Meteo.")

nama = st.text_input("Nama wilayah/desa", "")

if nama:
    lokasi = get_location(nama)
    if lokasi:
        lat, lon = lokasi["lat"], lokasi["lon"]
        bmkg_data = get_bmkg(lat, lon)
        openmeteo_data = get_openmeteo(lat, lon)
        fused = fuse_data(bmkg_data, openmeteo_data)
        st.text(format_output(lokasi['nama'], lat, lon, fused))
    else:
        st.warning("Wilayah tidak ditemukan.")
