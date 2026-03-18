import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orderbook_stream import footprint_data, whale_alerts, start_streams

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_streams())

# ৩ নম্বর টুল API: Whale Alerts
@app.get("/whales")
async def get_whales():
    return {"alerts": whale_alerts}

# ৪ নম্বর টুল API: AI SMC Interpreter
@app.get("/ai-smc/{symbol}")
async def get_ai_smc(symbol: str):
    symbol = symbol.upper()
    data = footprint_data.get(symbol, [])
    
    # এখানে আমরা SMC লজিকগুলো প্রসেস করি
    results = []
    if len(data) > 10:
        results.append({
            "concept": "Institutional Flow", 
            "type": "ICT Engine", 
            "msg": f"Smart Money activity detected on {symbol}.", 
            "color": "#02c076"
        })
    
    return {"symbol": symbol, "results": results}

@app.get("/")
async def root():
    return {"status": "FTBD Tool 3 & 4 Online (XAU, BTC, ETH)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
