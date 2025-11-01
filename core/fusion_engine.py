from .bmkg_api import fetch_bmkg_forecast, BMKGNotConfigured, BMKGFetchError
from .openmeteo_api import fetch_openmeteo_forecast

def get_fused_forecast(lat, lon, prefer_bmkg=True, bmkg_base_url=None):
    """
    Try BMKG first (if configured). If fails use Open-Meteo.
    Returns a dict describing which source was used and the payload.
    """
    # Try BMKG if preferred
    if prefer_bmkg:
        try:
            bmkg = fetch_bmkg_forecast(lat, lon, bmkg_base_url=bmkg_base_url)
            return {
                "used_source": "bmkg",
                "bmkg": bmkg
            }
        except BMKGNotConfigured:
            # not configured; fallthrough to Open-Meteo
            pass
        except BMKGFetchError as e:
            # BMKG reachable but returned error (404/500). Fall back but include error.
            om = fetch_openmeteo_forecast(lat, lon)
            return {
                "used_source": "open-meteo",
                "fallback_reason": str(e),
                "open_meteo": om
            }
    # Either not preferring BMKG or BMKG not configured / failed
    om = fetch_openmeteo_forecast(lat, lon)
    return {
        "used_source": "open-meteo",
        "open_meteo": om
    }
