import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


API_BASE = "https://api.company-information.service.gov.uk"


def _get_api_key() -> Optional[str]:
    return os.environ.get("COMPANIES_HOUSE_API_KEY")


def _build_auth_header(api_key: str) -> str:
    credentials = base64.b64encode(f"{api_key}:".encode()).decode()
    return f"Basic {credentials}"


def search_company(query: str) -> Optional[Dict[str, Any]]:
    """Search for a company by name. Returns the best match or None.
    
    Falls back silently to None when the API key is not set, the API
    is unreachable, rate-limited, or no match is found.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    url = f"{API_BASE}/search/companies?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", _build_auth_header(api_key))

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            items = data.get("items", [])
            if not items:
                return None
            best = items[0]
            return {
                "company_name": best.get("title", ""),
                "company_number": best.get("company_number", ""),
                "company_status": best.get("company_status", ""),
                "address": best.get("address_snippet", ""),
            }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None
