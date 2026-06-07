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
    ("ARGX", "argenx SE"),
    ("LULU", "Lululemon Athletica"),
]

# name lookup
TICKER_NAMES = {t: n for t, n in WATCHLIST}


# ═══════════════════════════════════════════════════════════════════
#  INDICATOR CORE
# ═══════════════════════════════════════════════════════════════════

def calc_garypower(df):
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]

    # 1. 基础价格与 PJJ 计算
    # PJJ:=DMA((H + L + C * 2) / 4, 0.9);
    pjj_input = (h + l + c * 2) / 4
    pjj = pjj_input.ewm(alpha=0.9, adjust=False).mean()

    # 2. EMA 计算
    def pine_ema(series, period):
        alpha = 2 / (period + 1)
        return series.ewm(alpha=alpha, adjust=False).mean()

    jj1 = pine_ema(pjj, 3)
    jj = jj1.shift(1)

    # 3. 流量控制算法 (XVL)
    # QJJ:=VOL / ((H - L) * 2 - ABS(C - O));
    denom = (h - l) * 2 - (c - o).abs()
    denom = denom.replace(0, np.nan)  # 规避分母为0导致的极值不稳定
    qjj = v / denom

    bull = c > o
    bear = c < o

    xvl1 = np.where(bull, qjj * (h - l), np.where(bear, qjj * (h - o + c - l), v / 2))
    xvl2 = np.where(bull, -(qjj * (h - c + o - l)), np.where(bear, -(qjj * (h - l)), -(v / 2)))
    xvl = xvl1 + xvl2

    hsl = pd.Series(xvl, index=df.index) / 20 / 1.15
    gp = hsl * 0.6  # 力度:HSL*0.6 完美对齐

    gjll = hsl * 0.55 + hsl.shift(1) * 0.33 + hsl.shift(2) * 0.22
    gs = pine_ema(gjll.fillna(0), 3)
    pw = gp / gs.abs()

    # 4. 力度新高:TOPRANGE(力度) -> 动态回溯算法
    src = gp.values
    n = len(src)
    days = np.zeros(n)
    
    for idx in range(1, n):
        val = src[idx]
        count = 0
        for j in range(idx - 1, -1, -1):
            if src[j] < val:
                count += 1
            else:
                break
        days[idx] = count

    days_series = pd.Series(days, index=df.index)

    # 5. 状态机逻辑及错位对齐
    bar_index = np.arange(n)
    since_last_gt100 = np.full(n, np.nan)
    last_gt100_bar = np.nan

    for idx in range(n):
        if not np.isnan(days[idx]) and days[idx] > 100:
            last_gt100_bar = bar_index[idx]
        if not np.isnan(last_gt100_bar):
            since_last_gt100[idx] = bar_index[idx] - last_gt100_bar

    since_last_gt100_series = pd.Series(since_last_gt100, index=df.index)

    # 6. 条件判断：days > 100 并且【上一根】距上次新高天数 > 100
    condition_a = (days_series > 100) & (since_last_gt100_series.shift(1) > 100)

    # 7. 组装输出
    out = df.copy()
    out["gp"] = gp
    out["gs"] = gs
    out["pw"] = pw
    out["days"] = days_series
    out["since_last_gt100"] = since_last_gt100_series
    out["conditionA"] = condition_a
    return out


# ═══════════════════════════════════════════════════════════════════
#  DATA FETCH (强力穿透与高精度版：确保拿到最新价，保留3位小数)
# ═══════════════════════════════════════════════════════════════════

