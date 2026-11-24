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


def check_session_and_killzone(market, style, now_dt=None):
    """
    Market hours aur Intraday Killzone alignment check (IST).
    Swing mode mein Killzone bypass rehta hai, par active market hours check honge.
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
    if market in PENDING_MARKETS:
        return False, f"{market} Pending"

    now_dt = now_dt or get_ist_now()
    t = now_dt.time()

    if market == "NSE":
        if now_dt.weekday() >= 5:
            return False, "NSE Weekend Closed"
        for start_t, end_t in STRATEGY_2_CONFIG["delivery_windows_ist"]["NSE"]:
            if _in_window(t, start_t, end_t):
                return True, "NSE Silver Bullet Delivery Window"
        return False, "Outside NSE Silver Bullet Window"

    if market == "Crypto":
        allowed_kz, reason = check_session_and_killzone("Crypto", "Intraday", now_dt)
        if not allowed_kz:
            return False, reason
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
