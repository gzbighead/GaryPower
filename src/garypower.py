import os
import json
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════════════════
#  CONFIGURATION & KV SETTINGS
# ═══════════════════════════════════════════════════════════════════
# 确保在环境变量中配置: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_KV_NAMESPACE_ID, CLOUDFLARE_API_TOKEN

WATCHLIST = [("SPY", "标普500ETF"), ("FLY", "Firefly Aerospace"), ("NVDA", "英伟达"), ("PLTR", "Palantir")] # 示例列表
TICKER_NAMES = {t: n for t, n in WATCHLIST}

def save_signal_to_kv(res_data):
    """写入 Cloudflare KV，Key 格式: signals:YYYY-MM-DD:SYMBOL"""
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    namespace_id = os.environ.get("CLOUDFLARE_KV_NAMESPACE_ID")
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")

    if not all([account_id, namespace_id, api_token]):
        return

    key = f"signals:{res_data['date']}:{res_data['ticker']}"
    
    # 构建符合要求的 JSON 结构
    record = {
        "date": res_data['date'],
        "code": res_data['ticker'],
        "price": float(res_data['close']),
        "days": int(res_data['days']),
        "since": int(res_data['since_last_gt100_shifted']),
        "receivedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "scanner"
    }

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
    
    try:
        requests.put(
            url,
            headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"},
            json=record
        )
        print(f"[KV] 成功存储: {key}")
    except Exception as e:
        print(f"[KV Error] {e}")

# ═══════════════════════════════════════════════════════════════════
#  CORE INDICATOR & SCANNER
# ═══════════════════════════════════════════════════════════════════

def calc_garypower(df):
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]
    pjj = ((h + l + c * 2) / 4).ewm(alpha=0.9, adjust=False).mean()
    jj = pjj.ewm(alpha=2/4, adjust=False).mean().shift(1)
    
    denom = (h - l) * 2 - (c - o).abs()
    qjj = v / denom.replace(0, np.nan)
    
    bull, bear = c > o, c < o
    xvl = np.where(bull, qjj * (h - l), np.where(bear, qjj * (h - o + c - l), v / 2)) + \
          np.where(bull, -(qjj * (h - c + o - l)), np.where(bear, -(qjj * (h - l)), -(v / 2)))
    
    hsl = pd.Series(xvl, index=df.index) / 20 / 1.15
    gp = hsl * 0.6
    gs = (hsl * 0.55 + hsl.shift(1) * 0.33 + hsl.shift(2) * 0.22).ewm(alpha=2/4, adjust=False).mean()
    
    # Days 计算
    src = gp.values
    n = len(src)
    days = np.zeros(n)
    for idx in range(1, n):
        count = 0
        for j in range(idx - 1, -1, -1):
            if src[j] < src[idx]: count += 1
            else: break
        days[idx] = count

    # Since 计算
    since_last_gt100 = np.full(n, np.nan)
    last_gt100_bar = np.nan
    bar_index = np.arange(n)
    for idx in range(n):
        if days[idx] > 100: last_gt100_bar = bar_index[idx]
        if not np.isnan(last_gt100_bar): since_last_gt100[idx] = bar_index[idx] - last_gt100_bar

    out = df.copy()
    out["days"] = days
    out["since_last_gt100"] = since_last_gt100
    out["conditionA"] = (pd.Series(days, index=df.index) > 100) & (pd.Series(since_last_gt100, index=df.index).shift(1) > 100)
    return out

def scan_ticker(ticker):
    try:
        # 数据获取
        t = yf.Ticker(ticker)
        df = pd.concat([t.history(period="2y"), t.history(period="1mo")]).sort_index()
        df = df[~df.index.duplicated(keep='last')].dropna()
        df.columns = [c.lower() for c in df.columns]
        
        out = calc_garypower(df)
        last = out.iloc[-1]
        
        res = {
            "ticker": ticker,
            "date": out.index[-1].strftime("%Y-%m-%d"),
            "close": last["close"],
            "days": last["days"],
            "since_last_gt100_shifted": out['since_last_gt100'].shift(1).iloc[-1],
            "conditionA": last["conditionA"]
        }
        
        if res["conditionA"]:
            print(f"🔥 触发信号: {ticker}")
            save_signal_to_kv(res)
            
    except Exception as e:
        print(f"扫描 {ticker} 失败: {e}")

# ═══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    for ticker, name in WATCHLIST:
        scan_ticker(ticker)
