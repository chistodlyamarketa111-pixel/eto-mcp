from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List
import requests
import json
from pathlib import Path

app = FastAPI(title="ETO Travel MCP Server")

BASE_DIR = Path(__file__).parent
DEMO_FILE = BASE_DIR / "demo_data.json"

# =========================
# Models
# =========================

class GetResultsRequest(BaseModel):
    requestid: int
    lastblock: int = 3


# =========================
# Helpers
# =========================

def load_demo_results() -> List[Dict[str, Any]]:
    if not DEMO_FILE.exists():
        return []
    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("results", [])


def fetch_live_results(requestid: int, lastblock: int) -> List[Dict[str, Any]]:
    url = "https://search3.tourvisor.ru/modresult.php"
    params = {
        "requestid": requestid,
        "lastblock": lastblock,
        "referrer": "https://eto.travel/search/",
    }
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://eto.travel",
        "Referer": "https://eto.travel/",
    }

    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    raw = r.json()

    blocks = raw.get("data", {}).get("block", [])
    decode = raw.get("data", {}).get("decode", {})

    hotels = decode.get("hotels", {})
    meals = decode.get("meal", {})
    cities = decode.get("cityto", {})

    results = []

    for block in blocks:
        for h in block.get("hotel", []):
            hid = h.get("id")
            hinfo = hotels.get(str(hid), {})

            for t in h.get("tour", []):
                results.append({
                    "price_rub": t.get("pr"),
                    "date_from": t.get("dt"),
                    "nights": t.get("nt"),
                    "operator_id": t.get("op"),
                    "meal": meals.get(str(t.get("ml")), {}).get("name"),
                    "city": cities.get(str(t.get("ct")), {}).get("name"),
                    "tour_id": t.get("id"),
                    "hotel": {
                        "id": hid,
                        "name": hinfo.get("name"),
                        "stars": hinfo.get("stars"),
                        "rating": hinfo.get("rating"),
                        "region": hinfo.get("region"),
                        "subregion": hinfo.get("subregion"),
                        "country": hinfo.get("country"),
                        "image": hinfo.get("pic"),
                        "link_slug": hinfo.get("link"),
                    }
                })

    return results


# =========================
# Endpoints
# =========================

@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/mcp/get_results")
def get_results(req: GetResultsRequest):
    try:
        results = fetch_live_results(req.requestid, req.lastblock)
        if results:
            return {
                "tool": "get_results",
                "mode": "live",
                "results": results,
                "count": len(results)
            }
    except Exception:
        pass

    # Demo fallback (always works)
    demo_results = load_demo_results()

    return {
        "tool": "get_results",
        "mode": "demo_fallback",
        "warning": (
            "External search result expired or unavailable. "
            "Demo data returned for MCP interface demonstration."
        ),
        "results": demo_results,
        "count": len(demo_results)
    }

