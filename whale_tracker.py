# whale_tracker.py
import time

# বড় ট্রানজেকশন জমার লিস্ট
whale_alerts = []

def process_whale_trade(symbol, price, quantity, is_buyer_maker):
    usd_value = float(price) * float(quantity)
    
    # আমরা শুধু ১০০,০০০ ডলারের ওপরের ট্রেডগুলো ট্র্যাক করব (আপনি চাইলে ১০০০.০০ করতে পারেন)
    if usd_value > 100000:
        side = "SELL 🔴" if is_buyer_maker else "BUY 🟢"
        alert = {
            "time": time.strftime("%H:%M:%S"),
            "symbol": symbol,
            "side": side,
            "amount": f"${usd_value:,.2f}",
            "price": price,
            "quantity": quantity
        }
        
        # লিস্টের শুরুতে নতুন এলার্ট যোগ করা
        whale_alerts.insert(0, alert)
        
        # শুধু শেষ ২০টি এলার্ট রাখা
        if len(whale_alerts) > 20:
            whale_alerts.pop()

def get_whale_alerts():
    return whale_alerts
