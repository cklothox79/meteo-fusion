import os
import requests
from datetime import datetime, timezone

class BMKGNotConfigured(Exception):
    pass

class BMKGFetchError(Exception):
    pass

def fetch_bmkg_forecast(lat, lon, bmkg_base_url=None, timeout=12):
    """
    Attempt to fetch forecast from BMKG.
    - bmkg_base_url: if None, will check environment variable BMKG_BASE_URL
    The function expects the BMKG endpoint to accept lat/lon as query params 'lat' and 'lon',
    or a custom URL template can be provided like:
      https://example.com/forecast?lat={lat}&lon={lon}
    If not configured, raises BMKGNotConfigured.
    """
    if bmkg_base_url is None:
        bmkg_base_url = os.environ.get("BMKG_BASE_URL")
    if not bmkg_base_url:
        raise BMKGNotConfigured("BMKG endpoint not configured. Set BMKG_BASE_URL env or provide base url.")
    # If template, format it; else append params
    if "{lat}" in bmkg_base_url or "{lon}" in bmkg_base_url:
        url = bmkg_base_url.format(lat=lat, lon=lon)
        params = None
    else:
        url = bmkg_base_url
        params = {"lat": lat, "lon": lon}
    try:
        r = requests.get(url, params=params, timeout=timeout)
        # if 404 will raise for caller to handle (so we can fallback)
        r.raise_for_status()
    except requests.HTTPError as e:
        # wrap
        raise BMKGFetchError(f"HTTP {r.status_code} from BMKG: {r.text[:200]}") from e
    except Exception as e:
        raise BMKGFetchError(str(e)) from e
    # Try to parse as json if possible, else return raw text
    try:
        data = r.json()
    except Exception:
        data = {"raw_text": r.text}
    return {
        "source": "bmkg",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw": data
    }
