"""
Fetch VIX (from Yahoo Finance) and CNN Fear & Greed Index.
Writes results to data.json for the static dashboard.
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

DATA_FILE = "data.json"


def fetch_vix():
    """Fetch current VIX from Yahoo Finance API."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=1d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        meta = data["chart"]["result"][0]["meta"]
        return round(meta["regularMarketPrice"], 2)
    except Exception as e:
        print(f"VIX fetch error: {e}")
        return None


def fetch_fear_greed():
    """Fetch CNN Fear & Greed Index."""
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        score = data["fear_and_greed"]["score"]
        return round(score, 1)
    except Exception as e:
        print(f"Fear & Greed fetch error: {e}")
        return None


def load_existing():
    """Load existing data.json to preserve history."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"current": {}, "history": []}


def main():
    now = datetime.now(timezone.utc)
    vix = fetch_vix()
    fg = fetch_fear_greed()

    if vix is None and fg is None:
        print("Both fetches failed — skipping update.")
        return

    existing = load_existing()

    current = {
        "vix": vix,
        "fear_greed": fg,
        "updated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Keep up to 90 days of daily snapshots
    history = existing.get("history", [])
    today_str = now.strftime("%Y-%m-%d")
    # Replace today's entry if it exists, otherwise append
    history = [h for h in history if h.get("date") != today_str]
    history.append({"date": today_str, "vix": vix, "fear_greed": fg})
    history = history[-90:]

    output = {"current": current, "history": history}

    with open(DATA_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Updated: VIX={vix}, F&G={fg} at {current['updated_utc']}")


if __name__ == "__main__":
    main()
