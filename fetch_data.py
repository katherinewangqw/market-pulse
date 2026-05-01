"""
Fetch VIX, VOO (Yahoo Finance) and CNN Fear & Greed Index.
Uses ranged calls so a single fetch yields both current value and ~90 days of history.
Writes results to data.json for the static dashboard.
"""
import json
import urllib.request
from datetime import datetime, timezone

DATA_FILE = "data.json"
HISTORY_DAYS = 365

YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}
CNN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cnn.com/",
    "Origin": "https://www.cnn.com",
}


def fetch_yahoo(symbol):
    """Fetch a Yahoo symbol's recent daily history. Returns (current, prev_close, [(date, close), ...])."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
    req = urllib.request.Request(url, headers=YAHOO_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        timestamps = result.get("timestamp", []) or []
        closes = result["indicators"]["quote"][0].get("close", []) or []
        history = []
        for ts, close in zip(timestamps, closes):
            if close is None:
                continue
            date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            history.append((date_str, round(close, 2)))
        current = round(meta["regularMarketPrice"], 2)
        prev_close = round(meta.get("chartPreviousClose") or meta.get("previousClose") or current, 2)
        return current, prev_close, history
    except Exception as e:
        print(f"{symbol} fetch error: {e}")
        return None, None, []


def fetch_fear_greed():
    """Fetch CNN F&G current + historical. Returns (current, [(date, score), ...])."""
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    req = urllib.request.Request(url, headers=CNN_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        current = round(data["fear_and_greed"]["score"], 1)
        history = []
        for entry in data.get("fear_and_greed_historical", {}).get("data", []):
            ts_ms = entry.get("x")
            score = entry.get("y")
            if ts_ms is None or score is None:
                continue
            date_str = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            history.append((date_str, round(score, 1)))
        return current, history
    except Exception as e:
        print(f"Fear & Greed fetch error: {e}")
        return None, []


def load_existing():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"current": {}, "history": []}


def main():
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    vix, _, vix_hist = fetch_yahoo("^VIX")
    voo, _, voo_hist = fetch_yahoo("VOO")
    fg, fg_hist = fetch_fear_greed()

    if vix is None and voo is None and fg is None:
        print("All fetches failed — skipping update.")
        return

    existing = load_existing()
    by_date = {h["date"]: dict(h) for h in existing.get("history", [])}

    for date_str, val in vix_hist:
        by_date.setdefault(date_str, {"date": date_str})["vix"] = val
    for date_str, val in voo_hist:
        by_date.setdefault(date_str, {"date": date_str})["voo"] = val
    for date_str, val in fg_hist:
        by_date.setdefault(date_str, {"date": date_str})["fear_greed"] = val

    today_row = by_date.setdefault(today_str, {"date": today_str})
    if vix is not None:
        today_row["vix"] = vix
    if voo is not None:
        today_row["voo"] = voo
    if fg is not None:
        today_row["fear_greed"] = fg

    history = sorted(by_date.values(), key=lambda x: x["date"])[-HISTORY_DAYS:]

    current = {
        "vix": vix,
        "voo": voo,
        "fear_greed": fg,
        "updated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    with open(DATA_FILE, "w") as f:
        json.dump({"current": current, "history": history}, f, indent=2)

    print(f"Updated: VIX={vix}, VOO={voo}, F&G={fg}, history={len(history)} days")


if __name__ == "__main__":
    main()
