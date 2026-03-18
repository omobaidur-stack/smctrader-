# orderbook_stream.py
import json
import websocket
from heatmap_engine import update_heatmap
from footprint_engine import update_footprint

# হিটম্যাপ এবং ফুটপ্রিন্টের জন্য কম্বাইন্ড স্ট্রিম
WS_URL = "wss://stream.binance.com:9443/stream?streams=btcusdt@depth20@100ms/ethusdt@depth20@100ms/paxgusdt@depth20@100ms/btcusdt@aggTrade/ethusdt@aggTrade/paxgusdt@aggTrade"

def on_message(ws, message):
    raw_data = json.loads(message)
    stream_name = raw_data['stream']
    data = raw_data['data']

    # সিম্বল ডিটেক্ট করা
    if "btcusdt" in stream_name: symbol = "BTCUSD"
    elif "ethusdt" in stream_name: symbol = "ETHUSD"
    else: symbol = "XAUUSD"

    # ১ নম্বর টুল: হিটম্যাপের ডেটা প্রসেসিং (Depth)
    if "@depth" in stream_name:
        for b in data.get("bids", []):
            update_heatmap(symbol, b[0], b[1], "bid")
        for a in data.get("asks", []):
            update_heatmap(symbol, a[0], a[1], "ask")
    
    # ২ নম্বর টুল: ফুটপ্রিন্টের ডেটা প্রসেসিং (Trades)
    elif "@aggTrade" in stream_name:
        # p=price, q=quantity, m=is_buyer_maker (True মানে Market Sell)
        update_footprint(symbol, data['p'], data['q'], data['m'])

def start_stream():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()
