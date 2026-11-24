import json
import os
import time
import requests

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}

BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "8631903317:AAFX00flVYz1gSPreDtDpjFhZjauyzHWRzY",
)
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-10036395310882")

SCAN_INTERVAL_SEC = 120  # Har 2 minute mein check (zaroorat ke hisaab se badal sakte ho)
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


def resolve_ticker(symbol, market):
    sym = symbol.strip().upper()
    if market == "NSE":
        if sym in NSE_INDEX_TICKERS or sym.startswith("^") or sym.endswith(".NS"):
            return sym
        return f"{sym}.NS"
    if market == "Crypto":
        return sym if sym.endswith("-USD") else f"{sym}-USD"
    return sym


def fetch_price(ticker):
    try:
        resp = requests.get(
            YAHOO_CHART_URL.format(ticker),
            headers=YAHOO_HEADERS,
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        results = (data.get("chart") or {}).get("result") or []
        if not results:
            return None
        meta = results[0].get("meta") or {}
        price = meta.get("regularMarketPrice")
        return float(price) if price is not None else None
    except Exception as e:
        print(f"[Error] {ticker}: {e}")
        return None


def send_telegram_alert(text):
    if "YOUR_BOT_TOKEN_HERE" in BOT_TOKEN or "YOUR_CHAT_ID_HERE" in CHAT_ID:
        print("[Telegram Skipped - Token/Chat ID set nahi hai]:\n" + text)
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=8)
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram Error]: {e}")
        return False


def load_sent_alerts():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_sent_alerts(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def evaluate_strategies(symbol, market, price):
    """
    Yahan tum apni strategies ke rules daaloge.
    Abhi yeh sirf ek sample hook hai jo alert format dikhata hai.
    """
    triggered = []
    # Example placeholder:
    # if market == "Crypto" and symbol == "BTC-USD" and price > 0:
    #     triggered.append("Sample Setup #1")
    return triggered


def run_cycle():
    sent_state = load_sent_alerts()
    now = int(time.time())

    for sym, market in WATCHLIST:
        ticker = resolve_ticker(sym, market)
        price = fetch_price(ticker)
        if price is None:
            continue

        matched_setups = evaluate_strategies(sym, market, price)
        curr_prefix = "₹" if market == "NSE" else "$"

        for setup_name in matched_setups:
            alert_key = f"{market}:{sym}:{setup_name}"
            last_sent = sent_state.get(alert_key, 0)

            # 6 ghante (21600 sec) tak same setup repeat na ho
            if now - last_sent >= 21600:
                msg = (
                    f"🚨 <b>ICT Scanner Alert</b>\n"
                    f"<b>Market:</b> {market} ({sym})\n"
                    f"<b>Ticker:</b> <code>{ticker}</code>\n"
                    f"<b>Price:</b> {curr_prefix}{price:,.2f}\n"
                    f"<b>Setup:</b> {setup_name}"
                )
                if send_telegram_alert(msg):
                    sent_state[alert_key] = now
                    save_sent_alerts(sent_state)
                    print(f"[Alert Sent] {alert_key} @ {price}")


if __name__ == "__main__":
    print("🚀 Auto Scanner Started...")
    while True:
        run_cycle()
        time.sleep(SCAN_INTERVAL_SEC)
