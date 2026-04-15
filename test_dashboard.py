#!/usr/bin/env python3
"""
Test Dashboard - Generate mock data to preview the dashboard locally
Run this script, then open docs/dashboard.html in your browser to see the dashboard with test data
"""

import json
import os
from datetime import datetime, timedelta
import random

def generate_test_data():
    """Generate realistic test data for the dashboard"""

    # Create data directory if it doesn't exist
    os.makedirs('docs/data', exist_ok=True)

    # Generate portfolio data
    portfolio = {
        "starting_balance": 10000,
        "equity": 10523.45,
        "cash": 4200.50,
        "total_pnl": 523.45,
        "win_rate": 66.67,
        "trades_count": 3,
        "win_count": 2,
        "loss_count": 1,
        "open_positions": [
            {
                "symbol": "AAPL",
                "shares": 10.5,
                "entry_price": 185.50,
                "entry_date": datetime.now().isoformat(),
                "unrealized_pnl": 125.75
            },
            {
                "symbol": "NVDA",
                "shares": 5.25,
                "entry_price": 875.30,
                "entry_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "unrealized_pnl": 45.20
            }
        ],
        "closed_positions": [
            {
                "symbol": "MSFT",
                "shares": 8,
                "entry_price": 420.15,
                "exit_price": 428.50,
                "entry_date": (datetime.now() - timedelta(days=5)).isoformat(),
                "exit_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "pnl": 66.80,
                "reason": "take_profit"
            },
            {
                "symbol": "TSLA",
                "shares": 2,
                "entry_price": 245.60,
                "exit_price": 240.30,
                "entry_date": (datetime.now() - timedelta(days=4)).isoformat(),
                "exit_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "pnl": -10.60,
                "reason": "stop_loss"
            },
            {
                "symbol": "META",
                "shares": 6.5,
                "entry_price": 480.25,
                "exit_price": 495.80,
                "entry_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "exit_date": datetime.now().isoformat(),
                "pnl": 100.58,
                "reason": "take_profit"
            }
        ]
    }

    # Generate signals data
    signals = [
        {
            "symbol": "AAPL",
            "score": 87,
            "trend": 30,
            "rsi": 15,
            "momentum": 12,
            "volume": 14,
            "volatility": -20,
            "relative_strength": 8,
            "notes": "Strong uptrend, high momentum, elevated volume"
        },
        {
            "symbol": "NVDA",
            "score": 92,
            "trend": 30,
            "rsi": 15,
            "momentum": 15,
            "volume": 15,
            "volatility": -18,
            "relative_strength": 10,
            "notes": "Very strong signal, excellent technicals"
        },
        {
            "symbol": "MSFT",
            "score": 78,
            "trend": 30,
            "rsi": 12,
            "momentum": 10,
            "volume": 14,
            "volatility": -22,
            "relative_strength": 7,
            "notes": "Good setup, above SMA, moderate RSI"
        },
        {
            "symbol": "GOOGL",
            "score": 68,
            "trend": 20,
            "rsi": 8,
            "momentum": 8,
            "volume": 12,
            "volatility": -15,
            "relative_strength": 5,
            "notes": "Weak signal, not enough momentum"
        },
        {
            "symbol": "AMZN",
            "score": 45,
            "trend": 10,
            "rsi": 5,
            "momentum": 3,
            "volume": 8,
            "volatility": -20,
            "relative_strength": 2,
            "notes": "Below thresholds, skip"
        }
    ]

    # Generate runs data (bot execution history)
    runs = []
    base_equity = 10000
    current_time = datetime.now() - timedelta(days=10)

    for i in range(15):
        equity = base_equity + random.uniform(-100, 150)
        base_equity = equity

        run = {
            "timestamp": current_time.isoformat(),
            "portfolio_equity": equity,
            "trades_opened": random.randint(0, 3),
            "trades_closed": random.randint(0, 2),
            "signals_generated": random.randint(5, 15),
            "status": "completed"
        }
        runs.append(run)
        current_time += timedelta(hours=23)

    # Save to JSON files
    with open('docs/data/portfolio.json', 'w') as f:
        json.dump(portfolio, f, indent=2)

    with open('docs/data/signals.json', 'w') as f:
        json.dump(signals, f, indent=2)

    with open('docs/data/runs.json', 'w') as f:
        json.dump(runs, f, indent=2)

    print("[OK] Test data generated!")
    print(f"  - Portfolio: {portfolio['equity']:.2f} equity, {len(portfolio['open_positions'])} open, {portfolio['trades_count']} total")
    print(f"  - Signals: {len(signals)} signals")
    print(f"  - Runs: {len(runs)} runs")
    print("\nNow open docs/dashboard.html in your browser to see the dashboard!")

if __name__ == "__main__":
    generate_test_data()
