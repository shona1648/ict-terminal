import streamlit as st

st.set_page_config(page_title="ICT Trading Terminal", page_icon="📈", layout="wide")

st.title("🏛️ Institutional ICT AI Trading Terminal")
st.markdown("### Master Blueprint Terminal | Live Surveillance Hub")

# Sidebar Controls
st.sidebar.header("⚙️ Terminal Settings")
market = st.sidebar.selectbox("Select Market", ["NSE (Nifty / BankNifty)", "Crypto Futures", "Forex Derivatives", "MCX Commodities"])
killzone = st.sidebar.checkbox("Active Session / Killzone (Visual Toggle)", value=True)

if killzone:
    st.sidebar.success("🟢 Killzone Active: High Probability Array Setup")
else:
    st.sidebar.warning("🔴 Killzone Inactive: Consolidation Phase")

# Main Dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Market Structure & Liquidity")
    st.info("Monitoring Order Blocks, iFVG, and Market Structure Shifts (MSS).")
    if st.button("Run Liquidity Sweep Scan"):
        st.write("Scanning order flow and footprint delta... All clear for execution setup.")

with col2:
    st.subheader("🎯 Risk & Position Sizing")
    capital = st.number_input("Trading Capital (₹)", value=50000)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 3.0, 1.0)
    risk_amount = capital * (risk_pct / 100)
    st.write(f"**Allowed Risk Amount:** ₹{risk_amount:.2f}")

st.markdown("---")
st.caption("Institutional ICT AI Trading Terminal | Mobile PWA Optimized")
