import streamlit as st
import random
import requests
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Institutional ICT AI Trading Terminal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Mobile Optimization & Institutional Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 6px; background-color: #2962ff; color: white; font-weight: bold; }
    .metric-card { background-color: #1e222d; padding: 15px; border-radius: 8px; border: 1px solid #2a2e39; margin-bottom: 10px; }
    .alert-box { background-color: #131722; padding: 20px; border-radius: 8px; border-left: 5px solid #00e676; margin-top: 15px; }
    .no-trade-box { background-color: #131722; padding: 20px; border-radius: 8px; border-left: 5px solid #ff5252; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State Watchlists & Toggles Safely
if 'nse_watchlist' not in st.session_state:
    st.session_state.nse_watchlist = ["NIFTY", "BANKNIFTY", "RELIANCE", "TATASTEEL"]
if 'crypto_watchlist' not in st.session_state:
    st.session_state.crypto_watchlist = ["BTC-USD", "ETH-USD", "SOL-USD"]
if 'forex_watchlist' not in st.session_state:
    st.session_state.forex_watchlist = ["EURUSD", "GBPUSD", "USDJPY"]
if 'mcx_watchlist' not in st.session_state:
    st.session_state.mcx_watchlist = ["CRUDEOIL", "GOLD", "SILVER", "NATURALGAS"]

if 'nse_toggle' not in st.session_state: st.session_state.nse_toggle = True
if 'crypto_toggle' not in st.session_state: st.session_state.crypto_toggle = True
if 'forex_toggle' not in st.session_state: st.session_state.forex_toggle = True
if 'mcx_toggle' not in st.session_state: st.session_state.mcx_toggle = True
if 'killzone_toggle' not in st.session_state: st.session_state.killzone_toggle = True

# --- PROFESSIONAL LIVE DATA FETCHING ENGINE ---
def get_live_price(symbol, market_type):
    sym = symbol.strip().upper()
    try:
        if "-" in sym or sym.endswith("-USD"):
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={sym.replace('-', '')}"
            res = requests.get(url, timeout=2).json()
            return float(res.get("price", 1000.0))
        elif len(sym) == 6 and sym.isalpha():
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}=X"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=2).json()
            return float(res['chart']['result'][0]['meta']['regularMarketPrice'])
        else:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
            if "NSE" in market_type and not sym.endswith(".NS") and sym not in ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"]:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}.NS"
            elif "MCX" in market_type and not sym.endswith("=F"):
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}=F"
                
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=2).json()
            price = res['chart']['result'][0]['meta']['regularMarketPrice']
            return float(price)
    except:
        pass
    return 1000.00

# --- STRICT ONLINE VALIDATION FUNCTIONS ---
def verify_nse_symbol(symbol):
    sym = symbol.strip().upper()
    if sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"]:
        return True, sym
    test_sym = sym if sym.endswith(".NS") else sym + ".NS"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{test_sym}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('chart') and res['chart'].get('result'):
            return True, sym
    except:
        pass
    return False, sym

def verify_crypto_symbol(symbol):
    sym = symbol.strip().upper()
    if not sym.endswith("-USD") and not sym.endswith("=F"):
        sym = sym + "-USD"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('chart') and res['chart'].get('result'):
            return True, sym
    except:
        pass
    return False, sym

def verify_mcx_symbol(symbol):
    sym = symbol.strip().upper()
    if sym == "CRUDE": sym = "CRUDEOIL"
    test_sym = sym if sym.endswith("=F") else sym + "=F"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{test_sym}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('chart') and res['chart'].get('result'):
            return True, sym
    except:
        pass
    return False, sym

# --- 12 CORE STRATEGIES LIBRARY ---
STRATEGIES = [
    "ICT 2022 Model", "Silver Bullet Setup", 
    "Power of 3 (AMD - Accumulation, Manipulation, Distribution)",
    "Order Block (OB) Retest Model", "Inverted Fair Value Gap (iFVG) Continuation",
    "Liquidity Sweep & Reversal Model", "Market Structure Shift (MSS) Breaker Block Entry",
    "Premium / Discount Array Matrix", "Dealing Range Open Float Model",
    "London Open Killzone Continuation", "New York Lunch Reversal Model", "Turtle Soup Entry Model"
]

