"""
GaryPOWER Signal Scanner
Ported from Pine Script v6 by Gary
Detects conditionA: days > 100 AND since_last_gt100[1] > 100
"""

import yfinance as yf
import pandas as pd
import numpy as np
import argparse
import sys
from datetime import datetime


# ─────────────────────────────────────────
#  Core indicator calculation
# ─────────────────────────────────────────

def calc_pjj(high, low, close):
    """
    Custom smoothing (NOT standard EMA):
      bar 0  : pjj1
      bar n  : pjj1 * 0.9 + pjj1_prev * 0.1
    Pine: barstate.isfirst → pjj1; else pjj1*0.9 + pjj1[1]*0.1
    Note: pjj[1] is the PREVIOUS pjj1, not pjj.
    """
    pjj1 = (high + low + close * 2) / 4
    pjj = np.empty(len(pjj1))
    pjj[0] = pjj1.iloc[0]
    for i in range(1, len(pjj1)):
        pjj[i] = pjj1.iloc[i] * 0.9 + pjj1.iloc[i - 1] * 0.1
    return pd.Series(pjj, index=high.index)


def calc_garypower(df):
    """
    Compute all intermediate values and return enriched DataFrame.
    Input columns required: open, high, low, close, volume
    """
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]

    # ── pjj / jj ──────────────────────────────────────────────────
    pjj = calc_pjj(h, l, c)
    jj1 = pjj.ewm(span=3, adjust=False).mean()
    jj  = jj1.shift(1)                          # jj = jj1[1]

    # ── qjj ───────────────────────────────────────────────────────
    denom = (h - l) * 2 - (c - o).abs()
    denom = denom.replace(0, np.nan)             # avoid div/0
    qjj   = v / denom

    # ── xvl (active volume split) ─────────────────────────────────
    bull = c > o
    bear = c < o
    flat = ~bull & ~bear

    xvl1 = np.where(bull, qjj * (h - l),
           np.where(bear, qjj * (h - o + c - l),
                    v / 2))

    xvl2 = np.where(bull, -(qjj * (h - c + o - l)),
           np.where(bear, -(qjj * (h - l)),
                    -(v / 2)))

    xvl = xvl1 + xvl2

    # ── hsl / gp / lljx ───────────────────────────────────────────
    hsl  = pd.Series(xvl, index=df.index) / 20 / 1.15
    ld1  = hsl / 1000
    gp   = ld1 * 600                            # 力度

    gjll  = hsl * 0.55 + hsl.shift(1) * 0.33 + hsl.shift(2) * 0.22
    lljx  = gjll.ewm(span=3, adjust=False).mean()   # 流量 (gs)

    gs   = lljx
    pw   = gp / gs.abs()

    # ── days (TOPRANGE equivalent) ────────────────────────────────
    # For each bar: find the largest i (1..2048) where gp equals
    # the rolling maximum over i bars. days = that i - 1.
    src   = gp.values
    n     = len(src)
    days  = np.full(n, np.nan)
    MAX_LB = min(2048, n)

    for idx in range(n):
        best = 0
        for i in range(1, min(idx + 2, MAX_LB + 1)):
            window = src[max(0, idx - i + 1): idx + 1]
            if src[idx] == np.max(window):
                best = i - 1
            else:
                break          # once not the max, larger windows won't qualify
        days[idx] = best

    days = pd.Series(days, index=df.index)

    # ── since_last_gt100 ─────────────────────────────────────────
    # Stateful: track bar_index of last event where days > 100
    bar_index         = np.arange(n)
    last_gt100_bar    = np.full(n, np.nan)
    since_last_gt100  = np.full(n, np.nan)
    last_bar          = np.nan

    for idx in range(n):
        if days.iloc[idx] > 100:
            last_bar = bar_index[idx]
        last_gt100_bar[idx] = last_bar
        if not np.isnan(last_bar):
            since_last_gt100[idx] = bar_index[idx] - last_bar

    since_last_gt100 = pd.Series(since_last_gt100, index=df.index)

    # ── conditionA ───────────────────────────────────────────────
    # Pine: days > 100 AND since_last_gt100[1] > 100
    condition_a = (days > 100) & (since_last_gt100.shift(1) > 100)

    # ── assemble output ──────────────────────────────────────────
    out = df.copy()
    out["gp"]              = gp
    out["gs"]              = gs
    out["pw"]              = pw
    out["days"]            = days
    out["since_last_gt100"]= since_last_gt100
    out["conditionA"]      = condition_a

    return out


