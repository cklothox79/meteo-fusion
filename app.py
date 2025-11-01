import streamlit as st
from core.location_resolver import find_location, LocationNotFound
from core.fusion_engine import get_fused_forecast
from core.formatter import summarize_fusion
import plotly.graph_objs as go

st.set_page_config(page_title="Meteo Fusion - Jawa Timur", layout="centered")

st.title("🌦️ Meteo Fusion — Prakiraan Cuaca (Jawa Timur)")
st.markdown("Fusion data: BMKG (opsional) + Open-Meteo (fallback). Masukkan nama desa/kecamatan/kabupaten di Jawa Timur:")

loc_query = st.text_input("Nama desa / kecamatan / kabupaten", value="", placeholder="mis. simogirang")
use_bmkg = st.checkbox("Prefer gunakan BMKG jika tersedia (butuh konfigurasi BMKG_BASE_URL)", value=True)

if st.button("Dapatkan Prakiraan"):
    if not loc_query.strip():
        st.error("Masukkan nama lokasi dulu.")
    else:
        try:
            name, lat, lon = find_location(loc_query)
            st.success(f"Lokasi ditemukan: **{name}** → lat={lat:.5f}, lon={lon:.5f}")
            st.map({"lat": [lat], "lon": [lon]})
            # Fetch fused forecast
            with st.spinner("Mengambil data prakiraan..."):
                fused = get_fused_forecast(lat, lon, prefer_bmkg=use_bmkg)
            summary = summarize_fusion(fused)
            st.subheader("Ringkasan Sumber Data")
            st.write(summary["note"])
            st.write(f"Used source: **{summary['used_source']}**")
            if summary["used_source"] == "open-meteo":
                current = summary.get("current")
                if current:
                    st.markdown("### Cuaca Saat Ini")
                    st.write(current)
                daily = summary.get("daily")
                if daily:
                    st.markdown("### Prakiraan Harian (Ringkasan)")
                    # daily usually has arrays: time, temperature_2m_max, temperature_2m_min, precipitation_sum, weathercode
                    import pandas as pd
                    df_daily = pd.DataFrame(daily)
                    st.dataframe(df_daily)
                    # plot max/min temp if present
                    if "temperature_2m_max" in df_daily.columns and "temperature_2m_min" in df_daily.columns:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df_daily["time"], y=df_daily["temperature_2m_max"], name="Max"))
                        fig.add_trace(go.Scatter(x=df_daily["time"], y=df_daily["temperature_2m_min"], name="Min"))
                        fig.update_layout(title="Temperature (daily)", xaxis_title="Date", yaxis_title="°C")
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("### Data BMKG (raw)")
                st.json(summary.get("raw"))
        except LocationNotFound as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Gagal memproses: {e}")
            st.exception(e)