# --- 13 CONFIRMATION FILTERS ---
CONFIRMATION_FILTERS = [
    "SMT Divergence", "Cumulative Volume Delta (CVD) Spike", "Footprint Delta Imbalance",
    "Session Killzone Alignment", "Higher Timeframe (HTF) POI Confluence", "Premium/Discount Array Alignment",
    "Optimal Trade Entry (OTE 0.618 - 0.786)", "Displaced Market Structure Shift",
    "Institutional Reference Number", "Round Number Magnet", "Open Interest Build-up",
    "Zero-Line Crossover", "Multi-Timeframe Sweep"
]

# Sidebar Controls (Reverted back to original 4 core categories without "All")
st.sidebar.markdown("### 🏛️ Terminal Controls")
selected_market = st.sidebar.selectbox(
    "Select Market Category",
    ["NSE (Equity Cash & F&O)", "Crypto Futures", "FOREX Major Pairs", "MCX Commodities"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔔 Global Market Toggles")

# Master Toggles Placed Safely at the Top Level
st.session_state.nse_toggle = st.sidebar.toggle("🟢 NSE Alerts ON/OFF", value=st.session_state.nse_toggle, key="top_tgl_nse")
st.session_state.crypto_toggle = st.sidebar.toggle("🪙 Crypto Alerts ON/OFF", value=st.session_state.crypto_toggle, key="top_tgl_crypto")
st.session_state.forex_toggle = st.sidebar.toggle("💱 Forex Alerts ON/OFF", value=st.session_state.forex_toggle, key="top_tgl_forex")
st.session_state.mcx_toggle = st.sidebar.toggle("🛢️ MCX Alerts ON/OFF", value=st.session_state.mcx_toggle, key="top_tgl_mcx")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Independent Watchlists")

# Category-wise Watchlist Managers (4 Options)
if selected_market.startswith("NSE"):
    st.sidebar.markdown("**🟢 NSE Watchlist (Dhan Powered)**")
    new_nse = st.sidebar.text_input("Add Symbol to NSE", key="input_nse_box", placeholder="e.g. RELIANCE, SBIN")
    if st.sidebar.button("Add to NSE", key="btn_nse"):
        if new_nse:
            is_valid, verified_sym = verify_nse_symbol(new_nse)
            if is_valid:
                if verified_sym in st.session_state.nse_watchlist:
                    st.sidebar.warning(f"⚠️ '{verified_sym}' already exists!")
                else:
                    st.session_state.nse_watchlist.append(verified_sym)
                    st.sidebar.success(f"✅ Added {verified_sym}!")
                    st.rerun()
            else:
                st.sidebar.error(f"❌ Invalid NSE symbol!")
    
    st.sidebar.markdown("**Current NSE Watchlist:**")
    for sym in list(st.session_state.nse_watchlist):
        c1, c2 = st.sidebar.columns([3, 1])
        c1.markdown(f"`{sym}`")
        if c2.button("🗑️", key=f"del_nse_{sym}"):
            if len(st.session_state.nse_watchlist) > 1:
                st.session_state.nse_watchlist.remove(sym)
                st.rerun()
            else:
                st.sidebar.warning("⚠️ Keep at least 1 symbol!")

elif selected_market.startswith("Crypto"):
    st.sidebar.markdown("**🪙 Crypto Watchlist**")
    new_crypto = st.sidebar.text_input("Add Symbol to Crypto", key="input_crypto_box", placeholder="e.g. BTC or BTC-USD")
    if st.sidebar.button("Add to Crypto", key="btn_crypto"):
        if new_crypto:
            is_valid, verified_sym = verify_crypto_symbol(new_crypto)
            if is_valid:
                if verified_sym in st.session_state.crypto_watchlist:
                    st.sidebar.warning(f"⚠️ '{verified_sym}' already exists!")
                else:
                    st.session_state.crypto_watchlist.append(verified_sym)
                    st.sidebar.success(f"✅ Added {verified_sym}!")
                    st.rerun()
            else:
                st.sidebar.error(f"❌ Invalid Crypto ticker!")
                
    st.sidebar.markdown
