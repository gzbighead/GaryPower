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
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]

    # 1. 基础价格与 pjj 计算
    pjj1 = (h + l + c * 2) / 4
    pjj = np.empty(len(pjj1))
    pjj[0] = pjj1.iloc[0]
    for i in range(1, len(pjj1)):
        pjj[i] = pjj1.iloc[i] * 0.9 + pjj[i - 1] * 0.1
    pjj = pd.Series(pjj, index=df.index)

    # 2. EMA
    def pine_ema(series, period):
        alpha = 2 / (period + 1)
        res = np.empty(len(series))
        res[0] = series.iloc[0]
        for i in range(1, len(series)):
            res[i] = series.iloc[i] * alpha + res[i-1] * (1 - alpha)
        return pd.Series(res, index=series.index)

    jj1 = pine_ema(pjj, 3)
    jj = jj1.shift(1)

    # 3. XVL 流量算法
    denom = (h - l) * 2 - (c - o).abs()
    denom = denom.replace(0, np.nan)
    qjj = v / denom

    bull = c > o
    bear = c < o

    xvl1 = np.where(bull, qjj * (h - l), np.where(bear, qjj * (h - o + c - l), v / 2))
    xvl2 = np.where(bull, -(qjj * (h - c + o - l)), np.where(bear, -(qjj * (h - l)), -(v / 2)))
    xvl = xvl1 + xvl2

    hsl = pd.Series(xvl, index=df.index) / 20 / 1.15
    gp = hsl / 1000 * 600

    gjll = hsl * 0.55 + hsl.shift(1) * 0.33 + hsl.shift(2) * 0.22
    gs = pine_ema(gjll.fillna(0), 3)
    pw = gp / gs.abs()

    # 4. 新高天数判定
    src = gp.values
    n = len(src)
    days = np.zeros(n)
    eps = 1e-9 
    
    for idx in range(n):
        current_val = src[idx]
        current_days = 0
        for i in range(1, min(idx + 1, 2048 + 1)):
            if i == 1:
                window_max = current_val
            else:
                window_max = np.max(src[idx - i + 1 : idx])
            
            if current_val >= window_max - eps:
                current_days = i - 1
            else:
                break
        days[idx] = current_days

    days_series = pd.Series(days, index=df.index)

    # 5. 🔥 带有诊断追踪的绝对坐标法
    since_last_gt100 = np.full(n, np.nan)
    debug_trigger_idx = np.full(n, np.nan) # 用于追踪到底是在哪一根 K 线判定为新高的
    last_gt100_bar = np.nan 

    for idx in range(n):
        if not np.isnan(days[idx]) and days[idx] > 100:
            last_gt100_bar = float(idx)
        
        if not np.isnan(last_gt100_bar):
            since_last_gt100[idx] = float(idx) - last_gt100_bar
            debug_trigger_idx[idx] = last_gt100_bar

    since_last_gt100_series = pd.Series(since_last_gt100, index=df.index)
    debug_trigger_series = pd.Series(debug_trigger_idx, index=df.index)

    # 6. 条件判断
    condition_a = (days_series > 100) & (since_last_gt100_series.shift(1) > 100)

    # 7. 返回结果
    out = df.copy()
    out["gp"] = gp
    out["gs"] = gs
    out["pw"] = pw
    out["days"] = days_series
    out["since_last_gt100"] = since_last_gt100_series
    out["debug_trigger"] = debug_trigger_series # 👈 塞入诊断标签
    out["conditionA"] = condition_a
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
    return raw[["open", "high", "low", "close", "volume"]].dropna()


# ═══════════════════════════════════════════════════════════════════
#  SCANNER
# ═══════════════════════════════════════════════════════════════════

def scan_ticker(ticker, period="2y"):
    try:
        df = fetch_data(ticker, period=period)
        out = calc_garypower(df)
        
        # 获取最后一根 K 线的数据
        last = out.iloc[-1]
        d = last["days"]
        s = last["since_last_gt100"]
        cond_a = last["conditionA"]
        
        # ═══════════════════════════════════════════════════════════════
        #  【新增】详细日志核对区
        # ═══════════════════════════════════════════════════════════════
        print(f"\n{'='*80}")
        print(f"📊 标的核对日志: {ticker} ({TICKER_NAMES.get(ticker, '未知')}) | 数据长度: {len(out)} 根 K 线")
        print(f"{'-'*80}")
        print("💡 尾部 5 天详细序列数据 (用于对照 TradingView 逐根 K 线):")
        
        # 提取最后 5 天的截面进行对账
        check_df = pd.DataFrame({
            "Close": out["close"],
            "Days(新高)": out["days"].astype(int),
            "Since(距上次)": out["since_last_gt100"],
            "Since[1](昨距)": out["since_last_gt100"].shift(1),
            "TriggerIdx(触发坐标)": out["debug_trigger"]
        }).tail(5)
        
        # 打印对账表格
        print(check_df.to_string())
        
        # 打印触发状态
        print(f"{'-'*80}")
        status_str = "🔥【触发信号】" if cond_a else "⏳【未触发】"
        print(f"当天结果 ({out.index[-1].strftime('%Y-%m-%d')}): Days={int(d) if not np.isnan(d) else 'NaN'}, "
              f"Since_Shift1={out['since_last_gt100'].shift(1).iloc[-1]} | 状态: {status_str}")
        print(f"{'='*80}\n")
        # ═══════════════════════════════════════════════════════════════

        return {
            "ticker"          : ticker,
            "name"            : TICKER_NAMES.get(ticker, ""),
            "date"            : out.index[-1].strftime("%Y-%m-%d"),
            "close"           : round(float(last["close"]), 4),
            "gp"              : round(float(last["gp"]), 2),
            "gs"              : round(float(last["gs"]), 2),
            "pw"              : round(float(last["pw"]), 4),
            "days"            : int(d) if not np.isnan(d) else None,
            "since_last_gt100": int(s) if not np.isnan(s) else None,
            "conditionA"      : bool(cond_a),
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
        print(f"[{i:3d}/{total}] {t:<14}", end=" ", flush=True)
        r = scan_ticker(t, period=period)
        tag = "🔔 conditionA" if r["conditionA"] else ("⚠ error" if r["error"] else "–")
        print(tag)
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
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#60a5fa;text-align:right;">{r['since_last_gt100']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#fbbf24;text-align:right;">{round(r['pw'],3) if r['pw'] else '–'}</td>
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

      {'<table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="background:#1e1e1e;"><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">Ticker</th><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">名称</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Close</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Days</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Since</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">PW</th></tr></thead><tbody>' + signal_rows(signals) + '</tbody></table>' if signals else ''}

      <!-- legend -->
      <div style="margin-top:24px;padding:16px;background:#1a1a1a;border-radius:8px;font-size:12px;color:#64748b;line-height:1.8;">
        <strong style="color:#94a3b8;">指标说明</strong><br>
        <span style="color:#4ade80;">Days</span> — 力度新高持续天数（&gt;100 触发）<br>
        <span style="color:#60a5fa;">Since</span> — 距上次 Days&gt;100 事件的天数（前一根 &gt;100 触发）<br>
        <span style="color:#fbbf24;">PW</span> — 力度 / |流量|
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
                  f"close={r['close']}  days={r['days']}  since={r['since_last_gt100']}")
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
