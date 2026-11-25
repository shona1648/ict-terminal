import json
import os
import time
from datetime import datetime, timezone, timedelta
import requests

from strategies import (
    evaluate_strategies_detailed,
    process_live_trade_updates,
)

IST = timezone(timedelta(hours=5, minutes=30))
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}

BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "8631903317:AAFX00flVYz1gSPreDtDpjFhZjauyzHWRzY",
)
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-10036395310882")

SCAN_INTERVAL_SEC = 120
STATE_FILE = "sent_alerts.json"

NSE_INDEX_TICKERS = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "^CNXFIN",
    "SENSEX": "^BSESN",
}

WATCHLIST = [
    ("NIFTY", "NSE"),
    ("BANKNIFTY", "NSE"),
    ("RELIANCE", "NSE"),
    ("TATASTEEL", "NSE"),
    ("BTC-USD", "Crypto"),
    ("ETH-USD", "Crypto"),
    ("SOL-USD", "Crypto"),
]

TF_TO_YAHOO_PARAMS = {
    "1m": ("1m", "2d"),
    "3m": ("5m", "5d"),     # Yahoo chart API mein 3m direct nahi hota, 5m fallback
    "5m": ("5m", "5d"),
    "15m": ("15m", "10d"),
    "30m": ("30m", "1mo"),
    "1h": ("60m", "3mo"),
    "4h": ("60m", "6mo"),
    "1d": ("1d", "1y"),
    "1w": ("1wk", "2y"),
}

ALL_TFS = ["3m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]


def resolve_ticker(symbol, market):
    sym = symbol.strip().upper()
    if market == "NSE":
        if sym in NSE_INDEX_TICKERS or sym.startswith("^") or sym.endswith(".NS"):
            return sym
        return f"{sym}.NS"
    if market == "Crypto":
        return sym if sym.endswith("-USD") else f"{sym}-USD"
    return sym


def fetch_candles_for_tf(ticker, tf):
    interval, range_str = TF_TO_YAHOO_PARAMS.get(tf.lower(), ("15m", "10d"))
    try:
        resp = requests.get(
            YAHOO_CHART_URL.format(ticker),
            params={"interval": interval, "range": range_str},
            headers=YAHOO_HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = (data.get("chart") or {}).get("result") or []
        if not results:
            return None, []

        res = results[0]
        meta = res.get("meta") or {}
        live_price = meta.get("regularMarketPrice")

        timestamps = res.get("timestamp") or []
        quote = ((res.get("indicators") or {}).get("quote") or [{}])[0]
        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        vols = quote.get("volume") or []

        candles = []
        for i in range(len(timestamps)):
            o = opens[i] if i < len(opens) else None
            h = highs[i] if i < len(highs) else None
            l = lows[i] if i < len(lows) else None
            c = closes[i] if i < len(closes) else None
            if None in (o, h, l, c):
                continue
            v = vols[i] if i < len(vols) and vols[i] is not None else 0
            dt_ist = datetime.fromtimestamp(timestamps[i], tz=IST).strftime("%d-%m-%Y %H:%M IST")
            candles.append({
                "time": dt_ist,
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v),
            })

        if live_price is None and candles:
            live_price = candles[-1]["close"]

        return (float(live_price) if live_price is not None else None), candles
    except Exception as e:
        print(f"[Error] {ticker} ({tf}): {e}")
        return None, []


def build_candles_by_tf(ticker):
    candles_by_tf = {}
    latest_price = None

    for tf in ALL_TFS:
        price, candles = fetch_candles_for_tf(ticker, tf)
        if price is not None:
            latest_price = price
        if candles:
            candles_by_tf[tf] = candles

    return latest_price, candles_by_tf


def send_telegram_alert(text):
    if "YOUR_BOT_TOKEN_HERE" in BOT_TOKEN or "YOUR_CHAT_ID_HERE" in CHAT_ID:
        print("[Telegram Skipped - Token/Chat ID set nahi hai]:\n" + text)
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram Error]: {e}")
        return False


def load_state():
    default_state = {"sent_ids": [], "active_trades": []}
    if not os.path.exists(STATE_FILE):
        return default_state
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {
                    "sent_ids": data.get("sent_ids", []),
                    "active_trades": data.get("active_trades", []),
                }
    except Exception:
        pass
    return default_state


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run_cycle():
    state = load_state()
    sent_ids = set(state["sent_ids"])
    active_trades = state["active_trades"]
    current_prices = {}
    market_data_cache = {}

    for sym, market in WATCHLIST:
        ticker = resolve_ticker(sym, market)
        price, candles_by_tf = build_candles_by_tf(ticker)
        if price is None or not candles_by_tf:
            continue

        current_prices[f"{market}:{sym}"] = price
        market_data_cache[(sym, market)] = (price, candles_by_tf)

    correlated_candles = {}
    for (sym, market), (_, c_by_tf) in market_data_cache.items():
        if market == "Crypto":
            correlated_candles[sym.upper()] = c_by_tf

    for (sym, market), (price, candles_by_tf) in market_data_cache.items():
        setups, alerts = evaluate_strategies_detailed(
            symbol=sym,
            market=market,
            price=price,
            candles_by_tf=candles_by_tf,
            correlated_candles_by_tf=correlated_candles if market == "Crypto" else None,
        )

        for setup, alert_text in zip(setups, alerts):
            tid = setup.get("trade_id") or f"{market}:{sym}:{alert_text}"
            if tid not in sent_ids:
                if send_telegram_alert(alert_text):
                    sent_ids.add(tid)
                    active_trades.append(setup)
                    print(f"[New Setup Sent] {tid} @ {price}")

    update_msgs, active_trades = process_live_trade_updates(active_trades, current_prices)
    for msg in update_msgs:
        send_telegram_alert(msg)
        print("[Trade Update Sent]")

    state["sent_ids"] = list(sent_ids)[-1000:]
    state["active_trades"] = active_trades
    save_state(state)


if __name__ == "__main__":
    print("🚀 Auto Scanner Started (12 Strategies Live Test)...")
    while True:
        run_cycle()
        time.sleep(SCAN_INTERVAL_SEC)
