# GaryPOWER Signal Scanner

Python port of the **GaryPOWER** Pine Script v6 indicator.  
Detects **conditionA**: 力度新高 `days > 100` AND 上次新高 `since_last_gt100[1] > 100`

---

## Local Usage

```bash
pip install -r requirements.txt

# Single ticker
python src/garypower.py AAPL

# Multiple tickers
python src/garypower.py AAPL TSLA PLTR NVDA --period 2y

# A-share (Yahoo Finance format)
python src/garypower.py 600519.SS 000858.SZ

# Verbose mode (prints last 5 rows of indicator values)
python src/garypower.py PLTR --verbose
```

---

## GitHub Actions (Automated Daily Scan)

The workflow `.github/workflows/daily_scan.yml` runs automatically at:
- **06:00 Beijing Time** every trading day (UTC 22:00)

### Manual trigger
Go to **Actions → GaryPOWER Daily Scan → Run workflow**  
You can override the ticker list and period in the UI.

---

## Indicator Logic (ported from Pine Script)

| Variable | Description |
|---|---|
| `pjj` | Custom smoothed typical price (not standard EMA) |
| `qjj` | Volume-per-price-unit ratio |
| `xvl` | Active volume split (bull/bear/flat) |
| `hsl` | Normalised active volume |
| `gp` | 力度 (Power) |
| `gs` / `lljx` | 流量 (Flow, EMA of weighted hsl) |
| `pw` | Power/Flow ratio |
| `days` | Bars since gp was last the highest (TOPRANGE equivalent) |
| `since_last_gt100` | Bars since last `days > 100` event |
| **`conditionA`** | **`days > 100` AND `since_last_gt100[1] > 100`** |

---

## Notes

- Uses `yfinance` with `auto_adjust=True` (split & dividend adjusted) — equivalent to TradingView's adjusted data.
- `pjj` replicates Pine's `barstate.isfirst` logic via a Python loop.
- `days` replicates `ta.highest()` loop up to 2048 bars (same as Pine).
- `since_last_gt100` is stateful and computed bar-by-bar to match Pine's `var` variable behaviour.
- At least **6 months** of data recommended; **2y** (default) gives stable results.
