#!/usr/bin/env python3
"""
Supertrend 信号监控
美股加股市场趋势信号监控
每天两次触发，扫描股票列表，有信号发邮件，没有信号不发
三个信号：空转多、多转空、多头下股价跌穿20日均线
新增：当前多头标的列表，按多头持续天数从短到长排序
"""

import os
import datetime
import requests
import numpy as np
import yfinance as yf

# ─── 配置 ──────────────────────────────────────────────────────────────────
EMAIL_TO   = [
    "garyfocus@hotmail.com",
    "hua@ceic.ca",
]
EMAIL_FROM = "美股趋势报告 <gary@ceic.ca>"

# Supertrend 参数（TV 默认）
ST_PERIOD     = 10
ST_MULTIPLIER = 3.0

# 20日均线
MA_PERIOD = 20

# ─── 股票列表 ───────────────────────────────────────────────────────────────
WATCHLIST = [
("SPY", "标普500ETF"),
("QQQ", "纳指100ETF-Invesco QQQ Trust"),
("IWB", "罗素1000指数ETF-iShares"),
("IWM", "罗素2000ETF-iShares"),
("GLD", "黄金ETF-SPDR"),
("SLV", "白银ETF-iShares"),
("XLE", "能源指数ETF-SPDR"),
("NVDA", "英伟达"),
("PLTR", "Palantir"),
("TSLA", "特斯拉"),
("MSFT", "微软"),
("AEP", "美国电力"),
("RKLB", "火箭实验室"),
("AAPL", "苹果"),
("AMZN", "亚马逊"),
("MRVL", "迈威尔"),
("CRWD", "CrowdStrike"),
("DDOG", "Datadog"),
("ARM", "ARM Holding"),
("AMD", "美国超微公司"),
("CBRS", "Cerebras Systems"),
("HYLD.TO", "Hamilton美股cc ETF"),
("HMAX.TO", "Hamilton加金融 MAXIMIZER ETF"),
("TQQQ", "三倍做多纳指"),
("SOXL", "三倍做多半导体"),
("DBA", "Invesco德银农业ETF"),
("DBC", "商品指数ETF-Invesco"),
("DDM", "2倍做多道指ETF-Proshares"),
("DRN", "三倍做多房地产ETF-Direxion"),
("ERX", "2倍做多能源ETF-Direxion"),
("FAS", "三倍做多金融指数ETF-Direxion"),
("FRI", "First Trust S&P REIT Index Fund"),
("IBB", "生物科技指数ETF-iShares"),
("ICF", "精选美国房地产投资信托基金ETF-iShares"),
("IHE", "iShares安硕美国医药ETF"),
("IJH", "标普中型股指数ETF-iShares"),
("IJR", "标普小盘股指数ETF-iShares"),
("ITA", "iShares安硕美国航空航天与国防ETF"),
("ITB", "美国房屋建筑业ETF-iShares"),
("IVE", "标普500价值指数ETF-iShares"),
("IVV", "标普500ETF-iShares"),
("IVW", "标普500成长股指数ETF-iShares"),
("IWO", "罗素2000成长股指数ETF-iShares"),
("IWV", "罗素3000ETF-iShares"),
("IYC", "iShares安硕美国消费服务ETF"),
("IYF", "金融指数ETF-iShares Dow Jones"),
("IYM", "基础材料ETF-iShares"),
("IYR", "美国房地产指数ETF-iShares"),
("IYT", "运输指数ETF-iShares"),
("IYZ", "美国电信ETF-iShares"),
("KBE", "银行指数ETF-SPDR KBW"),
("KIE", "保险指数ETF-SPDR KBW"),
("MDY", "标普中型股400指数ETF-SPDR"),
("MOO", "农业企业指数ETF-VanEck"),
("NLR", "铀与核能ETF-VanEck"),
("OEF", "标普100指数ETF-iShares"),
("OIH", "石油服务指数ETF-VanEck"),
("PGF", "Invesco优先金融股指数ETF"),
("RTH", "零售指数ETF-VanEck"),
("SMH", "半导体指数ETF-VanEck"),
("SSO", "2倍做多标普500ETF-ProShares"),
("TAN", "太阳能ETF-Invesco"),
("TNA", "三倍做多小盘股ETF-Direxion"),
("TQQQ", "三倍做多纳指ETF-ProShares"),
("TWM", "罗素2000指数ETF-ProShares 两倍做空"),
("UDOW", "三倍做多道指30ETF-ProShares"),
("UNG", "美国天然气ETF"),
("UPRO", "三倍做多标普500ETF-ProShares"),
("URE", "2倍做多房地产ETF-ProShares"),
("UVXY", "1.5倍做多短期期货恐慌指数ETF-Proshares"),
("UWM", "罗素2000指数ETF-ProShares两倍做多"),
("UYG", "两倍做多金融股ETF-ProShares"),
("UYM", "2倍做多基础材料ETF-ProShares"),
("VIXY", "短期期货恐慌指数ETF-Proshares"),
("VNQ", "不动产信托指数ETF-Vanguard"),
("VOO", "标普500ETF-Vanguard"),
("VXX", "标普500短期期货恐慌指数ETN-iPath"),
("VXZ", "恐慌中期做多ETN-iPath S&P"),
("XHB", "标普房屋建筑商ETF-SPDR"),
("XLB", "SPDR原物料类ETF"),
("XLF", "金融行业ETF-SPDR"),
("XLI", "工业指数ETF-SPDR"),
("XLK", "科技行业精选指数ETF-SPDR"),
("XLP", "日常消费品精选行业指数ETF-SPDR"),
("XLU", "公用事业精选行业指数ETF-SPDR"),
("XLV", "医疗保健精选行业指数ETF-SPDR"),
("XLY", "非必需消费类ETF-SPDR"),
("XME", "SPDR标普金属与矿产业ETF"),
("XRT", "标普零售指数ETF-SPDR"),
]

