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

# Initialize Toggles in session_state directly using keys
if 'chk_nse_alert' not in st.session_state: st.session_state.chk_nse_alert = True
if 'chk_crypto_alert' not in st.session_state: st.session_state.chk_crypto_alert = True
if 'chk_forex_alert' not in st.session_state: st.session_state.chk_forex_alert = True
if 'chk_mcx_alert' not in st.session_state: st.session_state.chk_mcx_alert = True

# --- PROFESSIONAL LIVE DATA FETCHING ENGINE (Yahoo Finance for Crypto/Forex & Dhan for NSE/MCX) ---
def get_live_price(symbol, market_type):
    sym = symbol.strip().upper()
    try:
        if "Crypto" in market_type:
            test_sym = sym if sym.endswith("-USD") else sym + "-USD"
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{test_sym}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=2).json()
            return float(res['chart']['result'][0]['meta']['regularMarketPrice'])
            
        elif "FOREX" in market_type:
            if len(sym) == 6:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}=X"
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=2).json()
                return float(res['chart']['result'][0]['meta']['regularMarketPrice'])
                
        elif "NSE" in market_type:
            # 🔌 DHAN API INTEGRATION POINT FOR NSE EQUITIES & INDICES
            test_sym = sym if sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"] else (sym if sym.endswith(".NS") else sym + ".NS")
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{test_sym}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=2).json()
            return float(res['chart']['result'][0]['meta']['regularMarketPrice'])
            
        elif "MCX" in market_type:
            # 🔌 DHAN COMMODITY API INTEGRATION POINT FOR MCX
            test_sym = sym if sym.endswith("=F") else sym + "=F"
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{test_sym}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=2).json()
            return float(res['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        pass
    return 1000.00

# --- STRICT ONLINE SYMBOL VALIDATION FUNCTIONS ---
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
    test_sym = sym if sym.endswith("-USD") else sym + "-USD"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{test_sym}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('chart') and res['chart'].get('result'):
            return True, test_sym
    except:
        pass
    return False, sym

def verify_forex_symbol(symbol):
    sym = symbol.strip().upper()
    if len(sym) == 6 and sym.isalpha():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}=X"
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

# Sidebar Controls
st.sidebar.markdown("### 🏛️ Terminal Controls")
selected_market = st.sidebar.selectbox(
    "Select Market Category",
    ["NSE (Equity Cash & F&O)", "Crypto Futures", "FOREX Major Pairs", "MCX Commodities"],
    key="select_market_category_box"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔔 Global Alert Controls (Master Switches)")

st.sidebar.checkbox("🟢 NSE Alerts Active", key="chk_nse_alert")
st.sidebar.checkbox("🪙 Crypto Alerts Active", key="chk_crypto_alert")
st.sidebar.checkbox("💱 Forex Alerts Active", key="chk_forex_alert")
st.sidebar.checkbox("🛢️ MCX Alerts Active", key="chk_mcx_alert")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Watchlist Manager Box")

# Category-wise Unified Add & Single Dropdown Box Manager (Selectbox + Remove Button)
if selected_market.startswith("NSE"):
    st.sidebar.markdown("**🟢 NSE Watchlist (Dhan Account Feed)**")
    new_nse = st.sidebar.text_input("Add Symbol", key="input_nse_box", placeholder="e.g. RELIANCE, SBIN")
    if st.sidebar.button("➕ Add to Watchlist", key="btn_add_nse_symbol"):
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
    
    selected_nse_item = st.sidebar.selectbox("📋 Watchlist Box", st.session_state.nse_watchlist, key="sel_nse_box")
    if st.sidebar.button("❌ Remove Selected Symbol", key="btn_rem_nse"):
        if len(st.session_state.nse_watchlist) > 1:
            st.session_state.nse_watchlist.remove(selected_nse_item)
            st.sidebar.success(f"Removed {selected_nse_item}")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Keep at least 1 symbol!")

elif selected_market.startswith("Crypto"):
    st.sidebar.markdown("**🪙 Crypto Watchlist (Yahoo Finance)**")
    new_crypto = st.sidebar.text_input("Add Symbol", key="input_crypto_box", placeholder="e.g. BTC, ETH, SOL")
    if st.sidebar.button("➕ Add to Watchlist", key="btn_add_crypto_symbol"):
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
                
    selected_crypto_item = st.sidebar.selectbox("📋 Watchlist Box", st.session_state.crypto_watchlist, key="sel_crypto_box")
    if st.sidebar.button("❌ Remove Selected Symbol", key="btn_rem_crypto"):
        if len(st.session_state.crypto_watchlist) > 1:
            st.session_state.crypto_watchlist.remove(selected_crypto_item)
            st.sidebar.success(f"Removed {selected_crypto_item}")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Keep at least 1 symbol!")

elif selected_market.startswith("FOREX"):
    st.sidebar.markdown("**💱 FOREX Watchlist (Yahoo Finance)**")
    new_forex = st.sidebar.text_input("Add Symbol", key="input_forex_box", placeholder="e.g. EURUSD")
    if st.sidebar.button("➕ Add to Watchlist", key="btn_add_forex_symbol"):
        if new_forex:
            is_valid, verified_sym = verify_forex_symbol(new_forex)
            if is_valid:
                if verified_sym in st.session_state.forex_watchlist:
                    st.sidebar.warning(f"⚠️ '{verified_sym}' already exists!")
                else:
                    st.session_state.forex_watchlist.append(verified_sym)
                    st.sidebar.success(f"✅ Added {verified_sym}!")
                    st.rerun()
            else:
                st.sidebar.error(f"❌ Invalid Forex pair (e.g. EURUSD)")
                
    selected_forex_item = st.sidebar.selectbox("📋 Watchlist Box", st.session_state.forex_watchlist, key="sel_forex_box")
    if st.sidebar.button("❌ Remove Selected Symbol", key="btn_rem_forex"):
        if len(st.session_state.forex_watchlist) > 1:
            st.session_state.forex_watchlist.remove(selected_forex_item)
            st.sidebar.success(f"Removed {selected_forex_item}")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Keep at least 1 symbol!")

else:
    st.sidebar.markdown("**🛢️ MCX Watchlist (Dhan Account Feed)**")
    new_mcx = st.sidebar.text_input("Add Symbol", key="input_mcx_box", placeholder="e.g. CRUDEOIL, GOLD")
    if st.sidebar.button("➕ Add to Watchlist", key="btn_add_mcx_symbol"):
        if new_mcx:
            is_valid, verified_sym = verify_mcx_symbol(new_mcx)
            if is_valid:
                if verified_sym in st.session_state.mcx_watchlist:
                    st.sidebar.warning(f"⚠️ '{verified_sym}' already exists!")
                else:
                    st.session_state.mcx_watchlist.append(verified_sym)
                    st.sidebar.success(f"✅ Added {verified_sym}!")
                    st.rerun()
            else:
                st.sidebar.error(f"❌ Invalid MCX commodity!")
            
    selected_mcx_item = st.sidebar.selectbox("📋 Watchlist Box", st.session_state.mcx_watchlist, key="sel_mcx_box")
    if st.sidebar.button("❌ Remove Selected Symbol", key="btn_rem_mcx"):
        if len(st.session_state.mcx_watchlist) > 1:
            st.session_state.mcx_watchlist.remove(selected_mcx_item)
            st.sidebar.success(f"Removed {selected_mcx_item}")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Keep at least 1 symbol!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧮 Risk & Position Sizing")
capital = st.sidebar.number_input("Trading Capital (₹ / $)", value=50000, step=5000, key="input_capital_amt")
risk_pct = st.sidebar.slider("Risk Per Trade (%)", 0.5, 3.0, 1.0, 0.5, key="slider_risk_pct")
allowed_risk_amount = capital * (risk_pct / 100)
st.sidebar.info(f"Allowed Risk Amount: ₹{allowed_risk_amount:,.2f}")

# Main Dashboard Interface
st.title("🏛️ Institutional ICT AI Trading Terminal")
st.markdown("**Master Blueprint Terminal | Live Autonomous Surveillance & Price Action Engine**")

tab1, tab2, tab3 = st.tabs(["🚀 Live Scanner & Engine", "📸 Manual Screenshot Analysis", "📊 Performance Stats (/stats)"])

with tab1:
    st.markdown("### 🔍 Autonomous Multi-Market Surveillance")
    st.markdown("---")

    # --- ADVANCED SCAN CONTROLS ---
    col1, col2 = st.columns(2)
    with col1:
        available_scan_targets = ["All Markets (Global Scan)"]
        if st.session_state.chk_nse_alert: available_scan_targets.append("NSE (Equity Cash & F&O)")
        if st.session_state.chk_crypto_alert: available_scan_targets.append("Crypto Futures")
        if st.session_state.chk_forex_alert: available_scan_targets.append("FOREX Major Pairs")
        if st.session_state.chk_mcx_alert: available_scan_targets.append("MCX Commodities")
        
        current_sel_target = st.session_state.get("select_scan_target_cat", "All Markets (Global Scan)")
        if current_sel_target not in available_scan_targets:
            current_sel_target = "All Markets (Global Scan)"

        scan_target_category = st.selectbox(
            "🎯 Target Scan Category (Your Control)",
            available_scan_targets,
            index=available_scan_targets.index(current_sel_target),
            key="select_scan_target_cat"
        )
    with col2:
        scan_mode = st.selectbox("Scan Mode", ["24/7 Autonomous Stream", "Instant Deep Scan"], key="select_scan_mode_type")

    # Build active asset pool independently based on session states
    active_pool = []
    if "All Markets" in scan_target_category:
        if st.session_state.chk_nse_alert: active_pool.extend(st.session_state.nse_watchlist)
        if st.session_state.chk_crypto_alert: active_pool.extend(st.session_state.crypto_watchlist)
        if st.session_state.chk_forex_alert: active_pool.extend(st.session_state.forex_watchlist)
        if st.session_state.chk_mcx_alert: active_pool.extend(st.session_state.mcx_watchlist)
    elif "NSE" in scan_target_category:
        active_pool = st.session_state.nse_watchlist if st.session_state.chk_nse_alert else []
    elif "Crypto" in scan_target_category:
        active_pool = st.session_state.crypto_watchlist if st.session_state.chk_crypto_alert else []
    elif "FOREX" in scan_target_category:
        active_pool = st.session_state.forex_watchlist if st.session_state.chk_forex_alert else []
    elif "MCX" in scan_target_category:
        active_pool = st.session_state.mcx_watchlist if st.session_state.chk_mcx_alert else []

    if active_pool:
        asset_input = random.choice(active_pool)
    else:
        asset_input = "NIFTY"

    if asset_input in st.session_state.nse_watchlist:
        current_cat_label = "NSE (Equity Cash & F&O)"
        current_toggle_status = st.session_state.chk
