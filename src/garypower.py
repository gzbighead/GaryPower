"""
GaryPOWER Signal Scanner
Ported from Pine Script v6 by Gary
Detects conditionA: days > 100 AND since_last_gt100[1] > 100
Sends HTML email via Resend when signals are found.
"""

import os
import sys
import json
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
#  WATCHLIST
# ═══════════════════════════════════════════════════════════════════

WATCHLIST = [
    # ─── 美股核心 ─────────────────────────────────────────────────
    ("SPY",       "标普500ETF"),
    ("TQQQ",      "三倍做多纳指"),
    ("SOXL",      "三倍做多半导体"),
    ("NVDA",      "英伟达"),
    ("PLTR",      "Palantir"),
    ("TSLA",      "特斯拉"),
    ("MSFT",      "微软"),
    ("AEP",       "美国电力"),
    ("RKLB",      "火箭实验室"),
    ("AAPL",      "苹果"),
    ("AMZN",      "亚马逊"),
    ("MRVL",      "迈威尔"),
    ("CRWD",      "CrowdStrike"),
    ("DDOG",      "Datadog"),
    ("ARM",       "ARM Holding"),
    ("AMD",       "美国超微公司"),
    # ─── A股 ──────────────────────────────────────────────────────
    ("601568.SS", "北元化工"),
    ("600089.SS", "特变电工"),
    ("002322.SZ", "理工能科"),
    ("000858.SZ", "五粮液"),
    ("600941.SS", "中国移动"),
]

# name lookup
TICKER_NAMES = {t: n for t, n in WATCHLIST}


# ═══════════════════════════════════════════════════════════════════
#  INDICATOR CORE
# ═══════════════════════════════════════════════════════════════════

def calc_garypower(df):
    """
    严格按通达信公式翻译：
      QJJ  := VOL / ((H-L)*2 - ABS(C-O))
      XVL  := IF(C>O, QJJ*(H-L), IF(C<O, QJJ*(H-O+(C-L)), VOL/2))
             + IF(C>O, 0-QJJ*(H-C+(O-L)), IF(C<O, 0-QJJ*(H-L), 0-VOL/2))
      HSL  := XVL / 20 / 1.15
      力度 := HSL * 0.6
      TOPRANGE(力度)：向前找第一根严格大于当前力度的bar，距离即days
      BARSLAST(days>100)：向前找第一根days>100的bar，距离即since1
      上次新高 := IF(days>100, REF(since1,1), since1)
      conditionA := days>100 AND 上次新高>100
    """
    o = df["open"].values
    h = df["high"].values
    l = df["low"].values
    c = df["close"].values
    v = df["volume"].values
    n = len(df)

    # ── QJJ ──────────────────────────────────────────────────────
    denom = (h - l) * 2 - np.abs(c - o)
    denom = np.where(denom == 0, np.nan, denom)
    qjj = v / denom

    # ── XVL ──────────────────────────────────────────────────────
    bull = c > o
    bear = c < o
    xvl1 = np.where(bull, qjj*(h-l),
           np.where(bear, qjj*(h-o+(c-l)),
                    v/2))
    xvl2 = np.where(bull, -(qjj*(h-c+(o-l))),
           np.where(bear, -(qjj*(h-l)),
                    -(v/2)))
    xvl = xvl1 + xvl2

    # ── HSL / 力度 ────────────────────────────────────────────────
    hsl = xvl / 20 / 1.15
    ld  = hsl * 0.6

    # ── TOPRANGE(力度) ────────────────────────────────────────────
    # 向前找第一根大于等于当前力度的bar，距离即days
    # 通达信：等值也视为阻断（>=），不继续往前计数
    days = np.zeros(n)
    for idx in range(1, n):
        count = 0
        for j in range(idx - 1, -1, -1):
            if ld[j] >= ld[idx]:
                break
            count += 1
        days[idx] = count

    # ── BARSLAST(days>100) → since1 ──────────────────────────────
    # 向前找第一根 days>100 的bar，距离即since1
    since1 = np.full(n, np.nan)
    for idx in range(n):
        for j in range(idx - 1, -1, -1):
            if days[j] > 100:
                since1[idx] = idx - j
                break

    # ── 上次新高 ──────────────────────────────────────────────────
    # IF(days>100, REF(since1,1), since1)
    since = np.full(n, np.nan)
    for idx in range(n):
        if days[idx] > 100:
            since[idx] = since1[idx - 1] if idx > 0 else np.nan
        else:
            since[idx] = since1[idx]

    # ── conditionA ────────────────────────────────────────────────
    condition_a = (days > 100) & (since > 100)

    out = df.copy()
    out["ld"]          = ld
    out["days"]        = days
    out["since"]       = since
    out["conditionA"]  = condition_a
    return out


