from datetime import datetime

def analyze_ict_concepts(data_map, symbol, selected_tf):
    results = []
    
    # ১. ডাটা চেক (যদি HTF ডাটা না থাকে তবে এনালাইসিস স্কিপ করবে)
    d1_data = data_map.get('1d', [])
    h4_data = data_map.get('4h', [])
    tf_data = data_map.get(selected_tf, [])
    
    # পর্যাপ্ত ডাটা না থাকলে ফিডব্যাক দিবে
    if not d1_data or not h4_data or len(tf_data) < 10:
        return results

    # ২. বড় টাইমফ্রেম এনালাইসিস (Bias & Narrative)
    bias = "NEUTRAL"
    narrative = "Equilibrium"
    
    # ডেইলি বায়াস
    d1_close = d1_data[-1]['close']
    d1_open = d1_data[-1]['open']
    bias = "BULLISH 🟢" if d1_close > d1_open else "BEARISH 🔴"
    
    # ডেইলি ন্যারেটিভ (Premium vs Discount)
    h4_highs = [c['high'] for c in h4_data[-40:]] # গত ৪০টি ক্যান্ডেল চেক
    h4_lows = [c['low'] for c in h4_data[-40:]]
    h_max, l_min = max(h4_highs), min(h4_lows)
    mid = (h_max + l_min) / 2
    current_price = tf_data[-1]['close']
    
    narrative = "Premium (Sell Zone)" if current_price > mid else "Discount (Buy Zone)"

    results.append({"tag": "Bias", "concept": f"Today: {bias}", "color": "#02c076" if "BULLISH" in bias else "#ff3b3b", "msg": f"HTF Trend is currently {bias}."})
    results.append({"tag": "Narrative", "concept": narrative, "color": "#a626ff", "msg": f"Price relative to H4 range is in {narrative}."})

    # ৩. ছোট টাইমফ্রেম এনালাইসিস (২০০ ক্যান্ডেল)
    highs = [c['high'] for c in tf_data[-200:]]
    lows = [c['low'] for c in tf_data[-200:]]
    closes = [c['close'] for c in tf_data[-200:]]
    curr_c = closes[-1]
    
    # Killzone লজিক
    hour = datetime.utcnow().hour
    kz = "Asian Range"
    if 7 <= hour <= 10: kz = "London Killzone"
    elif 12 <= hour <= 15: kz = "NY Killzone"
    results.append({"tag": "Time", "concept": kz, "color": "#3498db", "msg": f"Market Session: {kz}."})

    # FVG (Imbalance)
    if len(highs) > 3:
        if highs[-3] < lows[-1]:
            results.append({"tag": "Imbalance", "concept": "Bullish FVG", "color": "#00ffcc", "msg": "Efficiency gap found below price."})
        elif lows[-3] > highs[-1]:
            results.append({"tag": "Imbalance", "concept": "Bearish FVG", "color": "#ff3b3b", "msg": "Efficiency gap found above price."})

    # Order Block
    if abs(closes[-1] - closes[-5]) > (closes[-1] * 0.0015):
        results.append({"tag": "Structure", "concept": "Order Block", "color": "#f1c40f", "msg": "Institutional entry zone detected."})

    # Liquidity Sweep
    if curr_c > max(highs[-50:-1]):
        results.append({"tag": "Liquidity", "concept": "BSL Purged", "color": "#ff6b6b", "msg": "Buy Side Liquidity swept."})
    elif curr_c < min(lows[-50:-1]):
        results.append({"tag": "Liquidity", "concept": "SSL Purged", "color": "#1abc9c", "msg": "Sell Side Liquidity swept."})

    # Fractal Sync
    sync = "MATCHED ✅" if (("BULLISH" in bias and curr_c > closes[-20]) or ("BEARISH" in bias and curr_c < closes[-20])) else "WAITING ⏳"
    results.append({"tag": "Sync", "concept": sync, "color": "#ffffff", "msg": "TF alignment with Daily Bias."})

    # GOLDEN SYNC
    if "Killzone" in kz and sync == "MATCHED ✅":
        results.insert(0, {"tag": "SIGNAL", "concept": "GOLDEN SYNC 🏆", "color": "#f0b90b", "msg": "Time + Bias + Structure Aligned!"})

    return results
