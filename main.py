import os
import asyncio
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from smc_detector import analyze_ict_concepts
from orderbook_stream import whale_alerts, start_streams # Whale Tracker ইমপোর্ট করা হলো

app = FastAPI()

# CORS সেটিংস যাতে ওয়ার্ডপ্রেস থেকে ডাটা পায়
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# গ্লোবাল ডাটা স্টোরেজ
market_data_store = {
    "XAUUSD": {"5m": [], "15m": [], "1h": [], "4h": [], "1d": []},
    "BTCUSDT": {"5m": [], "15m": [], "1h": [], "4h": [], "1d": []},
    "ETHUSDT": {"5m": [], "15m": [], "1h": [], "4h": [], "1d": []}
}

async def fetch_candles(symbol, interval, limit=200):
    """বাইনান্স থেকে নির্দিষ্ট টাইমফ্রেমের ২০০ ক্যান্ডেল আনা"""
    bin_sym = "PAXGUSDT" if "XAU" in symbol else symbol
    url = f"https://api.binance.com/api/v3/klines?symbol={bin_sym}&interval={interval}&limit={limit}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                raw_data = response.json()
                return [{
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "time": c[0]
                } for c in raw_data]
        except Exception as e:
            print(f"Error fetching {symbol} {interval}: {e}")
    return []

async def sync_all_data():
    """সব অ্যাসেট এবং দরকারি টাইমফ্রেম সিঙ্ক করা"""
    symbols = ["XAUUSD", "BTCUSDT", "ETHUSDT"]
    intervals = ["5m", "15m", "1h", "4h", "1d"] # আপনার রিকোয়েস্ট অনুযায়ী টাইমফ্রেম
    
    while True:
        for s in symbols:
            for i in intervals:
                candles = await fetch_candles(s, i)
                if candles:
                    market_data_store[s][i] = candles
                    print(f"Synced: {s} {i}")
        await asyncio.sleep(30) # সার্ভারের চাপ কমাতে ৩০ সেকেন্ড গ্যাপ

@app.on_event("startup")
async def startup_event():
    # দুটি কাজই একসাথে শুরু হবে
    asyncio.create_task(sync_all_data())
    asyncio.create_task(start_streams()) # ৩ নম্বর টুল (Whale) চালু করা হলো

# --- ৩ নম্বর টুল (Whale Tracker) এন্ডপয়েন্ট ---
@app.get("/whales")
async def get_whales():
    return {"alerts": whale_alerts if whale_alerts else [], "status": "Online"}

# --- ৪ নম্বর টুল (AI SMC) এন্ডপয়েন্ট ---
@app.get("/ai-smc/{symbol}")
async def get_ai_smc(symbol: str, tf: str = Query("15m")):
    symbol = symbol.upper()
    asset_data = market_data_store.get(symbol, {})
    
    # ডাটা এখনো সিঙ্ক না হয়ে থাকলে মেসেজ দিবে
    if not asset_data.get("1d") or not asset_data.get(tf):
        return {"symbol": symbol, "tf": tf, "results": [], "msg": "Booting AI Engine... Fetching 200 Candles."}

    # smc_detector কল করা
    analysis_results = analyze_ict_concepts(asset_data, symbol, tf)
    
    return {
        "symbol": symbol,
        "selected_tf": tf,
        "results": analysis_results
    }

@app.get("/")
async def root():
    return {"status": "FTBD Quant AI Engine is Live", "active_assets": ["XAU", "BTC", "ETH"]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
