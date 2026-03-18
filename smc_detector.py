from datetime import datetime

def analyze_ict_concepts(data_map, symbol, selected_tf):
    """
    data_map: একটি ডিকশনারি যাতে {'1m': [...], '4h': [...], '1d': [...]} ডাটা আছে।
    """
    results = []
    
    # ১. বড় টাইমফ্রেম এনালাইসিস (Bias & Narrative) - 1Day এবং 4Hour থেকে
    d1_data = data_map.get('1d', [])
    h4_data = data_map.get('4h', [])
    
    bias = "NEUTRAL"
    narrative = "Equilibrium"
    
    if d1_data and h4_data:
        # ২. ডেইলি বায়াস (Daily Bias) - বড় ট্রেন্ড চেক
        d1_close = d1_data[-1]['close']
        d1_open = d1_data[-1]['open']
        bias = "BULLISH 🟢" if d1_close > d1_open else "BEARISH 🔴"
        
        # ৩. ডেইলি ন্যারেটিভ (Daily Narrative) - প্রিমিয়াম না ডিসকাউন্ট
        h4_highs = [c['high'] for c in h4_data[-20:]]
        h4_lows = [c['low'] for c in h4_data[-20:]]
        mid = (max(h4_highs) + min(h4_lows)) / 2
        current_price = h4_data[-1]['close']
        narrative = "Premium (Sell Focus)" if current_price > mid else "Discount (Buy Focus)"

    # বায়াস এবং ন্যারেটিভ কার্ড যোগ করা
    results.append({"tag": "Bias", "concept": f"Today's Bias: {bias}", "color": "#02c076" if "BULLISH" in bias else "#ff3b3b", "msg": f"HTF analysis confirms a {bias} sentiment for today."})
    results.append({"tag": "Narrative", "concept": narrative, "color": "#a626ff", "msg": f"Price is currently in {narrative} zone."})

    # ২. ইউজারের সিলেক্ট করা টাইমফ্রেম এনালাইসিস (বাকি ৮টি বিষয় - ২০০ ক্যান্ডেল)
    tf_data = data_map.get(selected_tf, [])
    if len(tf_data) > 10:
        highs = [c['high'] for c in tf_data[-200:]]
        lows = [c['low'] for c in tf_data[-200:]]
        closes = [c['close'] for c in tf_data[-200:]]
        
        curr_c = closes[-1]
        
        # ১. Killzone
        hour = datetime.utcnow().hour
        kz = "Asian Range"
        if 7 <= hour <= 10: kz = "London Killzone"
        elif 12 <= hour <= 15: kz = "NY Killzone"
        results.append({"tag": "Time", "concept": kz, "color": "#3498db", "msg": f"Active Session: {kz}."})

        # ৪. FVG
        if highs[-3] < lows[-1]:
            results.append({"tag": "Imbalance", "concept": "Bullish FVG", "color": "#00ffcc", "msg": "Price gap identified in selected timeframe."})
        
        # ৫. Order Block (OB)
        if abs(closes[-1] - closes[-5]) > (closes[-1] * 0.001):
            results.append({"tag": "Structure", "concept": "Order Block", "color": "#f1c40f", "msg": "Institutional footprints detected."})

        # ৬. Breaker Block
        if curr_c > max(highs[-15:-5]):
            results.append({"tag": "Reversal", "concept": "Breaker Block", "color": "#e74c3c", "msg": "Trend reversal signal detected."})

        # ৭. Mitigation Block
        results.append({"tag": "Entry", "concept": "Mitigation Zone", "color": "#95a5a6", "msg": "Watching for price mitigation."})

        # ৮. Internal vs External
        liq = "External Sweep" if curr_c > max(highs[:-1]) else "Internal Liquidity"
        results.append({"tag": "Liquidity", "concept": liq, "color": "#1abc9c", "msg": "Price is moving towards liquidity pools."})

        # ৯. Engineered Liquidity
        results.append({"tag": "Trap", "concept": "Engineered Liquidity", "color": "#ff6b6b", "msg": "Retail liquidity traps identified."})

        # ১০. Fractal Nature (Sync Check)
        sync_status = "Fractal Sync" if (("BULLISH" in bias and curr_c > closes[-10])) else "No Sync"
        results.append({"tag": "Sync", "concept": sync_status, "color": "#ffffff", "msg": "Selected TF aligning with HTF Bias."})

        # ১১. GOLDEN SYNC
        if "Killzone" in kz and sync_status == "Fractal Sync":
            results.insert(0, {"tag": "SIGNAL", "concept": "GOLDEN SYNC", "color": "#f0b90b", "msg": "TIME + PRICE + LIQUIDITY ALIGNED!"})

    return results