def fetch_data(ticker, period="2y"):
    import yfinance as yf
    import pandas as pd
    import numpy as np
    
    t = yf.Ticker(ticker)
    
    # 1. 核心大招：利用 period="1mo" 的最高实时权限榨干 Yahoo 的最新“今天”数据
    # Yahoo 的服务器对 1mo/3mo 内的数据刷新率最高，能强制穿透未完全结算的最新交易日
    df_recent = t.history(period="1mo", interval="1d", auto_adjust=True, keepna=True)
    
    # 2. 如果最新数据里没有今天，或者你想双重保险，拉取 2y 的基础历史数据
    df_history = t.history(period=period, interval="1d", auto_adjust=True, keepna=True)
    
    # 3. 合并新旧账本，确保最新的一天（周五）绝对被囊括进来
    # combined 会自动根据日期 Index 去重并保留最新的那根 K 线
    raw = pd.concat([df_history, df_recent]).sort_index()
    raw = raw[~raw.index.duplicated(keep='last')]
    
    if raw.empty:
        raise ValueError(f"No data returned for {ticker}")
        
    # 兼容多级索引
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
        
    raw.columns = [c.lower() for c in raw.columns]
    
    # 4. 过滤成交量为 0 的日子（但如果是今天且正在交易，Volume 可能暂时为 NaN，要保留）
    # 只有当 Volume 明确存在且等于 0 的非交易日才过滤
    raw = raw[~(raw["volume"] == 0)]
    
    # 5. 关键修复：不要做任何 round() 强制截断！
    # 很多低价股/美股 ETF 报价在 3 位甚至 4 位小数，这里必须保持原始 float64 精度用于后面指标计算
    # 向前填充未结算数据（如果是盘中，防止 Close 暂时为 NaN）
    raw = raw.ffill()
    
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
        c = last["close"]
        gp_val = last["gp"]
        d = last["days"]
        s = last["since_last_gt100"]
        cond_a = last["conditionA"]
       
        # 打印触发状态 (已增加 Close 和 力度 并在控制台格式化对齐)
        # 找到这部分代码，修改控制台打印和 round 位数：
        status_str = "🔥【触发信号】" if cond_a else ""
        # 修复控制台打印：Close 改为 :>.3f 保留3位小数
        print(f": Close={c:>.3f}, 力度(gp)={gp_val:>.2f}, "
              f"Days={int(d) if not np.isnan(d) else 'NaN'}, "
              f"Since={out['since_last_gt100'].shift(1).iloc[-1]}  {status_str}")

        if cond_a:
           print(f"KV 写入:")
           save_signal_to_kv(ticker, c, d, s)

        return {
            "ticker"          : ticker,
            "name"            : TICKER_NAMES.get(ticker, ""),
            "date"            : out.index[-1].strftime("%Y-%m-%d"),
            # 💡 核心修改：close 的四舍五入至少保留 4 位，或者干脆不 round 维持高精度
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
        print(f"[{i:>{len(str(total))}}/{total}] {t:<11}", end=" ", flush=True)
        r = scan_ticker(t, period=period)
        results.append(r)

    df = pd.DataFrame(results)
    df = df.sort_values(["conditionA", "days"], ascending=[False, False])
    return df
    
# ═══════════════════════════════════════════════════════════════════
#  写入CLOUDFLARE KV
# ═══════════════════════════════════════════════════════════════════
# 1. 独立且安全的 KV 写入函数（完全独立，不影响原程序）
def save_signal_to_kv(ticker, close, days, since):
    try:
        # 获取环境变量
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        namespace_id = os.environ.get("CLOUDFLARE_KV_NAMESPACE_ID")
        api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
        
        if not (account_id and namespace_id and api_token):
            return

        date_str = datetime.now().strftime("%Y-%m-%d")
        key = f"signals:{date_str}:{ticker}"
        print(f"KV key: {key}")
        
        record = {
            "date": date_str,
            "code": ticker,
            "price": float(close),
            "days": int(days),
            "since": int(since),
            "receivedAt": datetime.now().isoformat() + "Z",
            "source": "scanner"
        }
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
        requests.put(url, headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}, json=record)
    except Exception as e:
        print(f"KV 写入跳过或失败: {e}")

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

    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:28px 32px;">
      <div style="font-size:22px;font-weight:700;color:#e2e8f0;letter-spacing:1px;">
        📡 GaryPOWER Signal Report
      </div>
      <div style="margin-top:6px;color:#64748b;font-size:13px;">
        {scan_date} &nbsp;·&nbsp; {total_scanned} tickers scanned &nbsp;·&nbsp; {subject_note}
      </div>
    </div>

    <div style="padding:28px 32px;">
      {'<p style="color:#4ade80;font-size:15px;font-weight:600;margin-bottom:16px;">🔔 conditionA Triggered</p>' if signals else '<p style="color:#888;font-size:15px;">No conditionA signals today.</p>'}

      {'<table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="background:#1e1e1e;"><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">Ticker</th><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">名称</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Close</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Days</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Since</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">PW</th></tr></thead><tbody>' + signal_rows(signals) + '</tbody></table>' if signals else ''}

      {error_section}
    </div>

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
    print(f"   GaryPOWER Scanner  |  {scan_date}")
    print(f"   Period: {period}  |  Tickers: {len(WATCHLIST)}")
    print(f"{'═'*60}\n")

    results = scan_all(period=period)

    signals = results[results["conditionA"] == True].to_dict("records")
    errors  = results[results["error"].notna()].to_dict("records")

    # ── terminal summary ─────────────────────────────────────────
    print(f"\n{'─'*60}")
    if signals:
        print(f"   🔔 {len(signals)} conditionA signal(s):")
        for r in signals:
            print(f"     {r['ticker']:<14} {r['name']:<20}  "
                  f"close={r['close']:<8} gp(力度)={r['gp']:<8} days={r['days']:<5} since={r['since_last_gt100']}")
    else:
        print("   No conditionA signals today.")
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
