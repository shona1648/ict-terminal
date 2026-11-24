from datetime import datetime, time as dt_time, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
PENDING_MARKETS = {"MCX"}

STRATEGY_1_CONFIG = {
    "id": "STRAT_01",
    "name": "ICT 2022 Model",
    "markets": ["NSE", "Crypto"],
    "pending_markets": ["MCX"],
    "timeframes": {
        "NSE": {
            "Intraday": ["3m", "5m", "15m"],
            "Swing": ["1h", "4h", "1d"],
            "HTF": ["1d", "1w"],
        },
        "Crypto": {
            "Intraday": ["15m", "30m", "1h"],
            "Swing": ["4h", "1d"],
            "HTF": ["1d", "1w"],
        },
    },
}

STRATEGY_2_CONFIG = {
    "id": "STRAT_02",
    "name": "Silver Bullet Setup",
    "markets": ["NSE", "Crypto"],
    "pending_markets": ["MCX"],
    "styles": ["Intraday"],
    "timeframes": {
        "NSE": {
            "Intraday": ["3m", "5m", "15m"],
        },
        "Crypto": {
            "Intraday": ["15m", "30m", "1h"],
        },
    },
    "delivery_windows_ist": {
        "NSE": [
            (dt_time(9, 30), dt_time(10, 30)),
            (dt_time(13, 30), dt_time(14, 30)),
        ],
        "Crypto": [
            (dt_time(13, 30), dt_time(14, 30)),  # London Silver Bullet
            (dt_time(19, 30), dt_time(20, 30)),  # NY AM Silver Bullet
            (dt_time(23, 30), dt_time(0, 30)),   # NY PM Silver Bullet
        ],
    },
}

