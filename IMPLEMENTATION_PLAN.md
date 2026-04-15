# Implementation Plan - Cloud-Based Trading Bot v2

## Final Architecture

```
FINNHUB API (Real-time data) 
    ↓
STOCK SCREENER (500+ stocks)
    ↓
SIGNAL ENGINE (Score 0-100)
    ↓
OLLAMA AI (Review top candidates)
    ↓
PAPER EXECUTION ($300 budget)
    ↓
FIREBASE/SUPABASE (Real-time cloud)
    ↓
PUBLIC DASHBOARD (GitHub Pages + Cloud)
    ↓
LEARNING SYSTEM (Profit optimization)
```

## Phase 1: Setup (Today)

### 1.1 Finnhub API Integration
**File:** `modules/finnhub_data.py` (NEW)
```python
- Initialize Finnhub client (free API key)
- Fetch real-time quotes
- Get market movers (top gainers/losers)
- Get trending stocks
- Screen by: volume > 1M, price $5-500, positive momentum
- Cache results to avoid rate limits
```

### 1.2 Stock Screener
**File:** `modules/stock_screener.py` (NEW)
```python
- Daily process: Scan 500+ stocks
- Sources:
  - Top 50 gainers (Finnhub)
  - Top 50 losers (Finnhub)
  - Trending/unusual volume (Finnhub)
  - S&P 500 stocks (all if possible)
- Filter by: Volume, price range, volatility
- Return: Top 100-150 candidates ranked by potential
```

### 1.3 Firebase/Supabase Setup
**Cloud Database:** Supabase (PostgreSQL + real-time)
```
Database tables:
- portfolio (current state)
- trades (all trades ever)
- signals (latest signals)
- analysis (after-market analysis)
- optimization (learned thresholds)
- dashboard_data (public dashboard)
```

**Real-time:** Supabase auto-notifies on data changes

### 1.4 Config Updates
**File:** `config.json` (UPDATED)
```json
{
  "trading": {
    "starting_balance": 300,
    "position_size_percent": 15,
    "max_positions": 5,
    "stop_loss_percent": 2.5,
    "take_profit_percent": 7
  },
  "finnhub": {
    "api_key": "YOUR_KEY",
    "base_url": "https://finnhub.io/api/v1"
  },
  "supabase": {
    "url": "YOUR_URL",
    "key": "YOUR_KEY"
  },
  "screening": {
    "max_stocks": 500,
    "min_volume": 1000000,
    "min_price": 5,
    "max_price": 500
  }
}
```

---

## Phase 2: Core Changes (Week 1)

### 2.1 New Module: `modules/supabase_sync.py`
```python
- Connect to Supabase
- Real-time listeners for trades
- Push portfolio updates
- Subscribe to analysis results
- Auto-update public dashboard
```

### 2.2 Updated: `modules/market_data.py`
```python
- Remove yfinance
- Use Finnhub for all data
- Retry logic for reliability
- Cache recent quotes
```

### 2.3 Updated: `modules/signal_engine.py`
```python
- Score based on profit potential (not just trend)
- Consider: volatility for bigger moves, volume for liquidity
- Dynamic thresholds from learning system
```

### 2.4 Updated: `modules/execution.py`
```python
- Change budget to $300
- Adjust position sizing: (cash * 0.15) / price
- Track every trade for learning
- Calculate unrealized profit correctly
```

---

## Phase 3: Learning System (Week 2)

### 3.1 New Module: `modules/analysis.py`
**Runs at 4:15 PM (after market close)**
```python
- Review all trades from today
- Calculate: Win rate, avg profit, avg loss
- Analyze by: entry time, sector, stock
- Find patterns: What made winners vs losers?
```

### 3.2 New Module: `modules/optimization.py`
**Runs after analysis**
```python
- Compare: Current thresholds vs optimal
- Update if results improved:
  - Stop loss percentage (2-3%)
  - Take profit percentage (6-8%)
  - RSI ranges
  - Volume minimums
  - Entry signal scores
- Learn: Best times to trade, best sectors
- Save optimized values to config
```

### 3.3 Profit Optimization Logic
```python
Metric to maximize: (Total Profit / Total Trades) * Win Rate

Example:
- Current: $12 profit/trade, 60% win rate = $7.20 score
- Adjust stop loss tighter (2% vs 3%):
  - Result: $18 profit/trade, 55% win rate = $9.90 score ✓
  - Accept this change
```

---

## Phase 4: Dashboard (Week 2)

### 4.1 Real-time Cloud Dashboard
**File:** `docs/public_dashboard.html`
```html
- Connect to Supabase real-time
- Show live portfolio equity
- Live trade execution updates
- Real-time signals
- Performance chart (equity curve)
- Learning insights (what's working)
```

### 4.2 Deployment
- Upload to GitHub `/docs` folder
- GitHub Pages serves publicly
- Supabase provides real-time updates
- No 1-minute delay, instant updates

---

## Phase 5: Automation (Week 3)

### 5.1 Task Scheduler Updates
```
8:20 AM - Main trading cycle
  - Screen 500+ stocks
  - Generate signals
  - Execute trades
  
4:15 PM - After-market analysis
  - Analyze today's trades
  - Calculate optimization changes
  - Update config.json
  
4:30 PM - Learning update
  - Apply optimizations
  - Save to Supabase
  - Update public dashboard
```

---

## Data Flow Example

```
Morning (8:20 AM):
1. Bot starts
2. Finnhub: Fetch top 100 movers + trending
3. Screener: Score all 500+ stocks
4. Signal Engine: Generate signals (top 50)
5. Ollama AI: Review top 10 candidates
6. Execution: Buy 3 best signals
7. Supabase: Push trades + portfolio
8. Dashboard: Updates instantly worldwide

Afternoon (During trading):
- Trades are monitored
- Positions tracked real-time
- Dashboard shows live P&L
- Supabase updates on each change

Evening (4:15 PM):
1. Analysis: What won/lost today?
2. Optimization: Update thresholds
3. Learning: Save insights
4. Tomorrow's bot will use optimized config

Day 2:
- Bot runs with yesterday's learned thresholds
- Better signals based on what worked
- Continues to learn and improve
```

---

## Expected Timeline

| Phase | Work | Time | Start |
|-------|------|------|-------|
| 1 | Setup Finnhub + Supabase | 1-2 days | Today |
| 2 | Update core modules | 2-3 days | Tomorrow |
| 3 | Learning system | 2-3 days | Day 4 |
| 4 | Dashboard | 1-2 days | Day 6 |
| 5 | Test & deploy | 1-2 days | Day 8 |

**Ready to live trade in ~10 days**

---

## Success Metrics

✓ Bot screens 500+ stocks reliably  
✓ Executes 3-8 trades/day with $300 budget  
✓ Dashboard updates in real-time (< 1 second)  
✓ Win rate improves after learning kicks in  
✓ Profit per trade increases over time  
✓ No API failures (Finnhub 100% uptime)  

---

## Should we start building? Confirm:
- [ ] Ready to get Finnhub API key? (5 min, free)
- [ ] Ready to create Supabase project? (10 min, free)
- [ ] Good to start with Phase 1 today?