# ─── 拉取日线数据 ──────────────────────────────────────────────────────────
def fetch_daily(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="6mo", interval="1d")
    if df.empty or len(df) < ST_PERIOD + MA_PERIOD + 5:
        return None
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = df[col].astype(float)
    return df


# ─── 计算 ATR ──────────────────────────────────────────────────────────────
def calc_atr(df, period):
    high  = df["High"].values.astype(float)
    low   = df["Low"].values.astype(float)
    close = df["Close"].values.astype(float)
    n     = len(close)

    tr = np.zeros(n)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i]  - close[i-1])
        )

    atr = np.zeros(n)
    atr[0] = np.mean(tr[:period])
    k = 1.0 / period
    for i in range(1, n):
        atr[i] = tr[i] * k + atr[i-1] * (1 - k)

    atr[:period] = np.nan
    return atr


# ─── 计算 Supertrend ────────────────────────────────────────────────────────
def calc_supertrend(df, period, multiplier):
    high  = df["High"].values.astype(float)
    low   = df["Low"].values.astype(float)
    close = df["Close"].values.astype(float)
    n     = len(close)

    atr = calc_atr(df, period)
    hl2 = (high + low) / 2.0

    upper_basic = hl2 + multiplier * atr
    lower_basic = hl2 - multiplier * atr

    upper = np.copy(upper_basic)
    lower = np.copy(lower_basic)
    trend = np.full(n, np.nan)
    st    = np.full(n, np.nan)

    first_valid = ST_PERIOD
    for i in range(first_valid, n):
        if np.isnan(atr[i]):
            continue

        if np.isnan(trend[i-1]):
            trend[i] = 1 if close[i] > upper_basic[i] else -1
            st[i] = lower[i] if trend[i] == 1 else upper[i]
            continue

        upper[i] = upper_basic[i] if (upper_basic[i] < upper[i-1] or close[i-1] > upper[i-1]) else upper[i-1]
        lower[i] = lower_basic[i] if (lower_basic[i] > lower[i-1] or close[i-1] < lower[i-1]) else lower[i-1]

        if close[i] > upper[i-1]:
            trend[i] = 1
        elif close[i] < lower[i-1]:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

        st[i] = lower[i] if trend[i] == 1 else upper[i]

    return trend, st