# ═══════════════════════════════════════════════════════════════════
#  DATA FETCH
# ═══════════════════════════════════════════════════════════════════

def fetch_data(ticker, period="2y"):
    raw = yf.download(ticker, period=period, interval="1d",
                      auto_adjust=True, progress=False)
    if raw.empty:
        raise ValueError(f"No data returned for {ticker}")
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    raw.columns = [c.lower() for c in raw.columns]
    raw = raw[["open", "high", "low", "close", "volume"]].dropna()
    # 去掉当天未收盘的数据，与 TradingView 日线对齐
    from datetime import date
    raw = raw[raw.index.date < date.today()]
    if raw.empty:
        raise ValueError(f"No completed daily bars for {ticker}")
    return raw


# ═══════════════════════════════════════════════════════════════════
#  SCANNER
# ═══════════════════════════════════════════════════════════════════

def scan_ticker(ticker, period="2y"):
    try:
        df   = fetch_data(ticker, period=period)
        out  = calc_garypower(df)
        last = out.iloc[-1]
        d    = last["days"]
        s    = last["since"]
        return {
            "ticker"          : ticker,
            "name"            : TICKER_NAMES.get(ticker, ""),
            "date"            : out.index[-1].strftime("%Y-%m-%d"),
            "close"           : round(float(last["close"]), 4),
            "ld"              : round(float(last["ld"]), 2),
            "days"            : int(d) if not np.isnan(d) else None,
            "since"           : int(s) if not np.isnan(s) else None,
            "conditionA"      : bool(last["conditionA"]),
            "error"           : None,
        }
    except Exception as e:
        return {
            "ticker": ticker, "name": TICKER_NAMES.get(ticker, ""),
            "date": None, "close": None, "gp": None, "gs": None,
            "pw": None, "days": None, "since_last_gt100": None,
            "conditionA": False, "error": str(e),
        }


def scan_all(period="2y"):
    tickers = [t for t, _ in WATCHLIST]
    total   = len(tickers)
    results = []
    for i, t in enumerate(tickers, 1):
        r = scan_ticker(t, period=period)
        if r["error"]:
            print(f"[{i:3d}/{total}] {t:<14} ⚠ error: {r['error']}")
        else:
            days_str  = f"{int(r['days']):>5}"  if r['days']  is not None else "  N/A"
            since_str = f"{int(r['since']):>5}" if r['since'] is not None else "  N/A"
            tag = "  🔔 conditionA" if r["conditionA"] else ""
            print(f"[{i:3d}/{total}] {t:<14} {r['name']:<24} "
                  f"days={days_str}  since={since_str}  close={r['close']}{tag}")
        results.append(r)

    df = pd.DataFrame(results)
    df = df.sort_values(["conditionA", "days"], ascending=[False, False])
    return df


# ═══════════════════════════════════════════════════════════════════
#  EMAIL  (Resend)
# ═══════════════════════════════════════════════════════════════════

RESEND_FROM = "gary@ceic.ca"
RESEND_TO   = "garyfocus@hotmail.com"