# ─────────────────────────────────────────
#  Data fetch
# ─────────────────────────────────────────

def fetch_data(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """Download OHLCV from Yahoo Finance and normalise column names."""
    raw = yf.download(ticker, period=period, interval=interval,
                      auto_adjust=True, progress=False)
    if raw.empty:
        raise ValueError(f"No data returned for {ticker}")

    # yfinance may return MultiIndex columns when downloading single ticker
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    raw.columns = [c.lower() for c in raw.columns]
    raw = raw[["open", "high", "low", "close", "volume"]].dropna()
    return raw


# ─────────────────────────────────────────
#  Scanner
# ─────────────────────────────────────────

def scan_ticker(ticker: str, period: str = "2y", verbose: bool = False) -> dict:
    """Run GaryPOWER on one ticker. Returns summary dict."""
    try:
        df  = fetch_data(ticker, period=period)
        out = calc_garypower(df)
        last = out.iloc[-1]

        result = {
            "ticker"          : ticker,
            "date"            : out.index[-1].strftime("%Y-%m-%d"),
            "close"           : round(float(last["close"]), 4),
            "gp"              : round(float(last["gp"]),    4),
            "gs"              : round(float(last["gs"]),    4),
            "pw"              : round(float(last["pw"]),    4),
            "days"            : int(last["days"]) if not np.isnan(last["days"]) else None,
            "since_last_gt100": int(last["since_last_gt100"])
                                if not np.isnan(last["since_last_gt100"]) else None,
            "conditionA"      : bool(last["conditionA"]),
            "error"           : None,
        }

        if verbose:
            # Print last 5 rows of key columns
            print(out[["close","gp","gs","pw","days","since_last_gt100","conditionA"]].tail(5).to_string())

        return result

    except Exception as e:
        return {
            "ticker": ticker, "date": None, "close": None,
            "gp": None, "gs": None, "pw": None,
            "days": None, "since_last_gt100": None,
            "conditionA": False, "error": str(e),
        }


def scan_list(tickers: list, period: str = "2y", verbose: bool = False) -> pd.DataFrame:
    """Scan multiple tickers and return a DataFrame sorted by conditionA."""
    results = []
    total   = len(tickers)
    for i, t in enumerate(tickers, 1):
        print(f"[{i}/{total}] Scanning {t} ...", end=" ", flush=True)
        r = scan_ticker(t, period=period, verbose=verbose)
        status = "✓ conditionA!" if r["conditionA"] else ("✗ error" if r["error"] else "–")
        print(status)
        results.append(r)

    df = pd.DataFrame(results)
    # Sort: conditionA first, then by days descending
    df = df.sort_values(["conditionA", "days"], ascending=[False, False])
    return df


# ─────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="GaryPOWER Signal Scanner")
    parser.add_argument(
        "tickers", nargs="+",
        help="One or more ticker symbols, e.g. AAPL TSLA 600519.SS"
    )
    parser.add_argument(
        "--period", default="2y",
        help="yfinance period string (default: 2y). Use longer for stable days calculation."
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print last 5 rows of indicator values per ticker"
    )
    args = parser.parse_args()

    print(f"\n{'─'*60}")
    print(f"  GaryPOWER Scanner  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'─'*60}\n")

    df = scan_list(args.tickers, period=args.period, verbose=args.verbose)

    print(f"\n{'─'*60}")
    print("  RESULTS")
    print(f"{'─'*60}")

    # Print all rows
    display_cols = ["ticker","date","close","gp","gs","pw","days","since_last_gt100","conditionA","error"]
    print(df[display_cols].to_string(index=False))

    # Highlight signals
    signals = df[df["conditionA"] == True]
    if not signals.empty:
        print(f"\n{'='*60}")
        print(f"  🔔 conditionA TRIGGERED ({len(signals)} ticker(s)):")
        for _, row in signals.iterrows():
            print(f"     {row['ticker']:10s}  date={row['date']}  "
                  f"days={row['days']}  since={row['since_last_gt100']}  "
                  f"close={row['close']}")
        print(f"{'='*60}\n")
    else:
        print("\n  No conditionA signals today.\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
