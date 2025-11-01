def summarize_fusion(result):
    """
    result: output dari get_fused_forecast
    Returns a user-friendly dict summary.
    """
    used = result.get("used_source")
    out = {"used_source": used}
    if used == "bmkg":
        out["note"] = "Menggunakan data dari BMKG (raw payload tersedia)."
        out["raw"] = result.get("bmkg", {}).get("raw")
    else:
        out["note"] = f"Using Open-Meteo (fallback). Reason: {result.get('fallback_reason', 'default')}"
        om = result.get("open_meteo", {})
        out["current"] = om.get("current_weather")
        out["daily"] = om.get("daily")
        out["raw"] = om.get("raw")
    return out