def build_html(signals, scan_date, total_scanned, errors):
    """Build a clean HTML email body."""

    def signal_rows(rows):
        out = ""
        for r in rows:
            out += f"""
            <tr>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;font-weight:600;color:#f0f0f0;">{r['ticker']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#aaa;">{r['name']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#f0f0f0;text-align:right;">{r['close']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#4ade80;text-align:right;">{r['days']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#60a5fa;text-align:right;">{r['since']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#fbbf24;text-align:right;">{round(r['ld'],3) if r['ld'] else '–'}</td>
            </tr>"""
        return out

    error_section = ""
    if errors:
        error_section = f"""
        <p style="margin-top:24px;color:#888;font-size:12px;">
          ⚠ {len(errors)} ticker(s) failed to load:
          {', '.join(e['ticker'] for e in errors)}
        </p>"""

    signal_count = len(signals)
    subject_note = f"{signal_count} signal(s)" if signal_count else "No signals"

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0d0d0d;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <div style="max-width:680px;margin:32px auto;background:#141414;border-radius:12px;overflow:hidden;border:1px solid #222;">

    <!-- header -->
    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:28px 32px;">
      <div style="font-size:22px;font-weight:700;color:#e2e8f0;letter-spacing:1px;">
        📡 GaryPOWER Signal Report
      </div>
      <div style="margin-top:6px;color:#64748b;font-size:13px;">
        {scan_date} &nbsp;·&nbsp; {total_scanned} tickers scanned &nbsp;·&nbsp; {subject_note}
      </div>
    </div>

    <!-- body -->
    <div style="padding:28px 32px;">
      {'<p style="color:#4ade80;font-size:15px;font-weight:600;margin-bottom:16px;">🔔 conditionA Triggered</p>' if signals else '<p style="color:#888;font-size:15px;">No conditionA signals today.</p>'}

      {'<table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="background:#1e1e1e;"><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">Ticker</th><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">名称</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Close</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Days</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Since</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">力度</th></tr></thead><tbody>' + signal_rows(signals) + '</tbody></table>' if signals else ''}

      <!-- legend -->
      <div style="margin-top:24px;padding:16px;background:#1a1a1a;border-radius:8px;font-size:12px;color:#64748b;line-height:1.8;">
        <strong style="color:#94a3b8;">指标说明</strong><br>
        <span style="color:#4ade80;">Days</span> — 力度新高持续天数（&gt;100 触发）<br>
        <span style="color:#60a5fa;">Since</span> — 距上次 Days&gt;100 事件的天数<br>
        <span style="color:#fbbf24;">力度</span> — HSL × 0.6（净主动买卖量）
      </div>

      {error_section}
    </div>

    <!-- footer -->
    <div style="padding:16px 32px;border-top:1px solid #1e1e1e;text-align:center;font-size:11px;color:#374151;">
      GaryPOWER · Automated by GitHub Actions
    </div>
  </div>
</body>
</html>
""", f"GaryPOWER {scan_date} | {subject_note}"


def send_email(api_key, html_body, subject):
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type" : "application/json",
                "User-Agent"   : "Mozilla/5.0 (compatible; GaryPOWER/1.0)",
            },
            json={
                "from"   : RESEND_FROM,
                "to"     : [RESEND_TO],
                "subject": subject,
                "html"   : html_body,
            },
            timeout=20,
        )
        if resp.status_code in (200, 201):
            print(f"✅ Email sent  →  {RESEND_TO}  (status {resp.status_code})")
            return True
        else:
            print(f"❌ Resend error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    api_key = os.environ.get("RESEND_KEY", "")
    period  = os.environ.get("SCAN_PERIOD", "2y")

    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'═'*60}")
    print(f"  GaryPOWER Scanner  |  {scan_date}")
    print(f"  Period: {period}  |  Tickers: {len(WATCHLIST)}")
    print(f"{'═'*60}\n")

    results = scan_all(period=period)

    signals = results[results["conditionA"] == True].to_dict("records")
    errors  = results[results["error"].notna()].to_dict("records")

    # ── terminal summary ─────────────────────────────────────────
    print(f"\n{'─'*60}")
    if signals:
        print(f"  🔔 {len(signals)} conditionA signal(s):")
        for r in signals:
            print(f"     {r['ticker']:<14} {r['name']:<20}  "
                  f"close={r['close']}  days={r['days']}  since={r['since']}")
    else:
        print("  No conditionA signals today.")
    if errors:
        print(f"\n  ⚠ {len(errors)} error(s): {', '.join(e['ticker'] for e in errors)}")
    print(f"{'─'*60}\n")

    # ── send email ───────────────────────────────────────────────
    if not api_key:
        print("⚠  RESEND_KEY not set — skipping email.")
        sys.exit(0)

    html, subject = build_html(signals, scan_date, len(WATCHLIST), errors)
    send_email(api_key, html, subject)


if __name__ == "__main__":
    main()
