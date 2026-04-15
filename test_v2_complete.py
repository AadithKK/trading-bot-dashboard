#!/usr/bin/env python3
"""
Test Trading Bot V2 with Mock Data
Verifies: Finnhub screener → Signal engine → AI decision → Execution → Supabase sync
"""

import json
import logging
from datetime import datetime
from modules.logger import setup_logging
from modules.stock_screener import StockScreener
from modules.signal_engine import SignalEngine
from modules.ai_decision import OllamaAIDecider
from modules.execution import PaperExecutionEngine, Portfolio
from modules.supabase_sync import SupabaseSync

# Setup logging
config = json.load(open('config.json'))
setup_logging(config)
logger = logging.getLogger(__name__)

# Generate mock stocks (simulating Finnhub screening)
def generate_mock_stocks():
    """Create 50 mock stocks for testing"""
    stocks = [
        {
            'symbol': 'AAPL',
            'c': 185.50,  # current price
            'dp': 2.5,    # percent change
            'v': 52000000,  # volume
            'price': 185.50,
            'change': 2.5,
            'volume': 52000000,
            'change_percent': 2.5
        },
        {
            'symbol': 'NVDA',
            'c': 875.30,
            'dp': 3.2,
            'v': 48000000,
            'price': 875.30,
            'change': 3.2,
            'volume': 48000000,
            'change_percent': 3.2
        },
        {
            'symbol': 'MSFT',
            'c': 420.15,
            'dp': 1.8,
            'v': 35000000,
            'price': 420.15,
            'change': 1.8,
            'volume': 35000000,
            'change_percent': 1.8
        },
        {
            'symbol': 'TSLA',
            'c': 245.60,
            'dp': 4.1,
            'v': 62000000,
            'price': 245.60,
            'change': 4.1,
            'volume': 62000000,
            'change_percent': 4.1
        },
        {
            'symbol': 'META',
            'c': 480.25,
            'dp': 2.9,
            'v': 41000000,
            'price': 480.25,
            'change': 2.9,
            'volume': 41000000,
            'change_percent': 2.9
        },
    ]
    return stocks

def run_test():
    """Run full trading cycle with mock data"""
    logger.info("=" * 60)
    logger.info("TRADING BOT V2 TEST (Mock Data)")
    logger.info("=" * 60)

    # Initialize components
    portfolio = Portfolio(config)
    screener = StockScreener(config)
    signal_engine = SignalEngine(config)
    ai_decider = OllamaAIDecider(config)
    execution = PaperExecutionEngine(config, portfolio)

    # Supabase sync
    supabase = SupabaseSync(
        config['supabase']['url'],
        config['supabase']['anon_key']
    )

    logger.info(f"Starting portfolio: ${portfolio.equity:.2f} cash")

    # Step 1: Screen stocks
    logger.info("\n[STEP 1] Screening stocks...")
    mock_stocks = generate_mock_stocks()
    logger.info(f"  Mock stocks: {len(mock_stocks)} stocks")

    # Step 2: Score stocks
    logger.info("\n[STEP 2] Scoring stocks...")
    scored = screener.screen_batch(mock_stocks)
    strong_signals = [s for s in scored if s.get('score', 0) >= 70]
    logger.info(f"  Strong signals: {len(strong_signals)} stocks")

    for signal in strong_signals[:5]:
        logger.info(f"    {signal['symbol']}: {signal['score']:.1f}")

    # Step 3: Get candidates for AI
    logger.info("\n[STEP 3] Getting AI review candidates...")
    candidates = screener.get_ai_review_candidates(strong_signals, top_n=5)
    logger.info(f"  AI candidates: {len(candidates)} stocks")

    # Step 4: Get AI decisions
    logger.info("\n[STEP 4] Getting AI decisions...")
    ai_available = ai_decider.is_available()
    logger.info(f"  Ollama available: {ai_available}")

    portfolio_state = {
        'cash': portfolio.get_cash(),
        'open_positions': len(portfolio.open_positions),
        'max_positions': config['trading']['max_open_positions'],
        'equity': portfolio.equity
    }

    decisions = []

    # Auto-approve high confidence
    auto_approve = [s for s in strong_signals if s.get('score', 0) >= 85]
    for signal in auto_approve:
        decisions.append({
            'symbol': signal['symbol'],
            'action': 'BUY',
            'confidence': min(100, signal['score']),
            'position_size_percent': config['trading']['position_size_percent'],
            'stop_loss_percent': config['trading']['stop_loss_percent'],
            'take_profit_percent': config['trading']['take_profit_percent'],
            'reasoning': 'auto_approved',
            'price': signal.get('price', 0)
        })

    # AI review for borderline
    if candidates and ai_available:
        ai_decisions = ai_decider.get_ai_decisions(candidates, portfolio_state)
        if ai_decisions:
            decisions.extend(ai_decisions)

    logger.info(f"  Total decisions: {len(decisions)} trades")

    # Step 5: Execute trades
    logger.info("\n[STEP 5] Executing trades...")
    trades_opened = 0
    for decision in decisions[:3]:  # Limit to 3 for testing
        symbol = decision['symbol']
        price = decision.get('price', 0)

        if price > 0:
            trade = execution.execute_trade(decision, price)
            if trade:
                trades_opened += 1
                logger.info(f"  ✓ {symbol}: BUY {trade['shares']:.4f} @ ${price}")

                # Sync to cloud
                supabase.push_trade(trade)

    # Step 6: Save and sync
    logger.info("\n[STEP 6] Saving and syncing...")
    portfolio.save_portfolio()

    supabase.push_portfolio(portfolio.to_dict())
    supabase.push_signals(strong_signals[:10])

    logger.info(f"  Portfolio saved")
    logger.info(f"  Cloud synced")

    # Final status
    logger.info("\n" + "=" * 60)
    logger.info("FINAL STATUS")
    logger.info("=" * 60)
    logger.info(f"  Equity: ${portfolio.equity:.2f}")
    logger.info(f"  Cash: ${portfolio.get_cash():.2f}")
    logger.info(f"  Open positions: {len(portfolio.open_positions)}")
    logger.info(f"  Trades executed: {trades_opened}")
    logger.info("=" * 60 + "\n")

    return trades_opened > 0

if __name__ == '__main__':
    success = run_test()
    exit(0 if success else 1)
