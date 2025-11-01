# ============================================================
# 🌦️ Meteo Fusion – Prakiraan Cuaca Otomatis Jawa Timur
# ============================================================

import os
import subprocess
import streamlit as st
from core.fusion_engine import get_fusion_forecast

# ============================================================
# 1️⃣ Setup Awal & Cek File Data
# ============================================================

DATA_PATH = "data/Village_LongLat_Approx.csv"
st.set_page_config(page_title="Meteo Fusion – Jawa Timur", page_icon="🌦️", layout="wide")

st.title("🌦️ Meteo Fusion – Prakiraan Cuaca Otomatis Jawa Timur")
st.caption("Fusion data BMKG + Open-Meteo untuk wilayah administratif Jawa Timur")

# Cek apakah file data koordinat sudah tersedia
if not os.path.exists(DATA_PATH):
    st.warning("⚠️ File `Village_LongLat_Approx.csv` belum tersedia. "
               "Kamu bisa buat otomatis dengan tombol di bawah.")

    if st.button("⚙️ Generate File Koordinat (Jawa Timur)"):
        with st.spinner("Sedang membuat file koordinat, mohon tunggu..."):
            try:
                subprocess.run(["python", "generate_village_csv.py"], check=True)
                st.success("✅ File `Village_LongLat_Approx.csv` berhasil dibuat!")
            except Exception as e:
                st.error(f"Gagal membuat file CSV otomatis: {e}")
    st.stop()
else:
    st.success("✅ File `Village_LongLat_Approx.csv` siap digunakan.")

# ============================================================
# 2️⃣ Input Lokasi Pengguna
# ============================================================

query = st.text_input(
    "🗺️ Masukkan nama **desa/kecamatan/kabupaten** di Jawa Timur:",
    placeholder="Contoh: Simogirang atau Prambon",
)

if not query:
    st.info("Silakan ketik nama wilayah untuk menampilkan prakiraan cuaca.")
    st.stop()

# ============================================================
# 3️⃣ Proses Fusion Data Cuaca
# ============================================================

with st.spinner("🔄 Mengambil data cuaca gabungan dari BMKG + Open-Meteo..."):
    try:
        data = get_fusion_forecast(query)
        if data is None:
            st.error("❌ Data tidak ditemukan untuk wilayah tersebut.")
            st.stop()
    except Exception as e:
        st.error(f"Gagal memproses data fusion: {e}")
        st.stop()

# ============================================================
# 4️⃣ Tampilkan Hasil
# ============================================================

st.subheader(f"🌍 Hasil Prakiraan untuk: {data.get('lokasi', 'Wilayah Tidak Dikenal')}")
st.write(f"Koordinat: `{data.get('lat')}, {data.get('lon')}`")

# Cuaca utama
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Suhu (°C)", data.get("temperature"))
with col2:
    st.metric("Kelembapan (%)", data.get("humidity"))
with col3:
    st.metric("Curah Hujan (mm)", data.get("rain"))

st.divider()

# ============================================================
# 5️⃣ Visualisasi & Dinamika Atmosfer
# ============================================================

st.markdown("### 📈 Dinamika Atmosfer (Grafik 24 jam ke depan)")
try:
    import plotly.express as px
    import pandas as pd

    df = data.get("timeseries")
    if isinstance(df, list):
        df = pd.DataFrame(df)

    if not df.empty:
        fig = px.line(df, x="time", y="temperature", title="Perubahan Suhu (°C)", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(df, x="time", y="rain", title="Curah Hujan (mm)")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Tidak ada data timeseries tersedia.")
except Exception as e:
    st.warning(f"Tidak bisa menampilkan grafik: {e}")

st.divider()

st.caption("© 2025 Meteo Fusion | BMKG + Open-Meteo | Prototype by Ferri Kusuma & ChatGPT")