STRATEGY_3_CONFIG = {
    "id": "STRAT_03",
    "name": "Power of 3 (AMD)",
    "markets": ["NSE", "Crypto"],
    "pending_markets": ["MCX"],
    "styles": ["Intraday", "Swing"],
    "use_killzone": False,
    "timeframes": {
        "NSE": {
            "Intraday": ["3m", "5m", "15m"],
            "Swing": ["15m", "1h", "4h", "1d"],
            "HTF_POI": ["4h", "1d", "1w"],
        },
        "Crypto": {
            "Intraday": ["15m", "30m", "1h"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POI": ["4h", "1d", "1w"],
        },
    },
}

STRATEGY_4_CONFIG = {
    "id": "STRAT_04",
    "name": "Market Maker Buy/Sell Model (MMMS)",
    "markets": ["NSE", "Crypto"],
    "pending_markets": ["MCX"],
    "styles": ["Intraday", "Swing"],
    "use_killzone": False,
    "timeframes": {
        "NSE": {
            "Intraday": ["3m", "5m", "15m"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POI": ["4h", "1d", "1w"],
        },
        "Crypto": {
            "Intraday": ["15m", "30m", "1h"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POI": ["4h", "1d", "1w"],
        },
    },
}

STRATEGY_5_CONFIG = {
    "id": "STRAT_05",
    "name": "Order Block (OB) Retest Model",
    "markets": ["NSE", "Crypto"],
    "pending_markets": ["MCX"],
    "styles": ["Intraday", "Swing"],
    "use_killzone": False,
    "timeframes": {
        "NSE": {
            "Intraday": ["3m", "5m", "15m"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POI": ["4h", "1d", "1w"],
        },
        "Crypto": {
            "Intraday": ["15m", "30m", "1h"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POI": ["4h", "1d", "1w"],
        },
    },
}

STRATEGY_6_CONFIG = {
    "id": "STRAT_06",
    "name": "Liquidity Sweep & Reversal Model",
    "markets": ["NSE", "Crypto"],
    "pending_markets": ["MCX"],
    "styles": ["Intraday", "Swing"],
    "use_killzone": False,
    "timeframes": {
        "NSE": {
            "Intraday": ["3m", "5m", "15m"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POOLS": ["1d", "1w"],
        },
        "Crypto": {
            "Intraday": ["15m", "30m", "1h"],
            "Swing": ["1h", "4h", "1d"],
            "HTF_POOLS": ["1d", "1w"],
        },
    },
}

NSE_INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX", "^NSEI", "^NSEBANK", "^CNXFIN", "^BSESN"}


def get_ist_now():
    return datetime.now(IST)


def format_ist_timestamp(dt=None):
    dt = dt or get_ist_now()
    return dt.strftime("%d-%m-%Y %I:%M:%S %p IST")


def _in_window(now_t, start_t, end_t):
    if start_t <= end_t:
        return start_t <= now_t <= end_t
    return now_t >= start_t or now_t <= end_t


def check_market_open_hours(market, now_dt=None):
    """
    Active market hours check (IST) without killzone filtering.
    """
    if market in PENDING_MARKETS:
        return False, f"{market} Pending"

    now_dt = now_dt or get_ist_now()
    t = now_dt.time()

    if market == "NSE":
        if now_dt.weekday() >= 5:
            return False, "NSE Weekend Closed"
        if not _in_window(t, dt_time(9, 15), dt_time(15, 30)):
            return False, "Outside NSE Hours"
        return True, "NSE Active Hours"

    if market == "Crypto":
        return True, "Crypto 24/7 Active"

    return False, "Unsupported Market"


def check_session_and_killzone(market, style, now_dt=None):
    """
    Market hours aur Intraday Killzone alignment check (IST).
    Swing mode mein Killzone bypass rehta hai, par active market hours check honge.
    """
    allowed_hours, reason = check_market_open_hours(market, now_dt)
    if not allowed_hours:
        return False, reason

    now_dt = now_dt or get_ist_now()
    t = now_dt.time()

    if market == "NSE":
        return True, "NSE Active Hours"

    if market == "Crypto":
        if style == "Swing":
            return True, "Crypto Swing (Killzone Bypassed)"
        london_kz = _in_window(t, dt_time(12, 30), dt_time(15, 30))
        ny_kz = _in_window(t, dt_time(17, 30), dt_time(20, 30))
        ny_pm_kz = _in_window(t, dt_time(23, 0), dt_time(1, 30))
        if london_kz or ny_kz or ny_pm_kz:
            return True, "Crypto Killzone Active"
        return False, "Outside Crypto Killzone"

    return False, "Unsupported Market"


def check_silver_bullet_window(market, now_dt=None):
    """
    Strategy #2: Killzone + 60-minute Interbank Delivery Window check (IST).
    NSE mein London/NY Killzone bypass karke NSE Silver Bullet windows check hote hain.
    """
    allowed_hours, reason = check_market_open_hours(market, now_dt)
    if not allowed_hours:
        return False, reason

    now_dt = now_dt or get_ist_now()
    t = now_dt.time()

    if market == "NSE":
        for start_t, end_t in STRATEGY_2_CONFIG["delivery_windows_ist"]["NSE"]:
            if _in_window(t, start_t, end_t):
                return True, "NSE Silver Bullet Delivery Window"
        return False, "Outside NSE Silver Bullet Window"

    if market == "Crypto":
        allowed_kz, kz_reason = check_session_and_killzone("Crypto", "Intraday", now_dt)
        if not allowed_kz:
            return False, kz_reason
        for start_t, end_t in STRATEGY_2_CONFIG["delivery_windows_ist"]["Crypto"]:
            if _in_window(t, start_t, end_t):
                return True, "Crypto Silver Bullet Delivery Window"
        return False, "Outside Crypto Silver Bullet Window"

    return False, "Unsupported Market"


def calc_atr(candles, period=14):
    if len(candles) < period + 1:
        return (candles[-1]["high"] - candles[-1]["low"]) if candles else 0.0
    trs = []
    for i in range(-period, 0):
        c = candles[i]
        prev_c = candles[i - 1]
        tr = max(
            c["high"] - c["low"],
            abs(c["high"] - prev_c["close"]),
            abs(c["low"] - prev_c["close"]),
        )
        trs.append(tr)
    return sum(trs) / len(trs)


def avg_volume(candles, lookback=20):
    vols = [c.get("volume", 0) or 0 for c in candles[-lookback:]]
    valid = [v for v in vols if v > 0]
    return (sum(valid) / len(valid)) if valid else 0.0


def check_htf_bias(candles_by_tf):
    """
    Swing mode ke liye 1D / 1W structure & draw-on-liquidity bias.
    Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
    """
    htf_candles = candles_by_tf.get("1d") or candles_by_tf.get("1w") or []
    if len(htf_candles) < 10:
        return "NEUTRAL"

    recent = htf_candles[-10:]
    mid = len(recent) // 2
    first_half_high = max(c["high"] for c in recent[:mid])
    second_half_high = max(c["high"] for c in recent[mid:])
    first_half_low = min(c["low"] for c in recent[:mid])
    second_half_low = min(c["low"] for c in recent[mid:])
    last_close = recent[-1]["close"]

    if second_half_high > first_half_high and second_half_low >= first_half_low and last_close > recent[-3]["close"]:
        return "BULLISH"
    if second_half_low < first_half_low and second_half_high <= first_half_high and last_close < recent[-3]["close"]:
        return "BEARISH"
    return "NEUTRAL"


def check_htf_poi_bias(candles_by_tf, live_price):
    """
    Swing mode ke liye 4H / 1D / 1W HTF POI (OB / FVG / Breaker / Mitigation / Major Swing) confluence check.
    Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
    """
    for htf in ("4h", "1d", "1w"):
        htf_candles = candles_by_tf.get(htf) or []
        if len(htf_candles) < 8:
            continue

        atr_htf = calc_atr(htf_candles, min(14, len(htf_candles) - 1))
        recent = htf_candles[-8:]

        # Bullish HTF POI (FVG or bullish impulse base near current price)
        for i in range(2, len(recent)):
            c0, c1, c2 = recent[i - 2], recent[i - 1], recent[i]
            if c0["high"] < c2["low"] and (c1["close"] - c1["open"]) > atr_htf * 0.4:
                poi_low, poi_high = c0["high"], max(c2["low"], c1["close"])
                if live_price >= poi_low - (0.5 * atr_htf) and live_price <= poi_high + (0.5 * atr_htf):
                    return "BULLISH"

        # Bearish HTF POI (FVG or bearish impulse supply near current price)
        for i in range(2, len(recent)):
            c0, c1, c2 = recent[i - 2], recent[i - 1], recent[i]
            if c0["low"] > c2["high"] and (c1["open"] - c1["close"]) > atr_htf * 0.4:
                poi_high, poi_low = c0["low"], min(c2["high"], c1["close"])
                if live_price >= poi_low - (0.5 * atr_htf) and live_price <= poi_high + (0.5 * atr_htf):
                    return "BEARISH"

        # Major swing level reaction fallback
        swing_low = min(c["low"] for c in recent[:-1])
        swing_high = max(c["high"] for c in recent[:-1])
        if abs(live_price - swing_low) <= atr_htf * 0.6 and recent[-1]["close"] >= swing_low:
            return "BULLISH"
        if abs(live_price - swing_high) <= atr_htf * 0.6 and recent[-1]["close"] <= swing_high:
            return "BEARISH"

    return "NEUTRAL"


def _has_institutional_reference_confluence(symbol, market, zone_low, zone_high, atr):
    """
    Strategy #5: Checks whether the OB / retest zone aligns with or sits near
    a relevant Institutional Reference Number (psychological / round figure level).
    """
    mid_price = (zone_low + zone_high) / 2.0
    if mid_price <= 0:
        return False

    sym_upper = (symbol or "").upper()
    if sym_upper in NSE_INDEX_SYMBOLS or mid_price >= 50000:
        step = 100.0 if mid_price < 50000 else 500.0
    elif mid_price >= 5000:
        step = 50.0
    elif mid_price >= 500:
        step = 10.0
    elif mid_price >= 50:
        step = 5.0
    else:
        step = 1.0

    nearest_lower = (mid_price // step) * step
    nearest_upper = nearest_lower + step
    tolerance = max(atr * 0.65, step * 0.12)

    if zone_low <= nearest_lower <= zone_high or zone_low <= nearest_upper <= zone_high:
        return True
    if abs(mid_price - nearest_lower) <= tolerance or abs(mid_price - nearest_upper) <= tolerance:
        return True
    return False


def _extract_anchor_liquidity(lookback, style):
    """
    Strategy #6: Isolated timeframe-local anchor liquidity levels (PDH/PDL or PWH/PWL
    approximated from prior session/period block + swing pools) without cross-TF state.
    """
    if len(lookback) < 12:
        return None, None
    prior_block = lookback[:-8] if style == "Intraday" else lookback[:-10]
    if not prior_block:
        return None, None
    anchor_high = max(c["high"] for c in prior_block)
    anchor_low = min(c["low"] for c in prior_block)
    return anchor_high, anchor_low


def _find_swing_lows(candles, left=2, right=2):
    lows = []
    for i in range(left, len(candles) - right):
        low_val = candles[i]["low"]
        if all(low_val <= candles[i - j]["low"] for j in range(1, left + 1)) and all(
            low_val < candles[i + j]["low"] for j in range(1, right + 1)
        ):
            lows.append((i, low_val))
    return lows


def _find_swing_highs(candles, left=2, right=2):
    highs = []
    for i in range(left, len(candles) - right):
        high_val = candles[i]["high"]
        if all(high_val >= candles[i - j]["high"] for j in range(1, left + 1)) and all(
            high_val > candles[i + j]["high"] for j in range(1, right + 1)
        ):
            highs.append((i, high_val))
    return highs


# ==============================================================================
# STRATEGY #1: ICT 2022 MODEL
# ==============================================================================
def evaluate_ict_2022_tf(symbol, market, style, tf, candles, live_price, htf_bias="NEUTRAL", now_dt=None):
    """
    Isolated single-timeframe state evaluation for ICT 2022 Model (LONG & SHORT).
    Returns list of setup dicts for active trade tracking & alert formatting.
    """
    if not candles or len(candles) < 35:
        return []

    if style == "Swing" and htf_bias == "NEUTRAL":
        return []

    now_str = format_ist_timestamp(now_dt)
    setups = []
    atr = calc_atr(candles, 14)
    base_vol = avg_volume(candles[:-1], 20)
    is_nse_index = market == "NSE" and symbol.upper() in NSE_INDEX_SYMBOLS
    vol_available = base_vol > 0 and not is_nse_index

    lookback = candles[-30:]
    curr = lookback[-1]
    prev = lookback[-2]

    swing_lows = _find_swing_lows(lookback[:-4], 2, 2)
    swing_highs = _find_swing_highs(lookback[:-4], 2, 2)

    # ---------------- LONG ENTRY LOGIC (BULLISH ICT 2022) ----------------
    if (style == "Intraday" or htf_bias == "BULLISH") and swing_lows and swing_highs:
        ssl_idx, ssl_level = swing_lows[-1]
        post_ssl = lookback[ssl_idx + 1 :]

        if len(post_ssl) >= 5:
            sweep_candle = min(post_ssl[:-2], key=lambda c: c["low"])
            sweep_low = sweep_candle["low"]
            sweep_idx = post_ssl.index(sweep_candle)

            if sweep_low < ssl_level:
                cp1_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.15)

                after_sweep = post_ssl[sweep_idx + 1 :]
                prior_highs = [h for idx, h in swing_highs if idx <= ssl_idx + sweep_idx]
                mss_target = prior_highs[-1] if prior_highs else max(c["high"] for c in lookback[: ssl_idx + 1])

                disp_high = max((c["high"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] > mss_target for c in after_sweep)

                fvg_zone = None
                cp2_ok = False
                for i in range(2, len(after_sweep)):
                    c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                    if c0["high"] < c2["low"] and (c1["close"] - c1["open"]) > atr * 0.6:
                        fvg_zone = (c0["high"], c2["low"])
                        if (not vol_available) or (c1.get("volume", 0) >= base_vol * 1.2):
                            cp2_ok = True
                        break

                if cp1_ok and mss_broken and fvg_zone and cp2_ok and disp_high > sweep_low:
                    leg_range = disp_high - sweep_low
                    ote_top = disp_high - (0.618 * leg_range)
                    ote_bottom = disp_high - (0.786 * leg_range)

                    zone_high = max(ote_top, fvg_zone[1])
                    zone_low = min(ote_bottom, fvg_zone[0])

                    invalidated = any(c["low"] < sweep_low for c in after_sweep[-3:]) or live_price < sweep_low

                    in_ote = (prev["low"] <= zone_high and prev["close"] >= ote_bottom) or (
                        curr["low"] <= zone_high and curr["close"] >= ote_bottom
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)

                    bullish_confirm = curr["close"] > curr["open"] and curr["low"] <= zone_high
                    if not invalidated and in_ote and cp3_ok and bullish_confirm and live_price > curr["high"]:
                        entry = float(live_price)
                        sl = float(sweep_low - (0.15 * atr))
                        risk = entry - sl
                        if risk > 0:
                            tp1 = float(disp_high)
                            tp2 = float(max(disp_high + risk, entry + (2.5 * risk)))
                            rr = (tp2 - entry) / risk
                            if rr >= 2.0:
                                be_price = float(entry + risk)
                                setups.append({
                                    "trade_id": f"STRAT01_{symbol}_{market}_{style}_{tf}_LONG_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_1_CONFIG["name"],
                                    "direction": "LONG",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    # ---------------- SHORT SELL LOGIC (BEARISH ICT 2022) ----------------
    if (style == "Intraday" or htf_bias == "BEARISH") and swing_highs and swing_lows:
        bsl_idx, bsl_level = swing_highs[-1]
        post_bsl = lookback[bsl_idx + 1 :]

        if len(post_bsl) >= 5:
            sweep_candle = max(post_bsl[:-2], key=lambda c: c["high"])
            sweep_high = sweep_candle["high"]
            sweep_idx = post_bsl.index(sweep_candle)

            if sweep_high > bsl_level:
                cp1_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.15)

                after_sweep = post_bsl[sweep_idx + 1 :]
                prior_lows = [l for idx, l in swing_lows if idx <= bsl_idx + sweep_idx]
                mss_target = prior_lows[-1] if prior_lows else min(c["low"] for c in lookback[: bsl_idx + 1])

                disp_low = min((c["low"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] < mss_target for c in after_sweep)

                fvg_zone = None
                cp2_ok = False
                for i in range(2, len(after_sweep)):
                    c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                    if c0["low"] > c2["high"] and (c1["open"] - c1["close"]) > atr * 0.6:
                        fvg_zone = (c2["high"], c0["low"])
                        if (not vol_available) or (c1.get("volume", 0) >= base_vol * 1.2):
                            cp2_ok = True
                        break

                if cp1_ok and mss_broken and fvg_zone and cp2_ok and sweep_high > disp_low:
                    leg_range = sweep_high - disp_low
                    ote_bottom = disp_low + (0.618 * leg_range)
                    ote_top = disp_low + (0.786 * leg_range)

                    zone_low = min(ote_bottom, fvg_zone[0])
                    zone_high = max(ote_top, fvg_zone[1])

                    invalidated = any(c["high"] > sweep_high for c in after_sweep[-3:]) or live_price > sweep_high

                    in_ote = (prev["high"] >= zone_low and prev["close"] <= ote_top) or (
                        curr["high"] >= zone_low and curr["close"] <= ote_top
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)

                    bearish_confirm = curr["close"] < curr["open"] and curr["high"] >= zone_low
                    if not invalidated and in_ote and cp3_ok and bearish_confirm and live_price < curr["low"]:
                        entry = float(live_price)
                        sl = float(sweep_high + (0.15 * atr))
                        risk = sl - entry
                        if risk > 0:
                            tp1 = float(disp_low)
                            tp2 = float(min(disp_low - risk, entry - (2.5 * risk)))
                            rr = (entry - tp2) / risk
                            if rr >= 2.0:
                                be_price = float(entry - risk)
                                setups.append({
                                    "trade_id": f"STRAT01_{symbol}_{market}_{style}_{tf}_SHORT_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_1_CONFIG["name"],
                                    "direction": "SHORT",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    return setups


# ==============================================================================
# STRATEGY #2: SILVER BULLET SETUP (STRICTLY INTRADAY, NO HTF BIAS)
# ==============================================================================
def evaluate_silver_bullet_tf(symbol, market, tf, candles, live_price, now_dt=None):
    """
    Isolated single-timeframe state evaluation for Silver Bullet Setup (LONG & SHORT).
    Strictly Intraday (Swing OFF, No HTF confirmation required).
    """
    if not candles or len(candles) < 35:
        return []

    now_str = format_ist_timestamp(now_dt)
    setups = []
    atr = calc_atr(candles, 14)
    base_vol = avg_volume(candles[:-1], 20)
    is_nse_index = market == "NSE" and symbol.upper() in NSE_INDEX_SYMBOLS
    vol_available = base_vol > 0 and not is_nse_index

    lookback = candles[-24:]
    curr = lookback[-1]
    prev = lookback[-2]

    swing_lows = _find_swing_lows(lookback[:-4], 2, 2)
    swing_highs = _find_swing_highs(lookback[:-4], 2, 2)

    # ---------------- LONG ENTRY LOGIC (BULLISH SILVER BULLET) ----------------
    if swing_lows and swing_highs:
        ssl_idx, ssl_level = swing_lows[-1]
        post_ssl = lookback[ssl_idx + 1 :]

        if len(post_ssl) >= 4:
            sweep_candle = min(post_ssl[:-2], key=lambda c: c["low"])
            sweep_low = sweep_candle["low"]
            sweep_idx = post_ssl.index(sweep_candle)

            if sweep_low < ssl_level:
                cp1_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.15)

                after_sweep = post_ssl[sweep_idx + 1 :]
                prior_highs = [h for idx, h in swing_highs if idx <= ssl_idx + sweep_idx]
                mss_target = prior_highs[-1] if prior_highs else max(c["high"] for c in lookback[: ssl_idx + 1])

                disp_high = max((c["high"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] > mss_target for c in after_sweep)

                fvg_zone = None
                cp2_ok = False
                for i in range(2, len(after_sweep)):
                    c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                    if c0["high"] < c2["low"] and (c1["close"] - c1["open"]) > atr * 0.55:
                        fvg_zone = (c0["high"], c2["low"])
                        if (not vol_available) or (c1.get("volume", 0) >= base_vol * 1.2):
                            cp2_ok = True
                        break

                if cp1_ok and mss_broken and fvg_zone and cp2_ok and disp_high > sweep_low:
                    fvg_bottom, fvg_top = fvg_zone

                    invalidated = any(c["low"] < sweep_low for c in after_sweep[-3:]) or live_price < sweep_low

                    in_fvg = (prev["low"] <= fvg_top and prev["close"] >= fvg_bottom) or (
                        curr["low"] <= fvg_top and curr["close"] >= fvg_bottom
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)

                    bullish_confirm = curr["close"] > curr["open"] and curr["low"] <= fvg_top
                    if not invalidated and in_fvg and cp3_ok and bullish_confirm and live_price > curr["high"]:
                        entry = float(live_price)
                        sl = float(sweep_low - (0.15 * atr))
                        risk = entry - sl
                        if risk > 0:
                            tp1 = float(disp_high)
                            next_highs = [h for _, h in swing_highs if h > disp_high]
                            pool_tp2 = next_highs[0] if next_highs else (disp_high + risk)
                            tp2 = float(max(pool_tp2, entry + (2.0 * risk)))
                            rr = (tp2 - entry) / risk
                            if rr >= 2.0:
                                be_price = float(entry + risk)
                                setups.append({
                                    "trade_id": f"STRAT02_{symbol}_{market}_Intraday_{tf}_LONG_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_2_CONFIG["name"],
                                    "direction": "LONG",
                                    "style": "Intraday",
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    # ---------------- SHORT SELL LOGIC (BEARISH SILVER BULLET) ----------------
    if swing_highs and swing_lows:
        bsl_idx, bsl_level = swing_highs[-1]
        post_bsl = lookback[bsl_idx + 1 :]

        if len(post_bsl) >= 4:
            sweep_candle = max(post_bsl[:-2], key=lambda c: c["high"])
            sweep_high = sweep_candle["high"]
            sweep_idx = post_bsl.index(sweep_candle)

            if sweep_high > bsl_level:
                cp1_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.15)

                after_sweep = post_bsl[sweep_idx + 1 :]
                prior_lows = [l for idx, l in swing_lows if idx <= bsl_idx + sweep_idx]
                mss_target = prior_lows[-1] if prior_lows else min(c["low"] for c in lookback[: bsl_idx + 1])

                disp_low = min((c["low"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] < mss_target for c in after_sweep)

                fvg_zone = None
                cp2_ok = False
                for i in range(2, len(after_sweep)):
                    c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                    if c0["low"] > c2["high"] and (c1["open"] - c1["close"]) > atr * 0.55:
                        fvg_zone = (c2["high"], c0["low"])
                        if (not vol_available) or (c1.get("volume", 0) >= base_vol * 1.2):
                            cp2_ok = True
                        break

                if cp1_ok and mss_broken and fvg_zone and cp2_ok and sweep_high > disp_low:
                    fvg_bottom, fvg_top = fvg_zone

                    invalidated = any(c["high"] > sweep_high for c in after_sweep[-3:]) or live_price > sweep_high

                    in_fvg = (prev["high"] >= fvg_bottom and prev["close"] <= fvg_top) or (
                        curr["high"] >= fvg_bottom and curr["close"] <= fvg_top
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)

                    bearish_confirm = curr["close"] < curr["open"] and curr["high"] >= fvg_bottom
                    if not invalidated and in_fvg and cp3_ok and bearish_confirm and live_price < curr["low"]:
                        entry = float(live_price)
                        sl = float(sweep_high + (0.15 * atr))
                        risk = sl - entry
                        if risk > 0:
                            tp1 = float(disp_low)
                            next_lows = [l for _, l in swing_lows if l < disp_low]
                            pool_tp2 = next_lows[-1] if next_lows else (disp_low - risk)
                            tp2 = float(min(pool_tp2, entry - (2.0 * risk)))
                            rr = (entry - tp2) / risk
                            if rr >= 2.0:
                                be_price = float(entry - risk)
                                setups.append({
                                    "trade_id": f"STRAT02_{symbol}_{market}_Intraday_{tf}_SHORT_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_2_CONFIG["name"],
                                    "direction": "SHORT",
                                    "style": "Intraday",
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    return setups


# ==============================================================================
# STRATEGY #3: POWER OF 3 — AMD (INTRADAY & HTF POI SWING)
# ==============================================================================
def evaluate_po3_amd_tf(symbol, market, style, tf, candles, live_price, htf_poi_bias="NEUTRAL", now_dt=None):
    """
    Isolated single-timeframe state evaluation for Power of 3 (AMD) Setup (LONG & SHORT).
    Intraday: standalone AMD cycle (No killzone filter).
    Swing: requires HTF POI confluence (4H / 1D / 1W).
    """
    if not candles or len(candles) < 35:
        return []

    if style == "Swing" and htf_poi_bias == "NEUTRAL":
        return []

    now_str = format_ist_timestamp(now_dt)
    setups = []
    atr = calc_atr(candles, 14)
    base_vol = avg_volume(candles[:-1], 20)
    is_nse_index = market == "NSE" and symbol.upper() in NSE_INDEX_SYMBOLS
    vol_available = base_vol > 0 and not is_nse_index

    lookback = candles[-30:]
    curr = lookback[-1]
    prev = lookback[-2]

    # ---------------- LONG ENTRY LOGIC (BULLISH POWER OF 3 — AMD) ----------------
    if style == "Intraday" or htf_poi_bias == "BULLISH":
        for box_start in range(len(lookback) - 14, len(lookback) - 7):
            if box_start < 2:
                continue
            acc_candles = lookback[box_start : box_start + 4]
            acc_high = max(c["high"] for c in acc_candles)
            acc_low = min(c["low"] for c in acc_candles)
            acc_range = acc_high - acc_low

            if acc_range <= 0 or acc_range > atr * 1.4:
                continue

            acc_vols = [c.get("volume", 0) or 0 for c in acc_candles]
            acc_avg_vol = (sum(acc_vols) / len(acc_vols)) if acc_vols else 0.0
            cp1_ok = (not vol_available) or (acc_avg_vol <= base_vol * 1.05)

            post_acc = lookback[box_start + 4 :]
            if len(post_acc) < 3 or not cp1_ok:
                continue

            trap_candidates = post_acc[:-1]
            judas_candle = min(trap_candidates, key=lambda c: c["low"])
            judas_low = judas_candle["low"]
            judas_idx = post_acc.index(judas_candle)

            if judas_low < acc_low:
                cp2_trap_ok = (not vol_available) or (judas_candle.get("volume", 0) >= base_vol * 1.1)

                after_judas = post_acc[judas_idx + 1 :]
                mss_target = max(acc_high, max(c["high"] for c in lookback[box_start : box_start + 4 + judas_idx]))
                disp_high = max((c["high"] for c in after_judas), default=0)
                mss_broken = any(c["close"] > mss_target for c in after_judas)

                poi_zone = None
                cp2_disp_ok = False
                for i in range(len(after_judas)):
                    c_item = after_judas[i]
                    if (c_item["close"] - c_item["open"]) > atr * 0.5:
                        if (not vol_available) or (c_item.get("volume", 0) >= base_vol * 1.15):
                            cp2_disp_ok = True
                        if i >= 2:
                            c0, c1, c2 = after_judas[i - 2], after_judas[i - 1], after_judas[i]
                            if c0["high"] < c2["low"]:
                                poi_zone = (c0["high"], c2["low"])
                                break
                        if poi_zone is None:
                            poi_zone = (c_item["low"], max(c_item["open"], c_item["close"]))
                            break

                if cp2_trap_ok and mss_broken and poi_zone and cp2_disp_ok and disp_high > judas_low:
                    zone_low, zone_high = min(poi_zone), max(poi_zone)
                    invalidated = any(c["low"] < judas_low for c in after_judas[-3:]) or live_price < judas_low

                    in_pullback = (prev["low"] <= zone_high and prev["close"] >= zone_low) or (
                        curr["low"] <= zone_high and curr["close"] >= zone_low
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    bullish_confirm = curr["close"] > curr["open"] and curr["low"] <= zone_high

                    if not invalidated and in_pullback and cp3_ok and bullish_confirm and live_price > curr["high"]:
                        entry = float(live_price)
                        sl = float(judas_low - (0.15 * atr))
                        risk = entry - sl
                        if risk > 0:
                            tp1 = float(max(acc_high, disp_high))
                            tp2 = float(max(tp1 + risk, entry + (2.2 * risk)))
                            rr = (tp2 - entry) / risk
                            if rr >= 2.0:
                                be_price = float(entry + risk)
                                setups.append({
                                    "trade_id": f"STRAT03_{symbol}_{market}_{style}_{tf}_LONG_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_3_CONFIG["name"],
                                    "direction": "LONG",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })
                        break

    # ---------------- SHORT SELL LOGIC (BEARISH POWER OF 3 — AMD) ----------------
    if style == "Intraday" or htf_poi_bias == "BEARISH":
        for box_start in range(len(lookback) - 14, len(lookback) - 7):
            if box_start < 2:
                continue
            acc_candles = lookback[box_start : box_start + 4]
            acc_high = max(c["high"] for c in acc_candles)
            acc_low = min(c["low"] for c in acc_candles)
            acc_range = acc_high - acc_low

            if acc_range <= 0 or acc_range > atr * 1.4:
                continue

            acc_vols = [c.get("volume", 0) or 0 for c in acc_candles]
            acc_avg_vol = (sum(acc_vols) / len(acc_vols)) if acc_vols else 0.0
            cp1_ok = (not vol_available) or (acc_avg_vol <= base_vol * 1.05)

            post_acc = lookback[box_start + 4 :]
            if len(post_acc) < 3 or not cp1_ok:
                continue

            trap_candidates = post_acc[:-1]
            judas_candle = max(trap_candidates, key=lambda c: c["high"])
            judas_high = judas_candle["high"]
            judas_idx = post_acc.index(judas_candle)

            if judas_high > acc_high:
                cp2_trap_ok = (not vol_available) or (judas_candle.get("volume", 0) >= base_vol * 1.1)

                after_judas = post_acc[judas_idx + 1 :]
                mss_target = min(acc_low, min(c["low"] for c in lookback[box_start : box_start + 4 + judas_idx]))
                disp_low = min((c["low"] for c in after_judas), default=0)
                mss_broken = any(c["close"] < mss_target for c in after_judas)

                poi_zone = None
                cp2_disp_ok = False
                for i in range(len(after_judas)):
                    c_item = after_judas[i]
                    if (c_item["open"] - c_item["close"]) > atr * 0.5:
                        if (not vol_available) or (c_item.get("volume", 0) >= base_vol * 1.15):
                            cp2_disp_ok = True
                        if i >= 2:
                            c0, c1, c2 = after_judas[i - 2], after_judas[i - 1], after_judas[i]
                            if c0["low"] > c2["high"]:
                                poi_zone = (c2["high"], c0["low"])
                                break
                        if poi_zone is None:
                            poi_zone = (min(c_item["open"], c_item["close"]), c_item["high"])
                            break

                if cp2_trap_ok and mss_broken and poi_zone and cp2_disp_ok and judas_high > disp_low:
                    zone_low, zone_high = min(poi_zone), max(poi_zone)
                    invalidated = any(c["high"] > judas_high for c in after_judas[-3:]) or live_price > judas_high

                    in_pullback = (prev["high"] >= zone_low and prev["close"] <= zone_high) or (
                        curr["high"] >= zone_low and curr["close"] <= zone_high
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    bearish_confirm = curr["close"] < curr["open"] and curr["high"] >= zone_low

                    if not invalidated and in_pullback and cp3_ok and bearish_confirm and live_price < curr["low"]:
                        entry = float(live_price)
                        sl = float(judas_high + (0.15 * atr))
                        risk = sl - entry
                        if risk > 0:
                            tp1 = float(min(acc_low, disp_low))
                            tp2 = float(min(tp1 - risk, entry - (2.2 * risk)))
                            rr = (entry - tp2) / risk
                            if rr >= 2.0:
                                be_price = float(entry - risk)
                                setups.append({
                                    "trade_id": f"STRAT03_{symbol}_{market}_{style}_{tf}_SHORT_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_3_CONFIG["name"],
                                    "direction": "SHORT",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })
                        break

    return setups


# ==============================================================================
# STRATEGY #4: MARKET MAKER BUY/SELL MODEL — MMMS (INTRADAY & HTF POI SWING)
# ==============================================================================
def evaluate_mmms_tf(symbol, market, style, tf, candles, live_price, htf_poi_bias="NEUTRAL", now_dt=None):
    """
    Isolated single-timeframe state evaluation for Market Maker Buy/Sell Model (MMMS).
    Supports LONG (MMBM) and SHORT (MMSM) across Intraday and Swing (with HTF POI).
    No killzone filter.
    """
    if not candles or len(candles) < 35:
        return []

    if style == "Swing" and htf_poi_bias == "NEUTRAL":
        return []

    now_str = format_ist_timestamp(now_dt)
    setups = []
    atr = calc_atr(candles, 14)
    base_vol = avg_volume(candles[:-1], 20)
    is_nse_index = market == "NSE" and symbol.upper() in NSE_INDEX_SYMBOLS
    vol_available = base_vol > 0 and not is_nse_index

    lookback = candles[-32:]
    curr = lookback[-1]
    prev = lookback[-2]

    swing_lows = _find_swing_lows(lookback[:-4], 2, 2)
    swing_highs = _find_swing_highs(lookback[:-4], 2, 2)

    # ---------------- LONG ENTRY LOGIC (MMBM — MARKET MAKER BUY MODEL) ----------------
    if (style == "Intraday" or htf_poi_bias == "BULLISH") and swing_lows and swing_highs:
        ssl_idx, ssl_level = swing_lows[-1]
        post_ssl = lookback[ssl_idx + 1 :]

        if len(post_ssl) >= 4:
            eng_start = max(0, ssl_idx - 4)
            eng_candles = lookback[eng_start : ssl_idx + 1]
            eng_vols = [c.get("volume", 0) or 0 for c in eng_candles]
            eng_avg_vol = (sum(eng_vols) / len(eng_vols)) if eng_vols else 0.0
            cp1_ok = (not vol_available) or (eng_avg_vol <= base_vol * 1.25)

            sweep_candle = min(post_ssl[:-2], key=lambda c: c["low"])
            sweep_low = sweep_candle["low"]
            sweep_idx = post_ssl.index(sweep_candle)

            if sweep_low < ssl_level and cp1_ok:
                cp2_sweep_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.1)

                after_sweep = post_ssl[sweep_idx + 1 :]
                prior_highs = [h for idx, h in swing_highs if idx <= ssl_idx + sweep_idx]
                mss_target = prior_highs[-1] if prior_highs else max(c["high"] for c in lookback[: ssl_idx + 1])

                disp_high = max((c["high"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] > mss_target for c in after_sweep)

                void_zone = None
                cp2_disp_ok = False
                for i in range(len(after_sweep)):
                    c_item = after_sweep[i]
                    if (c_item["close"] - c_item["open"]) > atr * 0.55:
                        if (not vol_available) or (c_item.get("volume", 0) >= base_vol * 1.15):
                            cp2_disp_ok = True
                        if i >= 2:
                            c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                            if c0["high"] < c2["low"]:
                                void_zone = (c0["high"], c2["low"])
                                break
                        if void_zone is None:
                            void_zone = (c_item["low"], max(c_item["open"], c_item["close"]))
                            break

                if cp2_sweep_ok and mss_broken and void_zone and cp2_disp_ok and disp_high > sweep_low:
                    zone_low, zone_high = min(void_zone), max(void_zone)
                    invalidated = any(c["low"] < sweep_low for c in after_sweep[-3:]) or live_price < sweep_low

                    in_void = (prev["low"] <= zone_high and prev["close"] >= zone_low) or (
                        curr["low"] <= zone_high and curr["close"] >= zone_low
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    bullish_confirm = curr["close"] > curr["open"] and curr["low"] <= zone_high

                    if not invalidated and in_void and cp3_ok and bullish_confirm and live_price > curr["high"]:
                        entry = float(live_price)
                        sl = float(sweep_low - (0.15 * atr))
                        risk = entry - sl
                        if risk > 0:
                            tp1 = float(max(mss_target, disp_high))
                            opposing_highs = [h for _, h in swing_highs if h > tp1]
                            pool_tp2 = opposing_highs[0] if opposing_highs else (tp1 + risk)
                            tp2 = float(max(pool_tp2, entry + (2.2 * risk)))
                            rr = (tp2 - entry) / risk
                            if rr >= 2.0:
                                be_price = float(entry + risk)
                                setups.append({
                                    "trade_id": f"STRAT04_{symbol}_{market}_{style}_{tf}_LONG_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_4_CONFIG["name"],
                                    "direction": "LONG",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    # ---------------- SHORT SELL LOGIC (MMSM — MARKET MAKER SELL MODEL) ----------------
    if (style == "Intraday" or htf_poi_bias == "BEARISH") and swing_highs and swing_lows:
        bsl_idx, bsl_level = swing_highs[-1]
        post_bsl = lookback[bsl_idx + 1 :]

        if len(post_bsl) >= 4:
            eng_start = max(0, bsl_idx - 4)
            eng_candles = lookback[eng_start : bsl_idx + 1]
            eng_vols = [c.get("volume", 0) or 0 for c in eng_candles]
            eng_avg_vol = (sum(eng_vols) / len(eng_vols)) if eng_vols else 0.0
            cp1_ok = (not vol_available) or (eng_avg_vol <= base_vol * 1.25)

            sweep_candle = max(post_bsl[:-2], key=lambda c: c["high"])
            sweep_high = sweep_candle["high"]
            sweep_idx = post_bsl.index(sweep_candle)

            if sweep_high > bsl_level and cp1_ok:
                cp2_sweep_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.1)

                after_sweep = post_bsl[sweep_idx + 1 :]
                prior_lows = [l for idx, l in swing_lows if idx <= bsl_idx + sweep_idx]
                mss_target = prior_lows[-1] if prior_lows else min(c["low"] for c in lookback[: bsl_idx + 1])

                disp_low = min((c["low"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] < mss_target for c in after_sweep)

                void_zone = None
                cp2_disp_ok = False
                for i in range(len(after_sweep)):
                    c_item = after_sweep[i]
                    if (c_item["open"] - c_item["close"]) > atr * 0.55:
                        if (not vol_available) or (c_item.get("volume", 0) >= base_vol * 1.15):
                            cp2_disp_ok = True
                        if i >= 2:
                            c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                            if c0["low"] > c2["high"]:
                                void_zone = (c2["high"], c0["low"])
                                break
                        if void_zone is None:
                            void_zone = (min(c_item["open"], c_item["close"]), c_item["high"])
                            break

                if cp2_sweep_ok and mss_broken and void_zone and cp2_disp_ok and sweep_high > disp_low:
                    zone_low, zone_high = min(void_zone), max(void_zone)
                    invalidated = any(c["high"] > sweep_high for c in after_sweep[-3:]) or live_price > sweep_high

                    in_void = (prev["high"] >= zone_low and prev["close"] <= zone_high) or (
                        curr["high"] >= zone_low and curr["close"] <= zone_high
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    bearish_confirm = curr["close"] < curr["open"] and curr["high"] >= zone_low

                    if not invalidated and in_void and cp3_ok and bearish_confirm and live_price < curr["low"]:
                        entry = float(live_price)
                        sl = float(sweep_high + (0.15 * atr))
                        risk = sl - entry
                        if risk > 0:
                            tp1 = float(min(mss_target, disp_low))
                            opposing_lows = [l for _, l in swing_lows if l < tp1]
                            pool_tp2 = opposing_lows[-1] if opposing_lows else (tp1 - risk)
                            tp2 = float(min(pool_tp2, entry - (2.2 * risk)))
                            rr = (entry - tp2) / risk
                            if rr >= 2.0:
                                be_price = float(entry - risk)
                                setups.append({
                                    "trade_id": f"STRAT04_{symbol}_{market}_{style}_{tf}_SHORT_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_4_CONFIG["name"],
                                    "direction": "SHORT",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    return setups


# ==============================================================================
# STRATEGY #5: ORDER BLOCK (OB) RETEST MODEL (INTRADAY & HTF POI SWING)
# ==============================================================================
def evaluate_ob_retest_tf(symbol, market, style, tf, candles, live_price, htf_poi_bias="NEUTRAL", now_dt=None):
    """
    Isolated single-timeframe state evaluation for Order Block (OB) Retest Model.
    Includes Dealing Range Premium/Discount alignment, Institutional Reference Number
    confluence, Liquidity Sweep + Displaced MSS, OB 50% Mean Threshold, and 3 Volume CPs.
    No killzone filter.
    """
    if not candles or len(candles) < 35:
        return []

    if style == "Swing" and htf_poi_bias == "NEUTRAL":
        return []

    now_str = format_ist_timestamp(now_dt)
    setups = []
    atr = calc_atr(candles, 14)
    base_vol = avg_volume(candles[:-1], 20)
    is_nse_index = market == "NSE" and symbol.upper() in NSE_INDEX_SYMBOLS
    vol_available = base_vol > 0 and not is_nse_index

    lookback = candles[-32:]
    curr = lookback[-1]
    prev = lookback[-2]

    range_high = max(c["high"] for c in lookback[:-2])
    range_low = min(c["low"] for c in lookback[:-2])
    eq_50 = (range_high + range_low) / 2.0

    swing_lows = _find_swing_lows(lookback[:-4], 2, 2)
    swing_highs = _find_swing_highs(lookback[:-4], 2, 2)

    # ---------------- LONG ENTRY LOGIC (BULLISH OB RETEST — DISCOUNT) ----------------
    if (style == "Intraday" or htf_poi_bias == "BULLISH") and swing_lows and swing_highs and range_high > range_low:
        ssl_idx, ssl_level = swing_lows[-1]
        post_ssl = lookback[ssl_idx + 1 :]

        if len(post_ssl) >= 4:
            sweep_candle = min(post_ssl[:-2], key=lambda c: c["low"])
            sweep_low = sweep_candle["low"]
            sweep_idx = post_ssl.index(sweep_candle)

            if sweep_low < ssl_level:
                after_sweep = post_ssl[sweep_idx + 1 :]
                prior_highs = [h for idx, h in swing_highs if idx <= ssl_idx + sweep_idx]
                mss_target = prior_highs[-1] if prior_highs else max(c["high"] for c in lookback[: ssl_idx + 1])

                disp_high = max((c["high"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] > mss_target for c in after_sweep)

                bull_ob = None
                cp1_ok = False
                for i in range(len(after_sweep)):
                    c_disp = after_sweep[i]
                    if (c_disp["close"] - c_disp["open"]) > atr * 0.55:
                        cp1_ok = (not vol_available) or (c_disp.get("volume", 0) >= base_vol * 1.15)
                        candidates = list(reversed(lookback[: ssl_idx + 1 + sweep_idx + 1 + i]))
                        for cand in candidates:
                            if cand["close"] < cand["open"]:
                                bull_ob = (cand["low"], cand["high"])
                                break
                        break

                if bull_ob and cp1_ok and mss_broken and disp_high > sweep_low:
                    ob_low, ob_high = bull_ob
                    ob_mean_50 = (ob_low + ob_high) / 2.0

                    in_discount = ob_mean_50 <= eq_50
                    inst_ref_ok = _has_institutional_reference_confluence(symbol, market, ob_low, ob_high, atr)

                    body_broke_mean = any(c["close"] < ob_mean_50 for c in after_sweep[-3:]) or (curr["close"] < ob_mean_50)
                    broke_ob_low = any(c["low"] < ob_low for c in after_sweep[-3:]) or (live_price < ob_low)
                    invalidated = body_broke_mean or broke_ob_low

                    cp2_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    cp3_ok = (not vol_available) or (curr.get("volume", 0) <= base_vol * 1.35)

                    retest_touch = (prev["low"] <= ob_high and prev["close"] >= ob_mean_50) or (
                        curr["low"] <= ob_high and curr["close"] >= ob_mean_50
                    )
                    bullish_confirm = curr["close"] > curr["open"] and curr["low"] <= ob_high

                    if (
                        in_discount
                        and inst_ref_ok
                        and not invalidated
                        and cp2_ok
                        and cp3_ok
                        and retest_touch
                        and bullish_confirm
                        and live_price > curr["high"]
                    ):
                        entry = float(live_price)
                        sl = float(ob_low - (0.15 * atr))
                        risk = entry - sl
                        if risk > 0:
                            tp1 = float(max(eq_50, disp_high))
                            tp2 = float(max(range_high, entry + (2.2 * risk)))
                            rr = (tp2 - entry) / risk
                            if rr >= 2.0:
                                be_price = float(entry + risk)
                                setups.append({
                                    "trade_id": f"STRAT05_{symbol}_{market}_{style}_{tf}_LONG_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_5_CONFIG["name"],
                                    "direction": "LONG",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    # ---------------- SHORT SELL LOGIC (BEARISH OB RETEST — PREMIUM) ----------------
    if (style == "Intraday" or htf_poi_bias == "BEARISH") and swing_highs and swing_lows and range_high > range_low:
        bsl_idx, bsl_level = swing_highs[-1]
        post_bsl = lookback[bsl_idx + 1 :]

        if len(post_bsl) >= 4:
            sweep_candle = max(post_bsl[:-2], key=lambda c: c["high"])
            sweep_high = sweep_candle["high"]
            sweep_idx = post_bsl.index(sweep_candle)

            if sweep_high > bsl_level:
                after_sweep = post_bsl[sweep_idx + 1 :]
                prior_lows = [l for idx, l in swing_lows if idx <= bsl_idx + sweep_idx]
                mss_target = prior_lows[-1] if prior_lows else min(c["low"] for c in lookback[: bsl_idx + 1])

                disp_low = min((c["low"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] < mss_target for c in after_sweep)

                bear_ob = None
                cp1_ok = False
                for i in range(len(after_sweep)):
                    c_disp = after_sweep[i]
                    if (c_disp["open"] - c_disp["close"]) > atr * 0.55:
                        cp1_ok = (not vol_available) or (c_disp.get("volume", 0) >= base_vol * 1.15)
                        candidates = list(reversed(lookback[: bsl_idx + 1 + sweep_idx + 1 + i]))
                        for cand in candidates:
                            if cand["close"] > cand["open"]:
                                bear_ob = (cand["low"], cand["high"])
                                break
                        break

                if bear_ob and cp1_ok and mss_broken and sweep_high > disp_low:
                    ob_low, ob_high = bear_ob
                    ob_mean_50 = (ob_low + ob_high) / 2.0

                    in_premium = ob_mean_50 >= eq_50
                    inst_ref_ok = _has_institutional_reference_confluence(symbol, market, ob_low, ob_high, atr)

                    body_broke_mean = any(c["close"] > ob_mean_50 for c in after_sweep[-3:]) or (curr["close"] > ob_mean_50)
                    broke_ob_high = any(c["high"] > ob_high for c in after_sweep[-3:]) or (live_price > ob_high)
                    invalidated = body_broke_mean or broke_ob_high

                    cp2_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    cp3_ok = (not vol_available) or (curr.get("volume", 0) <= base_vol * 1.35)

                    retest_touch = (prev["high"] >= ob_low and prev["close"] <= ob_mean_50) or (
                        curr["high"] >= ob_low and curr["close"] <= ob_mean_50
                    )
                    bearish_confirm = curr["close"] < curr["open"] and curr["high"] >= ob_low

                    if (
                        in_premium
                        and inst_ref_ok
                        and not invalidated
                        and cp2_ok
                        and cp3_ok
                        and retest_touch
                        and bearish_confirm
                        and live_price < curr["low"]
                    ):
                        entry = float(live_price)
                        sl = float(ob_high + (0.15 * atr))
                        risk = sl - entry
                        if risk > 0:
                            tp1 = float(min(eq_50, disp_low))
                            tp2 = float(min(range_low, entry - (2.2 * risk)))
                            rr = (entry - tp2) / risk
                            if rr >= 2.0:
                                be_price = float(entry - risk)
                                setups.append({
                                    "trade_id": f"STRAT05_{symbol}_{market}_{style}_{tf}_SHORT_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_5_CONFIG["name"],
                                    "direction": "SHORT",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    return setups


# ==============================================================================
# STRATEGY #6: LIQUIDITY SWEEP & REVERSAL MODEL (ISOLATED MULTI-TF STATE)
# ==============================================================================
def evaluate_liquidity_sweep_reversal_tf(symbol, market, style, tf, candles, live_price, htf_bias="NEUTRAL", now_dt=None):
    """
    Isolated single-timeframe state evaluation for Liquidity Sweep & Reversal Model.
    Uses timeframe-local anchor liquidity (PDH/PDL or PWH/PWL proxy + swing highs/lows),
    3 volume checkpoints (no volume filter on live entry break), Displaced MSS, FVG/OB pullback,
    and LONG / SHORT support across Intraday and Swing. No killzone filter.
    """
    if not candles or len(candles) < 35:
        return []

    if style == "Swing" and htf_bias == "NEUTRAL":
        return []

    now_str = format_ist_timestamp(now_dt)
    setups = []
    atr = calc_atr(candles, 14)
    base_vol = avg_volume(candles[:-1], 20)
    is_nse_index = market == "NSE" and symbol.upper() in NSE_INDEX_SYMBOLS
    vol_available = base_vol > 0 and not is_nse_index

    lookback = candles[-34:]
    curr = lookback[-1]
    prev = lookback[-2]

    anchor_high, anchor_low = _extract_anchor_liquidity(lookback, style)
    range_high = max(c["high"] for c in lookback[:-2])
    range_low = min(c["low"] for c in lookback[:-2])
    eq_50 = (range_high + range_low) / 2.0

    swing_lows = _find_swing_lows(lookback[:-4], 2, 2)
    swing_highs = _find_swing_highs(lookback[:-4], 2, 2)

    # ---------------- LONG ENTRY LOGIC (SSL SWEEP & BULLISH REVERSAL) ----------------
    if (style == "Intraday" or htf_bias == "BULLISH") and swing_lows and swing_highs:
        ssl_idx, ssl_swing = swing_lows[-1]
        ssl_level = min(ssl_swing, anchor_low) if anchor_low is not None else ssl_swing
        post_ssl = lookback[ssl_idx + 1 :]

        if len(post_ssl) >= 4:
            # CP1: Controlled / non-climactic volume during pre-sweep liquidity build
            pre_start = max(0, ssl_idx - 4)
            pre_candles = lookback[pre_start : ssl_idx + 1]
            pre_vols = [c.get("volume", 0) or 0 for c in pre_candles]
            pre_avg_vol = (sum(pre_vols) / len(pre_vols)) if pre_vols else 0.0
            cp1_ok = (not vol_available) or (pre_avg_vol <= base_vol * 1.25)

            # Step 2: Sweep below key SSL level + CP2 volume spike
            sweep_candle = min(post_ssl[:-2], key=lambda c: c["low"])
            sweep_low = sweep_candle["low"]
            sweep_idx = post_ssl.index(sweep_candle)

            if sweep_low < ssl_level and cp1_ok:
                cp2_sweep_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.1)

                # Step 3: Bullish Displaced MSS + FVG / OB creation + CP2 expanding volume
                after_sweep = post_ssl[sweep_idx + 1 :]
                prior_highs = [h for idx, h in swing_highs if idx <= ssl_idx + sweep_idx]
                mss_target = prior_highs[-1] if prior_highs else max(c["high"] for c in lookback[: ssl_idx + 1])

                disp_high = max((c["high"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] > mss_target for c in after_sweep)

                rev_zone = None
                cp2_disp_ok = False
                for i in range(len(after_sweep)):
                    c_item = after_sweep[i]
                    if (c_item["close"] - c_item["open"]) > atr * 0.55:
                        if (not vol_available) or (c_item.get("volume", 0) >= base_vol * 1.15):
                            cp2_disp_ok = True
                        if i >= 2:
                            c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                            if c0["high"] < c2["low"]:
                                rev_zone = (c0["high"], c2["low"])
                                break
                        if rev_zone is None:
                            rev_zone = (c_item["low"], max(c_item["open"], c_item["close"]))
                            break

                if cp2_sweep_ok and mss_broken and rev_zone and cp2_disp_ok and disp_high > sweep_low:
                    zone_low, zone_high = min(rev_zone), max(rev_zone)
                    invalidated = any(c["low"] < sweep_low for c in after_sweep[-3:]) or live_price < sweep_low

                    # Step 4: Pullback into FVG/OB with CP3 controlled volume + live entry break
                    in_pullback = (prev["low"] <= zone_high and prev["close"] >= zone_low) or (
                        curr["low"] <= zone_high and curr["close"] >= zone_low
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    bullish_confirm = curr["close"] > curr["open"] and curr["low"] <= zone_high

                    if not invalidated and in_pullback and cp3_ok and bullish_confirm and live_price > curr["high"]:
                        entry = float(live_price)
                        sl = float(sweep_low - (0.15 * atr))
                        risk = entry - sl
                        if risk > 0:
                            tp1 = float(max(eq_50, disp_high))
                            opposing_bsl = anchor_high if (anchor_high is not None and anchor_high > tp1) else range_high
                            tp2 = float(max(opposing_bsl, entry + (2.2 * risk)))
                            rr = (tp2 - entry) / risk
                            if rr >= 2.0:
                                be_price = float(entry + risk)
                                setups.append({
                                    "trade_id": f"STRAT06_{symbol}_{market}_{style}_{tf}_LONG_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_6_CONFIG["name"],
                                    "direction": "LONG",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    # ---------------- SHORT SELL LOGIC (BSL SWEEP & BEARISH REVERSAL) ----------------
    if (style == "Intraday" or htf_bias == "BEARISH") and swing_highs and swing_lows:
        bsl_idx, bsl_swing = swing_highs[-1]
        bsl_level = max(bsl_swing, anchor_high) if anchor_high is not None else bsl_swing
        post_bsl = lookback[bsl_idx + 1 :]

        if len(post_bsl) >= 4:
            # CP1: Controlled / non-climactic volume during pre-sweep liquidity build
            pre_start = max(0, bsl_idx - 4)
            pre_candles = lookback[pre_start : bsl_idx + 1]
            pre_vols = [c.get("volume", 0) or 0 for c in pre_candles]
            pre_avg_vol = (sum(pre_vols) / len(pre_vols)) if pre_vols else 0.0
            cp1_ok = (not vol_available) or (pre_avg_vol <= base_vol * 1.25)

            # Step 2: Sweep above key BSL level + CP2 volume spike
            sweep_candle = max(post_bsl[:-2], key=lambda c: c["high"])
            sweep_high = sweep_candle["high"]
            sweep_idx = post_bsl.index(sweep_candle)

            if sweep_high > bsl_level and cp1_ok:
                cp2_sweep_ok = (not vol_available) or (sweep_candle.get("volume", 0) >= base_vol * 1.1)

                # Step 3: Bearish Displaced MSS + FVG / OB creation + CP2 expanding volume
                after_sweep = post_bsl[sweep_idx + 1 :]
                prior_lows = [l for idx, l in swing_lows if idx <= bsl_idx + sweep_idx]
                mss_target = prior_lows[-1] if prior_lows else min(c["low"] for c in lookback[: bsl_idx + 1])

                disp_low = min((c["low"] for c in after_sweep), default=0)
                mss_broken = any(c["close"] < mss_target for c in after_sweep)

                rev_zone = None
                cp2_disp_ok = False
                for i in range(len(after_sweep)):
                    c_item = after_sweep[i]
                    if (c_item["open"] - c_item["close"]) > atr * 0.55:
                        if (not vol_available) or (c_item.get("volume", 0) >= base_vol * 1.15):
                            cp2_disp_ok = True
                        if i >= 2:
                            c0, c1, c2 = after_sweep[i - 2], after_sweep[i - 1], after_sweep[i]
                            if c0["low"] > c2["high"]:
                                rev_zone = (c2["high"], c0["low"])
                                break
                        if rev_zone is None:
                            rev_zone = (min(c_item["open"], c_item["close"]), c_item["high"])
                            break

                if cp2_sweep_ok and mss_broken and rev_zone and cp2_disp_ok and sweep_high > disp_low:
                    zone_low, zone_high = min(rev_zone), max(rev_zone)
                    invalidated = any(c["high"] > sweep_high for c in after_sweep[-3:]) or live_price > sweep_high

                    # Step 4: Pullback into FVG/OB with CP3 controlled volume + live entry break
                    in_pullback = (prev["high"] >= zone_low and prev["close"] <= zone_high) or (
                        curr["high"] >= zone_low and curr["close"] <= zone_high
                    )
                    cp3_ok = (not vol_available) or (prev.get("volume", 0) <= base_vol * 1.35)
                    bearish_confirm = curr["close"] < curr["open"] and curr["high"] >= zone_low

                    if not invalidated and in_pullback and cp3_ok and bearish_confirm and live_price < curr["low"]:
                        entry = float(live_price)
                        sl = float(sweep_high + (0.15 * atr))
                        risk = sl - entry
                        if risk > 0:
                            tp1 = float(min(eq_50, disp_low))
                            opposing_ssl = anchor_low if (anchor_low is not None and anchor_low < tp1) else range_low
                            tp2 = float(min(opposing_ssl, entry - (2.2 * risk)))
                            rr = (entry - tp2) / risk
                            if rr >= 2.0:
                                be_price = float(entry - risk)
                                setups.append({
                                    "trade_id": f"STRAT06_{symbol}_{market}_{style}_{tf}_SHORT_{curr.get('time', '')}",
                                    "symbol": symbol,
                                    "market": market,
                                    "strategy": STRATEGY_6_CONFIG["name"],
                                    "direction": "SHORT",
                                    "style": style,
                                    "timeframe": tf,
                                    "entry": round(entry, 4),
                                    "entry_time": now_str,
                                    "sl": round(sl, 4),
                                    "active_sl": round(sl, 4),
                                    "be_trigger": round(be_price, 4),
                                    "tp1": round(tp1, 4),
                                    "tp2": round(tp2, 4),
                                    "rr": round(rr, 2),
                                    "be_hit": False,
                                    "tp1_hit": False,
                                    "status": "OPEN",
                                })

    return setups


# ==============================================================================
# LIVE TRADE MANAGEMENT (BE@1:1, TP1, TP2, SL WITH IST TIMESTAMPS)
# ==============================================================================
def process_live_trade_updates(active_trades, current_prices, now_dt=None):
    """
    Open trades ka live price check karke BE@1:1, TP1 Hit, TP2 Hit, aur SL Hit alerts
    exact IST Date & Time ke saath banata hai.
    Returns: (update_messages, updated_active_trades)
    """
    messages = []
    remaining = []
    now_str = format_ist_timestamp(now_dt)

    for trade in active_trades or []:
        if trade.get("status") != "OPEN":
            continue

        key = f"{trade['market']}:{trade['symbol']}"
        price = current_prices.get(key)
        if price is None:
            remaining.append(trade)
            continue

        price = float(price)
        direction = trade["direction"]
        base_tag = f"{trade['strategy']} | {trade['symbol']} ({trade['market']}) | {direction} [{trade['style']} - {trade['timeframe']}]"
        entry_time_str = trade.get("entry_time", "N/A")

        if direction == "LONG":
            if not trade.get("be_hit") and price >= trade["be_trigger"]:
                trade["be_hit"] = True
                trade["active_sl"] = trade["entry"]
                messages.append(
                    f"🛡️ <b>1:1 BREAKEVEN HIT</b> | {base_tag}\n"
                    f"🕒 Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | SL moved to Entry: <code>{trade['entry']}</code>"
                )

            if not trade.get("tp1_hit") and price >= trade["tp1"]:
                trade["tp1_hit"] = True
                trade["active_sl"] = trade["entry"]
                messages.append(
                    f"🎯 <b>1ST TARGET (TP1) HIT</b> | {base_tag}\n"
                    f"🕒 TP1 Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | TP1: <code>{trade['tp1']}</code> | Next Target TP2: <code>{trade['tp2']}</code>"
                )

            if price >= trade["tp2"]:
                trade["status"] = "CLOSED_TP2"
                messages.append(
                    f"🏆 <b>2ND TARGET (TP2) HIT</b> | {base_tag}\n"
                    f"🕒 TP2 Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | TP2: <code>{trade['tp2']}</code> (R:R 1:{trade['rr']}) | Trade Complete ✅"
                )
                continue

            if price <= trade["active_sl"]:
                sl_type = "BREAKEVEN SL HIT (₹0 Loss)" if trade.get("be_hit") else "STOPLOSS HIT"
                trade["status"] = "CLOSED_SL"
                messages.append(
                    f"🛑 <b>{sl_type}</b> | {base_tag}\n"
                    f"🕒 SL Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | SL: <code>{trade['active_sl']}</code>"
                )
                continue

        elif direction == "SHORT":
            if not trade.get("be_hit") and price <= trade["be_trigger"]:
                trade["be_hit"] = True
                trade["active_sl"] = trade["entry"]
                messages.append(
                    f"🛡️ <b>1:1 BREAKEVEN HIT</b> | {base_tag}\n"
                    f"🕒 Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | SL moved to Entry: <code>{trade['entry']}</code>"
                )

            if not trade.get("tp1_hit") and price <= trade["tp1"]:
                trade["tp1_hit"] = True
                trade["active_sl"] = trade["entry"]
                messages.append(
                    f"🎯 <b>1ST TARGET (TP1) HIT</b> | {base_tag}\n"
                    f"🕒 TP1 Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | TP1: <code>{trade['tp1']}</code> | Next Target TP2: <code>{trade['tp2']}</code>"
                )

            if price <= trade["tp2"]:
                trade["status"] = "CLOSED_TP2"
                messages.append(
                    f"🏆 <b>2ND TARGET (TP2) HIT</b> | {base_tag}\n"
                    f"🕒 TP2 Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | TP2: <code>{trade['tp2']}</code> (R:R 1:{trade['rr']}) | Trade Complete ✅"
                )
                continue

            if price >= trade["active_sl"]:
                sl_type = "BREAKEVEN SL HIT (₹0 Loss)" if trade.get("be_hit") else "STOPLOSS HIT"
                trade["status"] = "CLOSED_SL"
                messages.append(
                    f"🛑 <b>{sl_type}</b> | {base_tag}\n"
                    f"🕒 SL Hit Time: <code>{now_str}</code> (Opportunity: <code>{entry_time_str}</code>)\n"
                    f"Price: <code>{price}</code> | SL: <code>{trade['active_sl']}</code>"
                )
                continue

        remaining.append(trade)

    return messages, remaining


# ==============================================================================
# MASTER STRATEGY EVALUATOR (ALL ACTIVE STRATEGIES)
# ==============================================================================
def evaluate_strategies_detailed(symbol, market, price, candles_by_tf=None):
    """
    Sabhi active strategies ko parallel/independent evaluate karta hai.
    Returns: (structured_setups_list, formatted_alert_strings_list)
    """
    if not candles_by_tf or market in PENDING_MARKETS:
        return [], []

    setups = []
    formatted_alerts = []
    now_dt = get_ist_now()

    # --- Strategy #1: ICT 2022 Model (Intraday + Swing) ---
    s1_tfs = STRATEGY_1_CONFIG["timeframes"].get(market, {})
    for style in ("Intraday", "Swing"):
        allowed, _ = check_session_and_killzone(market, style, now_dt)
        if not allowed:
            continue

        htf_bias = check_htf_bias(candles_by_tf) if style == "Swing" else "NEUTRAL"
        for tf in s1_tfs.get(style, []):
            tf_candles = candles_by_tf.get(tf) or []
            matches = evaluate_ict_2022_tf(
                symbol=symbol,
                market=market,
                style=style,
                tf=tf,
                candles=tf_candles,
                live_price=price,
                htf_bias=htf_bias,
                now_dt=now_dt,
            )
            setups.extend(matches)

    # --- Strategy #2: Silver Bullet Setup (Strictly Intraday) ---
    sb_allowed, _ = check_silver_bullet_window(market, now_dt)
    if sb_allowed:
        s2_tfs = STRATEGY_2_CONFIG["timeframes"].get(market, {}).get("Intraday", [])
        for tf in s2_tfs:
            tf_candles = candles_by_tf.get(tf) or []
            matches = evaluate_silver_bullet_tf(
                symbol=symbol,
                market=market,
                tf=tf,
                candles=tf_candles,
                live_price=price,
                now_dt=now_dt,
            )
            setups.extend(matches)

    # --- Strategy #3: Power of 3 — AMD (Intraday + HTF POI Swing, No Killzone) ---
    hours_ok, _ = check_market_open_hours(market, now_dt)
    if hours_ok:
        s3_tfs = STRATEGY_3_CONFIG["timeframes"].get(market, {})
        for style in ("Intraday", "Swing"):
            htf_poi_bias = check_htf_poi_bias(candles_by_tf, price) if style == "Swing" else "NEUTRAL"
            for tf in s3_tfs.get(style, []):
                tf_candles = candles_by_tf.get(tf) or []
                matches = evaluate_po3_amd_tf(
                    symbol=symbol,
                    market=market,
                    style=style,
                    tf=tf,
                    candles=tf_candles,
                    live_price=price,
                    htf_poi_bias=htf_poi_bias,
                    now_dt=now_dt,
                )
                setups.extend(matches)

    # --- Strategy #4: Market Maker Buy/Sell Model — MMMS (Intraday + HTF POI Swing, No Killzone) ---
    if hours_ok:
        s4_tfs = STRATEGY_4_CONFIG["timeframes"].get(market, {})
        for style in ("Intraday", "Swing"):
            htf_poi_bias = check_htf_poi_bias(candles_by_tf, price) if style == "Swing" else "NEUTRAL"
            for tf in s4_tfs.get(style, []):
                tf_candles = candles_by_tf.get(tf) or []
                matches = evaluate_mmms_tf(
                    symbol=symbol,
                    market=market,
                    style=style,
                    tf=tf,
                    candles=tf_candles,
                    live_price=price,
                    htf_poi_bias=htf_poi_bias,
                    now_dt=now_dt,
                )
                setups.extend(matches)

    # --- Strategy #5: Order Block (OB) Retest Model (Intraday + HTF POI Swing, No Killzone) ---
    if hours_ok:
        s5_tfs = STRATEGY_5_CONFIG["timeframes"].get(market, {})
        for style in ("Intraday", "Swing"):
            htf_poi_bias = check_htf_poi_bias(candles_by_tf, price) if style == "Swing" else "NEUTRAL"
            for tf in s5_tfs.get(style, []):
                tf_candles = candles_by_tf.get(tf) or []
                matches = evaluate_ob_retest_tf(
                    symbol=symbol,
                    market=market,
                    style=style,
                    tf=tf,
                    candles=tf_candles,
                    live_price=price,
                    htf_poi_bias=htf_poi_bias,
                    now_dt=now_dt,
                )
                setups.extend(matches)

    # --- Strategy #6: Liquidity Sweep & Reversal Model (Intraday + Swing, No Killzone) ---
    if hours_ok:
        s6_tfs = STRATEGY_6_CONFIG["timeframes"].get(market, {})
        htf_pool_bias = check_htf_bias(candles_by_tf)
        for style in ("Intraday", "Swing"):
            for tf in s6_tfs.get(style, []):
                tf_candles = candles_by_tf.get(tf) or []
                matches = evaluate_liquidity_sweep_reversal_tf(
                    symbol=symbol,
                    market=market,
                    style=style,
                    tf=tf,
                    candles=tf_candles,
                    live_price=price,
                    htf_bias=htf_pool_bias if style == "Swing" else "NEUTRAL",
                    now_dt=now_dt,
                )
                setups.extend(matches)

    for m in setups:
        label = (
            f"{m['strategy']} | {m['direction']} ({m['style']} - {m['timeframe']}) | "
            f"Opportunity Time: {m['entry_time']} | Entry: {m['entry']} | "
            f"SL: {m['sl']} (BE@1:1: {m['be_trigger']}) | "
            f"TP1: {m['tp1']} | TP2: {m['tp2']} | R:R 1:{m['rr']}"
        )
        formatted_alerts.append(label)

    return setups, formatted_alerts


def evaluate_strategies(symbol, market, price, candles_by_tf=None):
    """
    Backward-compatible wrapper jo triggered alert strings ki list return karta hai.
    """
    _, formatted_alerts = evaluate_strategies_detailed(symbol, market, price, candles_by_tf)
    return formatted_alerts