# ─── 计算20日均线 ──────────────────────────────────────────────────────────
def calc_ma(df, period):
    return df["Close"].astype(float).rolling(period).mean().values.astype(float)


# ─── 计算多头持续天数（从历史数据反推最近一次空转多的日期）──────────────────
def calc_bull_duration(trend, dates):
    """
    从最后一根bar往前遍历，找到当前多头连续段的起始bar。
    返回 (持续交易日数, 起始日期字符串)，如果当前不是多头返回 (None, None)。
    """
    n = len(trend)
    last_i = n - 1

    # 当前不是多头，直接返回
    if trend[last_i] != 1:
        return None, None

    # 往前找连续多头的起点
    start_i = last_i
    for i in range(last_i - 1, -1, -1):
        if trend[i] == 1:
            start_i = i
        else:
            break  # 碰到非多头，停止

    duration_days = last_i - start_i + 1  # 交易日数
    start_date = dates[start_i]

    # 格式化日期
    if hasattr(start_date, 'strftime'):
        start_date_str = start_date.strftime("%Y-%m-%d")
    else:
        start_date_str = str(start_date)[:10]

    return duration_days, start_date_str


# ─── 扫描单只股票 ──────────────────────────────────────────────────────────
def scan_stock(symbol):
    df = fetch_daily(symbol)
    if df is None:
        return None

    trend, st = calc_supertrend(df, ST_PERIOD, ST_MULTIPLIER)
    ma        = calc_ma(df, MA_PERIOD)
    close     = df["Close"].values.astype(float)
    dates     = df.index  # DatetimeIndex

    n       = len(close)
    prev_i  = n - 2
    last_i  = n - 1

    def safe_float(v):
        try:
            f = float(v)
            return None if np.isnan(f) else f
        except (TypeError, ValueError):
            return None

    prev_trend = safe_float(trend[prev_i]) or 0
    last_trend = safe_float(trend[last_i]) or 0
    last_close = float(close[last_i])
    last_ma    = safe_float(ma[last_i])
    last_st    = safe_float(st[last_i])

    # 计算多头持续天数
    bull_days, bull_since = calc_bull_duration(trend, dates)

    signals = []

    # 信号1：空转多
    if prev_trend == -1 and last_trend == 1:
        signals.append("🟢 空转多")

    # 信号2：多转空
    if prev_trend == 1 and last_trend == -1:
        signals.append("🔴 多转空")

    # 信号3：多头下股价跌穿20日均线
    prev_close = close[prev_i]
    prev_ma    = ma[prev_i]
    if last_trend == 1 and last_close < last_ma and prev_close >= prev_ma:
        signals.append("🟡 多头回调跌穿20均线")

    return {
        "symbol":     symbol,
        "close":      round(last_close, 3),
        "ma20":       round(last_ma, 3) if last_ma is not None else None,
        "st":         round(last_st, 3) if last_st is not None else None,
        "trend":      "多头" if last_trend == 1 else "空头",
        "bull_days":  bull_days,   # 多头持续交易日数，非多头为 None
        "bull_since": bull_since,  # 多头起始日期字符串，非多头为 None
        "signals":    signals,
    }


