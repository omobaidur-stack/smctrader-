import asyncio
import requests
from datetime import datetime

# ডাটা স্টোরেজ
footprint_data = {"XAUUSD": [], "BTCUSDT": [], "ETHUSDT": []}
whale_alerts = []

def fetch_sync(symbol):
    # গোল্ডের জন্য PAXGUSDT, বাকিদের জন্য সরাসরি সিম্বল
    bin_sym = "PAXGUSDT" if "XAU" in symbol else symbol
    url = f"https://api.binance.com/api/v3/depth?symbol={bin_sym}&limit=10"
    try:
        res = requests.get(url, timeout=5)
        return res.json() if res.status_code == 200 else None
    except: return None

async def start_streams():
    while True:
        for symbol in ["XAUUSD", "BTCUSDT", "ETHUSDT"]:
            data = await asyncio.to_thread(fetch_sync, symbol)
            if data and 'bids' in data:
                price = float(data['bids'][0][0])
                qty = float(data['bids'][0][1])
                
                # ৪ নম্বর টুল (SMC) এর জন্য ডাটা সেভ
                candle = {"open": price, "high": price, "low": price, "close": price, "time": datetime.now().isoformat()}
                footprint_data[symbol].append(candle)
                if len(footprint_data[symbol]) > 50: footprint_data[symbol].pop(0)

                # ৩ নম্বর টুল (Whale Tracker) - $100,000 এর উপরের অর্ডার
                val = price * qty
                if val >= 100000:
                    alert = {
                        "symbol": symbol, 
                        "price": price, 
                        "amount": f"${val/1000:.1f}K", 
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
                    # ডুপ্লিকেট এড়াতে চেক
                    if not whale_alerts or whale_alerts[-1]['price'] != alert['price']:
                        whale_alerts.append(alert)
                        if len(whale_alerts) > 20: whale_alerts.pop(0)
        
        await asyncio.sleep(2) # ২ সেকেন্ড আপডেট রেট
