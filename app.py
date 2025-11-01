# app.py
import streamlit as st
from core.fusion_engine import get_fusion_forecast

st.set_page_config(
    page_title="🌦️ Meteo Fusion – Prakiraan Cuaca Otomatis",
    page_icon="🌦️",
    layout="centered"
)

st.title("🌦️ Meteo Fusion – Prakiraan Cuaca Otomatis Jawa Timur")
st.markdown("""
Masukkan nama **desa/kecamatan/kabupaten** di wilayah **Jawa Timur**  
untuk mendapatkan prakiraan cuaca gabungan dari **BMKG + Open-Meteo**.
""")

query = st.text_input("🗺️ Nama Wilayah:", placeholder="Contoh: Simogirang, Prambon, Sidoarjo")

if st.button("🔍 Cari Prakiraan"):
    if query.strip():
        with st.spinner("Mengambil data prakiraan cuaca..."):
            data = get_fusion_forecast(query)

        if "error" in data:
            st.error(data["error"])
        else:
            lokasi = data.get("lokasi", {})
            st.subheader(f"📍 Lokasi: {lokasi.get('adm4', '')}, {lokasi.get('adm3', '')}, {lokasi.get('adm2', '')}")
            st.write(f"**Koordinat:** {lokasi.get('latitude')} , {lokasi.get('longitude')}")

            st.markdown("### 🌧️ Ringkasan Cuaca")
            st.info(data["ringkasan"])

            with st.expander("📊 Detail Data BMKG"):
                st.json(data.get("bmkg", {}))

            with st.expander("🌤️ Detail Data Open-Meteo"):
                st.json(data.get("openmeteo", {}))
    else:
        st.warning("Masukkan nama wilayah terlebih dahulu.")

st.markdown("---")
st.caption("Dikembangkan oleh Kelompok Meteo-Fusion – powered by BMKG & Open-Meteo APIs 🌍")