# ─── 发邮件 ────────────────────────────────────────────────────────────────
def send_email(triggered, all_results):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("[邮件] 未设置 RESEND_API_KEY")
        return

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7)))
    bj_time = now.strftime("%Y-%m-%d %H:%M")

    # 按信号分组
    bull = [r for r in triggered if "🟢 空转多" in r["signals"]]
    pull = [r for r in triggered if "🟡 多头回调跌穿20均线" in r["signals"]]
    bear = [r for r in triggered if "🔴 多转空" in r["signals"]]

    # 当前所有多头标的，按持续天数从短到长排序
    current_bulls = [
        r for r in all_results
        if r is not None and r.get("bull_days") is not None
    ]
    current_bulls.sort(key=lambda r: r["bull_days"])

    # 统计
    total        = len(all_results)
    bull_count   = sum(1 for r in all_results if r["trend"] == "多头" and r["ma20"] is not None and r["close"] >= r["ma20"])
    adjust_count = sum(1 for r in all_results if r["trend"] == "多头" and r["ma20"] is not None and r["close"] < r["ma20"])
    bear_count   = sum(1 for r in all_results if r["trend"] == "空头")

    # ── HTML helpers ───────────────────────────────────────────────────────
    def signal_rows(items):
        if not items:
            return '<tr><td colspan="4" style="padding:10px;color:#888;font-style:italic;">无</td></tr>'
        rows = ""
        for r in items:
            rows += (
                f'<tr>'
                f'<td style="padding:8px 12px;font-weight:bold;white-space:nowrap;">{r["symbol"]}</td>'
                f'<td style="padding:8px 12px;color:#555;">{r.get("name","")}</td>'
                f'<td style="padding:8px 12px;text-align:right;white-space:nowrap;">{r["close"]:.3f}</td>'
                f'<td style="padding:8px 12px;text-align:right;white-space:nowrap;">{r["ma20"]:.3f if r["ma20"] else "-"}</td>'
                f'<td style="padding:8px 12px;text-align:right;white-space:nowrap;">{r["st"]:.3f if r["st"] else "-"}</td>'
                f'</tr>'
            )
        return rows

    def signal_section(emoji, title, color, items):
        header_bg  = {"🟢": "#e6f4ea", "🟡": "#fef9e7", "🔴": "#fdecea"}[emoji]
        header_col = {"🟢": "#1a7340", "🟡": "#856404", "🔴": "#922b21"}[emoji]
        th = f'style="padding:8px 12px;background:#f5f5f5;font-size:12px;color:#666;text-align:left;border-bottom:1px solid #ddd;"'
        thr = f'style="padding:8px 12px;background:#f5f5f5;font-size:12px;color:#666;text-align:right;border-bottom:1px solid #ddd;"'
        return f"""
        <div style="margin-bottom:24px;">
          <div style="background:{header_bg};border-left:4px solid {header_col};padding:10px 14px;border-radius:4px 4px 0 0;">
            <span style="font-size:15px;font-weight:bold;color:{header_col};">{emoji} {title}</span>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:14px;border:1px solid #ddd;border-top:none;">
            <thead>
              <tr>
                <th {th}>代码</th>
                <th {th}>名称</th>
                <th {thr}>价格</th>
                <th {thr}>20日均线</th>
                <th {thr}>趋势线</th>
              </tr>
            </thead>
            <tbody>{signal_rows(items)}</tbody>
          </table>
        </div>"""

    def bull_table(bulls):
        if not bulls:
            return '<p style="color:#888;font-style:italic;margin:8px 0;">无</p>'
        th  = 'style="padding:8px 12px;background:#f5f5f5;font-size:12px;color:#666;text-align:left;border-bottom:2px solid #ddd;"'
        thr = 'style="padding:8px 12px;background:#f5f5f5;font-size:12px;color:#666;text-align:right;border-bottom:2px solid #ddd;"'
        rows = ""
        for i, r in enumerate(bulls):
            bg = "#ffffff" if i % 2 == 0 else "#f9f9f9"
            rows += (
                f'<tr style="background:{bg};">'
                f'<td style="padding:8px 12px;font-weight:bold;white-space:nowrap;">{r["symbol"]}</td>'
                f'<td style="padding:8px 12px;color:#555;">{r.get("name","")}</td>'
                f'<td style="padding:8px 12px;text-align:right;font-weight:bold;color:#1a7340;white-space:nowrap;">{r["bull_days"]} 天</td>'
                f'<td style="padding:8px 12px;text-align:right;color:#888;white-space:nowrap;">{r["bull_since"]}</td>'
                f'</tr>'
            )
        return f"""
        <table style="width:100%;border-collapse:collapse;font-size:14px;border:1px solid #ddd;">
          <thead>
            <tr>
              <th {th}>代码</th>
              <th {th}>名称</th>
              <th {thr}>持续天数</th>
              <th {thr}>起始日期</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>"""

    # ── 拼接 HTML ──────────────────────────────────────────────────────────
    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:680px;margin:0 auto;padding:16px;color:#222;">

      <!-- 标题 -->
      <h2 style="margin:0 0 4px;font-size:18px;">📈 美股市场趋势信号监控</h2>
      <p style="margin:0 0 16px;color:#888;font-size:13px;">温哥华时间 {bj_time}</p>

      <!-- 市场概况 -->
      <div style="display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap;">
        <div style="flex:1;min-width:120px;background:#e6f4ea;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:22px;font-weight:bold;color:#1a7340;">{bull_count}</div>
          <div style="font-size:12px;color:#1a7340;margin-top:2px;">🟢 多头</div>
        </div>
        <div style="flex:1;min-width:120px;background:#fef9e7;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:22px;font-weight:bold;color:#856404;">{adjust_count}</div>
          <div style="font-size:12px;color:#856404;margin-top:2px;">🟡 多头调整</div>
        </div>
        <div style="flex:1;min-width:120px;background:#fdecea;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:22px;font-weight:bold;color:#922b21;">{bear_count}</div>
          <div style="font-size:12px;color:#922b21;margin-top:2px;">🔴 空头</div>
        </div>
        <div style="flex:1;min-width:120px;background:#f0f0f0;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:22px;font-weight:bold;color:#555;">{total}</div>
          <div style="font-size:12px;color:#555;margin-top:2px;">📊 总扫描</div>
        </div>
      </div>

      <!-- 今日信号 -->
      {signal_section("🟢", "进入上升趋势", "#1a7340", bull)}
      {signal_section("🟡", "多头调整（跌穿20均线）", "#856404", pull)}
      {signal_section("🔴", "进入下跌趋势", "#922b21", bear)}

      <!-- 多头列表 -->
      <div style="margin-bottom:24px;">
        <div style="background:#e8f0fe;border-left:4px solid #1a56db;padding:10px 14px;border-radius:4px 4px 0 0;">
          <span style="font-size:15px;font-weight:bold;color:#1a56db;">📋 当前多头标的（共 {len(current_bulls)} 只，按持续时间从短到长）</span>
        </div>
        {bull_table(current_bulls)}
      </div>

    </div>
    """

    res = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        },
        json={
            "from":    EMAIL_FROM,
            "to":      EMAIL_TO,
            "subject": "美股市场-趋势信号报告",
            "html":    html,
        },
    )
    print(f"[邮件] {'成功' if res.status_code == 200 else '失败'} {res.status_code}")


# ─── 主流程 ────────────────────────────────────────────────────────────────
def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    print(f"[开始] {now.strftime('%Y-%m-%d %H:%M')} 共 {len(WATCHLIST)} 只")

    triggered   = []
    all_results = []

    for stock in WATCHLIST:
        symbol = stock[0]
        name   = stock[1]
        try:
            result = scan_stock(symbol)
            if result is None:
                print(f"  {symbol}: 数据不足，跳过")
                continue
            result["name"] = name
            all_results.append(result)

            sig_str   = " / ".join(result["signals"]) if result["signals"] else "无"
            st_str    = f"{result['st']:.3f}" if result['st'] is not None else "None"
            ma_str    = f"{result['ma20']:.3f}" if result['ma20'] is not None else "None"
            close_str = f"{result['close']:.3f}"
            bull_info = f" 多头{result['bull_days']}日(自{result['bull_since']})" if result['bull_days'] else ""
            print(f"  {symbol} {name}: {result['trend']}{bull_info} 现价={close_str} ST={st_str} MA20={ma_str} 信号={sig_str}")

            if result["signals"]:
                triggered.append(result)
        except Exception as e:
            print(f"  {symbol}: 错误 {e}")

    print(f"[完成] 触发信号 {len(triggered)} 只 / 当前多头 {sum(1 for r in all_results if r.get('bull_days'))} 只")

    if triggered:
        send_email(triggered, all_results)
    else:
        print("[邮件] 无信号，不发送")


if __name__ == "__main__":
    main()
