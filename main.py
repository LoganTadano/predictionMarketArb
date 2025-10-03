import time, requests, math
BASE = "https://api.elections.kalshi.com/trade-api/v2"

def get_markets(status="open", limit=500):
    r = requests.get(f"{BASE}/markets", params={"status": status, "limit": limit})
    r.raise_for_status()
    return r.json()["markets"]

def get_orderbook(ticker, depth=10):
    r = requests.get(f"{BASE}/markets/{ticker}/orderbook", params={"depth": depth})
    r.raise_for_status()
    return r.json()["orderbook"]

def best_bid(levels):
    if not levels: return None
    def to_d(p): return float(p) if isinstance(p, str) else float(p)/100.0
    prices = [to_d(row[0]) for row in levels if row]
    return max(prices) if prices else None

def spread_from_ob(ob):
    yes_levels_d = ob.get("yes_dollars", [])
    no_levels_d  = ob.get("no_dollars", [])
    yes_levels_c = ob.get("yes", [])
    no_levels_c  = ob.get("no", [])
    by = best_bid(yes_levels_d) if yes_levels_d else best_bid(yes_levels_c)
    bn = best_bid(no_levels_d)  if no_levels_d  else best_bid(no_levels_c)
    if by is None or bn is None: return math.inf, by, bn
    yes_ask = 1.0 - bn
    no_ask  = 1.0 - by
    # Return the tighter of the two sides as the market's effective spread
    yes_spread = yes_ask - by
    no_spread  = no_ask  - bn
    return min(yes_spread, no_spread), by, bn

def recent_trade_count(minutes=10, ticker=None):
    now = int(time.time())
    params = {"min_ts": now - minutes*60, "limit": 1000}
    if ticker: params["ticker"] = ticker
    r = requests.get(f"{BASE}/markets/trades", params=params)
    r.raise_for_status()
    return len(r.json().get("trades", []))

def liquidity_score(m):
    # Higher is better: 24h volume, OI, API-provided liquidity; tighter spreads will be added later
    v24 = m.get("volume_24h", 0) or 0
    oi  = m.get("open_interest", 0) or 0
    liq = m.get("liquidity", 0) or 0
    return 0.5*v24 + 0.3*oi + 0.2*liq

def find_liquid_markets(top_n=20, spread_cap=0.03, min_depth_levels=1, require_trades=True):
    candidates = sorted(get_markets(status="open", limit=1000), key=liquidity_score, reverse=True)[:200]
    results = []
    for m in candidates:
        t = m["ticker"]
        ob = get_orderbook(t, depth=10)
        sp, by, bn = spread_from_ob(ob)
        # basic depth check: require at least one bid on both sides
        if sp == math.inf or sp > spread_cap: 
            continue
        # optional: require at least one recent trade
        if require_trades and recent_trade_count(15, ticker=t) == 0:
            continue
        results.append({
            "ticker": t,
            "title": m["title"],
            "volume_24h": m.get("volume_24h"),
            "open_interest": m.get("open_interest"),
            "liquidity": m.get("liquidity"),
            "yes_bid_d": by, "no_bid_d": bn,
            "effective_spread_d": round(sp, 4)
        })
        if len(results) >= top_n: break
    return results

if __name__ == "__main__":
    liquid = find_liquid_markets(top_n=15, spread_cap=0.02, require_trades=False)
    for row in liquid:
        print(row)
