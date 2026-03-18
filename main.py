import os
import asyncio
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from smc_detector import analyze_ict_concepts

app = FastAPI()

# CORS সেটিংস যাতে ওয়ার্ডপ্রেস থেকে ডাটা পায়
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# গ্লোবাল ডাটা স্টোরেজ (বিভিন্ন টাইমফ্রেমের জন্য)
# আমরা ৪টি বড় টাইমফ্রেম এবং ইউজারের সিলেক্ট করা টাইমফ্রেমের ডাটা রাখবো
market_data_store = {
    "XAUUSD": {"1m": [], "5m": [], "15m": [], "1h": [], "4h": [], "1d": []},
    "BTCUSDT": {"1m": [], "5m": [], "15m": [], "1h": [], "4h": [], "1d": []},
    "ETHUSDT": {"1m": [], "5m": [], "15m": [], "1h": [], "4h": [], "1d": []}
}

async def fetch_candles(symbol, interval, limit=200):
    """বাইনান্স থেকে নির্দিষ্ট টাইমফ্রেমের ২০০ ক্যান্ডেল আনা"""
    bin_sym = "PAXGUSDT" if "XAU" in symbol else symbol
    url = f"https://api.binance.com/api/v3/klines?symbol={bin_sym}&interval={interval}&limit={limit}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                raw_data = response.json()
                # ক্যান্ডেল ফরম্যাট করা
                candles = []
                for c in raw_data:
                    candles.append({
                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),
                        "time": c[0]
                    })
                return candles
        except Exception as e:
            print(f"Error fetching {symbol} {interval}: {e}")
    return []

async def sync_all_data():
    """সব অ্যাসেট এবং দরকারি টাইমফ্রেম সিঙ্ক করা"""
    symbols = ["XAUUSD", "BTCUSDT", "ETHUSDT"]
    intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
    
    while True:
        for s in symbols:
            for i in intervals:
                candles = await fetch_candles(s, i)
                if candles:
                    market_data_store[s][i] = candles
        # সার্ভারের ওপর চাপ কমাতে ২০ সেকেন্ড পর পর রিফ্রেশ
        await asyncio.sleep(20)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_all_data())

@app.get("/ai-smc/{symbol}")
async def get_ai_smc(symbol: str, tf: str = Query("15m")):
    symbol = symbol.upper()
    # নির্দিষ্ট অ্যাসেটের সব টাইমফ্রেম ডাটা smc_detector-এ পাঠানো
    asset_data = market_data_store.get(symbol, {})
    
    if not asset_data.get("1d") or not asset_data.get(tf):
        return {"symbol": symbol, "tf": tf, "results": [], "msg": "Booting AI Engine... Fetching 200 Candles."}

    # smc_detector এর analyze_ict_concepts কল করা
    analysis_results = analyze_ict_concepts(asset_data, symbol, tf)
    
    return {
        "symbol": symbol,
        "selected_tf": tf,
        "results": analysis_results
    }

@app.get("/")
async def root():
    return {"status": "FTBD Multi-TF Engine Online", "active_assets": ["XAU", "BTC", "ETH"]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
