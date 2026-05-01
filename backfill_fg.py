"""
One-time backfill of historical CNN Fear & Greed index from a community archive.

Source: https://github.com/whit3rabbit/fear-greed-data
  - Daily values from 2011-01-03 onward, ~3800 rows
  - Older data (pre-2021) frozen from archive (hackingthemarkets, openstockalert,
    archive.org); 2021-02 onward regenerated from CNN's live endpoint
  - Repo refreshes every Friday via GitHub Actions

Run manually once. The merge is idempotent: existing F&G values in data.json
are preserved (CNN's live endpoint output is treated as canonical for dates
it covers), and missing dates are filled from the archive.
"""
import csv
import io
import json
import urllib.request

DATA_FILE = "data.json"
SOURCE = "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv"


def main():
    print(f"Downloading {SOURCE}")
    with urllib.request.urlopen(SOURCE, timeout=30) as resp:
        text = resp.read().decode()

    archive = {}
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        date_str = row.get("Date")
        try:
            score = round(float(row.get("Fear Greed", "")), 1)
        except (TypeError, ValueError):
            continue
        if date_str:
            archive[date_str] = score

    if not archive:
        print("No rows parsed from archive — aborting.")
        return

    print(f"Loaded {len(archive)} F&G rows ({min(archive)} to {max(archive)})")

    with open(DATA_FILE) as f:
        data = json.load(f)

    by_date = {h["date"]: h for h in data.get("history", [])}
    added = 0
    for date_str, score in archive.items():
        row = by_date.setdefault(date_str, {"date": date_str})
        if row.get("fear_greed") is None:
            row["fear_greed"] = score
            added += 1

    data["history"] = sorted(by_date.values(), key=lambda x: x["date"])

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Backfill complete. Added F&G to {added} new rows.")
    print(f"data.json now has {len(data['history'])} total rows "
          f"({data['history'][0]['date']} to {data['history'][-1]['date']}).")


if __name__ == "__main__":
    main()
