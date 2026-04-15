# Trading Bot Redesign Plan

## Current Problems
1. **yfinance fails** - API rate-limited, unreliable during pre-market
2. **Batch dashboard updates** - Only updates after trades, not real-time
3. **Fixed watchlist** - Limited to 13 symbols, missing opportunities
4. **No learning** - Bot doesn't analyze what worked/failed
5. **Large budget** - $10k is too aggressive for paper trading
6. **No feedback loop** - No optimization between runs

---

## Proposed Solution

### 1. DATA SOURCE (Replace yfinance)

**Options:**
- **Alpha Vantage** - Free tier, reliable, 5 calls/min
- **Finnhub** - Free tier, real-time quotes, 60 calls/min
- **Polygon.io** - Free tier, enterprise-grade, unlimited
- **Alpaca Markets** - Free, real-time, broker integration
- **IEX Cloud** - Paid but very reliable

**Recommendation: Finnhub or Polygon.io**
- ✓ 100% reliable
- ✓ Real-time data
- ✓ Free tier available
- ✓ Can fetch unlimited stocks
- ✓ Better uptime than yfinance

---

### 2. PORTFOLIO BUDGET: $300 (Down from $10k)

**Changes:**
- Starting balance: $300
- Position size: $30-50 per trade (10-15% risk)
- Max 3-5 open positions
- Stop loss: 2-3% (tighter)
- Take profit: 5-8% (realistic)

**Position sizing formula:**
```
Position size = (Cash * 0.15) / Entry Price
```

---

### 3. REAL-TIME DASHBOARD

**Current (Broken):**
- Bot runs → Updates files → GitHub → Website refreshes every 60s
- Data is 1-2 minutes stale

**New (Real-time):**

**Option A: WebSocket Server (Best)**
- Bot runs local Flask/FastAPI server
- Server broadcasts updates via WebSocket
- Dashboard connects to `ws://localhost:8000`
- Updates show instantly (< 100ms)
- Works locally only

**Option B: Firebase/Supabase (Cloud)**
- Bot writes to cloud database in real-time
- Dashboard reads from cloud (auto-updates)
- Public dashboard works globally
- Requires API key management

**Option C: Hybrid (Recommended)**
- Local: WebSocket server for live monitoring
- Cloud: Firebase for public GitHub Pages dashboard
- Bot pushes updates to both

**Recommendation: Option C - Hybrid**
- Local dashboard (real-time) for active monitoring
- GitHub Pages dashboard (updated every 5 min) for remote access

---

### 4. UNLIMITED STOCK UNIVERSE

**Current:**
- Fixed 13 symbols (AAPL, MSFT, NVDA, etc.)
- Limited opportunity

**New:**

**Stock Screening:**
1. **Daily market movers** - Top 20 gainers/losers
2. **High volume stocks** - Unusual volume increases
3. **Trending stocks** - Bullish/bearish technical setups
4. **Sector leaders** - Best performers in each sector
5. **Custom criteria** - Price range, volume, volatility

**Data sources:**
- Finnhub: Get market movers, trending stocks
- Polygon.io: Screen by criteria (price range, volume)
- Yahoo Finance Scrape: Get trending from finance.yahoo.com

**Process:**
```
1. Fetch top 50 movers + trending stocks daily
2. Filter by: Volume > 1M shares, Price $5-500
3. Score each symbol (0-100)
4. Send top 10 to Ollama for final review
5. Execute best signals
```

---

### 5. LEARNING & OPTIMIZATION

**After-Market Analysis (Runs 4:15 PM daily):**

1. **Trade Review:**
   - What worked? (winning signals)
   - What didn't? (losing signals)
   - Pattern analysis

2. **Performance Metrics:**
   - Win rate by entry time
   - Win rate by sector
   - Average holding time
   - Best stop loss % (2% vs 3%)
   - Best take profit % (5% vs 8%)

3. **Signal Quality Analysis:**
   - Which indicators predict wins?
   - RSI ranges that work best
   - Momentum thresholds
   - Volume filters effectiveness

4. **Dynamic Adjustment:**
   - Update signal thresholds based on results
   - Adjust position sizing
   - Modify stock screening criteria
   - Change stop loss/take profit percentages

**Example Output:**
```
Performance Summary (Last 10 trades):
- Win Rate: 70% (7 wins, 3 losses)
- Best Entry Time: 10-11 AM (80% win)
- Best Sector: Tech (75% win)
- Recommended Stop Loss: 2.5% (was 3%)
- Recommended Take Profit: 7% (was 6%)
```

---

### 6. ARCHITECTURE CHANGES

**New Folder Structure:**
```
trading-bot-local/
├── main.py                 # Entry point
├── config.json             # Settings
├── requirements.txt        # Dependencies
│
├── modules/
│   ├── market_data.py      # NEW: Finnhub/Polygon integration
│   ├── stock_screener.py   # NEW: Screening & ranking
│   ├── signal_engine.py    # Scoring logic
│   ├── ai_decision.py      # Ollama integration
│   ├── execution.py        # Paper trading
│   ├── analysis.py         # NEW: After-market analysis
│   ├── learning.py         # NEW: Dynamic optimization
│   ├── websocket_server.py # NEW: Real-time updates
│   └── logger.py           # Logging
│
├── data/
│   ├── portfolio.json      # Current state
│   ├── trades_history.json # All trades ever
│   ├── performance.json    # NEW: Analysis results
│   ├── optimization.json   # NEW: Learned thresholds
│   └── screened_stocks.json # NEW: Today's candidates
│
├── docs/
│   ├── dashboard.html      # Local (connects to WebSocket)
│   ├── public_dashboard.html # Public (GitHub Pages)
│   └── data/
│
└── logs/
    ├── system.log
    ├── trades.log
    └── analysis.log
```

---

### 7. EXECUTION TIMELINE

**Phase 1 (This week):**
- [ ] Integrate Finnhub/Polygon API
- [ ] Update data fetcher to new source
- [ ] Test 100% reliability
- [ ] Reset portfolio to $300

**Phase 2 (Next week):**
- [ ] Build stock screener
- [ ] Create unlimited universe selection
- [ ] Test signal generation on 100+ stocks

**Phase 3 (Following week):**
- [ ] Build WebSocket server
- [ ] Create real-time dashboard
- [ ] Connect bot to live updates

**Phase 4 (After live trades):**
- [ ] Build after-market analysis
- [ ] Implement learning system
- [ ] Dynamic optimization

---

### 8. EXPECTED RESULTS

**Before:** 
- 0 trades (yfinance failures)
- No learning
- Manual tweaking

**After:**
- 5-10 trades/day with 100+ stock universe
- Real-time monitoring
- Automatic optimization
- Learning from past results
- Better win rate over time

---

## Questions to Confirm

1. **Data source:** Finnhub or Polygon.io?
2. **Dashboard:** Local WebSocket + Cloud backup?
3. **Stock universe:** How many stocks to screen daily? (50? 100? 500?)
4. **Learning priority:** Most important: win rate? Profit? Risk management?
5. **Timeline:** Implement all at once or phase by phase?

