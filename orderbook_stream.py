import asyncio
import httpx
from datetime import datetime

# শুধু ৩ নম্বর টুলের জন্য গ্লোবাল ডাটা
whale_alerts = []

async def fetch_whales(symbol):
    """বাইনান্স থেকে বড় অর্ডার বা লিকুইডিটি ট্র্যাক করা"""
    bin_sym = "PAXGUSDT" if "XAU" in symbol else symbol
    url = f"https://api.binance.com/api/v3/depth?symbol={bin_sym}&limit=5"
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                res = await client.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    price = float(data['bids'][0][0])
                    qty = float(data['bids'][0][1])
                    val = price * qty
                    
                    # $100,000 এর বড় অর্ডার হলে সেভ করবে
                    if val >= 100000:
                        alert = {
                            "symbol": symbol,
                            "price": price,
                            "amount": f"${val/1000:.1f}K",
                            "time": datetime.now().strftime("%H:%M:%S")
                        }
                        # ডুপ্লিকেট রোধ
                        if not whale_alerts or whale_alerts[-1]['price'] != alert['price']:
                            whale_alerts.append(alert)
                            if len(whale_alerts) > 15: whale_alerts.pop(0)
                
                await asyncio.sleep(3) # ৩ সেকেন্ড পর পর চেক
            except:
                await asyncio.sleep(10)

async def start_streams():
    """Whale tracking শুরু করা"""
    symbols = ["XAUUSD", "BTCUSDT", "ETHUSDT"]
    tasks = [fetch_whales(s) for s in symbols]
    await asyncio.gather(*tasks)
