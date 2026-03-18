# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
from heatmap_engine import get_heatmap
from footprint_engine import get_footprint # নতুন ইমপোর্ট
from orderbook_stream import start_stream

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ১ নম্বর টুলের এন্ডপয়েন্ট (আগের মতোই আছে)
@app.get("/heatmap/{symbol}")
def heatmap(symbol: str):
    return get_heatmap(symbol.upper())

# ২ নম্বর টুলের এন্ডপয়েন্ট (নতুন যোগ হয়েছে)
@app.get("/footprint/{symbol}")
def footprint(symbol: str):
    return get_footprint(symbol.upper())

@app.get("/")
def home():
    return {"status": "ForexTechBD Multi-Asset Engine (Heatmap + Footprint) is Live"}

def run_stream():
    start_stream()

threading.Thread(target=run_stream, daemon=True).start()
