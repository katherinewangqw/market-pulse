# 📊 Market Pulse

A lightweight daily dashboard tracking **VIX** and **CNN Fear & Greed Index** — hosted free on GitHub Pages, optimized for phone.

## Setup (5 minutes)

### 1. Create repo
- Create a new GitHub repo (e.g. `market-pulse`)
- Push all these files to the `main` branch

### 2. Enable GitHub Pages
- Go to **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: `main` / `/ (root)`
- Save

### 3. Seed initial data
- Go to **Actions** tab
- Click **"Update Market Data"** workflow
- Click **"Run workflow"** → Run
- Wait ~30 seconds for it to complete

### 4. Visit your dashboard
- `https://<your-username>.github.io/market-pulse/`
- On iPhone: Share → Add to Home Screen (acts like a mini app)
- On Android: Menu → Add to Home Screen

## How it works

```
GitHub Actions (cron: 9:30am + 4:30pm ET, weekdays)
    ↓
fetch_data.py → fetches VIX (Yahoo Finance) + F&G (CNN API)
    ↓
data.json (committed to repo)
    ↓
index.html (reads data.json, renders dashboard)
    ↓
GitHub Pages (serves static site)
```

## Features
- 🌙 Auto dark mode
- 📱 Mobile-first design (bookmark to home screen)
- 📈 30-day trend mini chart (builds up over time)
- 🎯 Chinese/English playbook with NOW indicator
- 🕐 Updates twice daily on market days
- 💰 100% free (GitHub Actions + Pages)

## Customization

**Change update frequency**: Edit `.github/workflows/update-data.yml` cron schedule.

**Add more indicators**: Extend `fetch_data.py` — add S&P 500 price, put/call ratio, etc.

## Notes
- Yahoo Finance and CNN endpoints are unofficial — if they change, update the URLs in `fetch_data.py`
- GitHub Actions free tier: 2,000 min/month — this uses ~1 min/day, well within limits
- History accumulates over time (kept to 90 days) for the trend chart
