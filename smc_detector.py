# smc_detector.py
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_ict_concepts(data, tf):
    if not data or len(data) < 30:
        return []

    df = pd.DataFrame(data)
    # ডাটা ফরম্যাট নিশ্চিত করা
    df['h'] = df['high'].astype(float)
    df['l'] = df['low'].astype(float)
    df['c'] = df['close'].astype(float)
    df['o'] = df['open'].astype(float)
    
    analysis = []
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    prev_2 = df.iloc[-3]

    # --- ১. Killzone (Time Sync) ---
    hour = datetime.utcnow().hour
    kz = "OFF-Hours"
    if 7 <= hour <= 10: kz = "London Killzone"
    elif 12 <= hour <= 15: kz = "NY Killzone"
    elif 0 <= hour <= 5: kz = "Asian Range"
    analysis.append({"concept": "Killzone Status", "type": "Time", "msg": f"Current: {kz}", "color": "#f0b90b"})

    # --- ২. Daily Bias & ৩. Daily Narrative (HTF specific) ---
    if tf in ['1d', '4h']:
        bias = "BULLISH" if curr['c'] > df['c'].iloc[-20] else "BEARISH"
        zone = "Premium (Sell Focus)" if curr['c'] > df['h'].tail(50).mean() else "Discount (Buy Focus)"
        analysis.append({"concept": "Market Narrative", "type": "Bias", "msg": f"Bias: {bias} | Zone: {zone}", "color": "#f0b90b"})

    # --- ৪. FVG (Fair Value Gap) - Internal Liquidity ---
    # Bullish FVG
    if df['l'].iloc[-1] > df['h'].iloc[-3]:
        gap_price = (df['l'].iloc[-1] + df['h'].iloc[-3]) / 2
        analysis.append({"concept": "Bullish FVG", "type": "Internal Liq", "msg": f"Gap at {gap_price:.2f}. Price may retrace here.", "color": "#02c076"})
    # Bearish FVG
    elif df['h'].iloc[-1] < df['l'].iloc[-3]:
        gap_price = (df['h'].iloc[-1] + df['l'].iloc[-3]) / 2
        analysis.append({"concept": "Bearish FVG", "type": "Internal Liq", "msg": f"Gap at {gap_price:.2f}. Expecting price fill.", "color": "#f84960"})

    # --- ৫. Order Block (OB) ---
    if curr['c'] > df['h'].iloc[-5:-1].max() and prev['c'] > prev['o']:
        analysis.append({"concept": "Bullish Order Block", "type": "Institutional", "msg": "Big players buying detected. Strong Support.", "color": "#02c076"})
    elif curr['c'] < df['l'].iloc[-5:-1].min() and prev['c'] < prev['o']:
        analysis.append({"concept": "Bearish Order Block", "type": "Institutional", "msg": "Heavy selling orders found. Strong Resistance.", "color": "#f84960"})

    # --- ৬. Breaker Block & ৭. Mitigation Block ---
    # Simplified Logic: Sweep followed by structure break
    if curr['c'] > df['h'].max() * 0.999:
        analysis.append({"concept": "Potential Breaker", "type": "Structure", "msg": "Liquidity sweep detected. Watch for trend shift.", "color": "#f0b90b"})

    # --- ৮. Internal vs External Liquidity & ৯. Engineered Liquidity ---
    pdh = df['h'].iloc[:-1].max() # Previous High
    pdl = df['l'].iloc[:-1].min() # Previous Low
    if curr['h'] >= pdh:
        analysis.append({"concept": "External Liquidity", "type": "Sweep", "msg": "BSL (Buy Side Liquidity) Taken. Engineered trap purged.", "color": "#f84960"})
    elif curr['l'] <= pdl:
        analysis.append({"concept": "External Liquidity", "type": "Sweep", "msg": "SSL (Sell Side Liquidity) Taken. Retail stops hit.", "color": "#02c076"})

    # --- ১০. Fractal Nature (Top-Down Analysis) ---
    analysis.append({"concept": "Fractal Nature", "type": "Context", "msg": f"Analyzing {tf} structure. Always check 1D for main bias.", "color": "#848e9c"})

    # --- ১১. Time + Price + Liquidity Sync (The Golden Signal) ---
    if kz != "OFF-Hours" and (curr['h'] >= pdh or curr['l'] <= pdl):
        analysis.append({"concept": "GOLDEN SYNC", "type": "EXECUTION", "msg": "Time + Price + Liquidity aligned! High Probability Entry.", "color": "#f0b90b"})

    return analysis
