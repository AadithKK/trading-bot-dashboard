#!/usr/bin/env python3
"""
Trading Bot v2 - Finnhub + Supabase + Stock Screener
Real-time trading with 500+ stock universe and cloud sync
"""

import json
import logging
import argparse
import sys
from datetime import datetime
from pathlib import Path

from modules.logger import setup_logging, TradeLogger
from modules.finnhub_data import FinnhubDataFetcher
from modules.stock_screener import StockScreener
from modules.signal_engine import SignalEngine
from modules.ai_decision import OllamaAIDecider
from modules.execution import PaperExecutionEngine, Portfolio
from modules.supabase_sync import SupabaseSync

logger = logging.getLogger(__name__)

class TradingBotV2:
    def __init__(self, config_file: str = 'config.json'):
        self.config = self.load_config(config_file)
        logger.info("=" * 60)
        logger.info("TRADING BOT V2 STARTED (Finnhub + Supabase)")
        logger.info("=" * 60)

        # Initialize components
        self.portfolio = Portfolio(self.config)

        # Finnhub data fetcher (reliable)
        finnhub_key = self.config['finnhub']['api_key']
        self.data_fetcher = FinnhubDataFetcher(finnhub_key)

        # Stock screener (500+ stocks)
        self.screener = StockScreener(self.config)

        # Signal engine
        self.signal_engine = SignalEngine(self.config)

        # AI decision (Ollama)
        self.ai_decider = OllamaAIDecider(self.config)

        # Execution engine (paper trading)
        self.execution_engine = PaperExecutionEngine(self.config, self.portfolio)

        # Logging
        self.trade_logger = TradeLogger()

        # Cloud sync (Supabase)
        supabase_config = self.config.get('supabase', {})
        self.cloud_sync = SupabaseSync(
            supabase_config.get('url', ''),
            supabase_config.get('anon_key', '')
        ) if supabase_config.get('enabled') else None

    def load_config(self, config_file: str) -> dict:
        """Load configuration from JSON."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            sys.exit(1)

    def run_cycle(self, force: bool = False) -> bool:
        """Run a complete trading cycle."""
        logger.info("Starting trading cycle...")

        # Check market hours (skip if not trading day)
        if not force and not self._is_trading_day():
            logger.info("Not a trading day, skipping cycle")
            return False

        run_stats = {
            'timestamp': datetime.now().isoformat(),
            'symbols_scanned': 0,
            'signals_generated': 0,
            'trades_opened': 0,
            'trades_closed': 0,
            'portfolio_equity': self.portfolio.equity,
            'ai_available': False
        }

        try:
            # Step 1: Screen 500+ stocks with Finnhub
            logger.info("Screening 500+ stocks...")
            screened_stocks = self.data_fetcher.screen_stocks(
                min_volume=self.config['screening']['min_volume'],
                min_price=self.config['screening']['min_price'],
                max_price=self.config['screening']['max_price']
            )

            if not screened_stocks:
                logger.warning("No stocks passed screening")
                return False

            run_stats['symbols_scanned'] = len(screened_stocks)
            logger.info(f"Screened {len(screened_stocks)} stocks")

            # Step 2: Score all stocks by profit potential
            logger.info("Scoring stocks...")
            scored_stocks = self.screener.screen_batch(screened_stocks)
            strong_signals = [s for s in scored_stocks if s.get('score', 0) >= 70]

            logger.info(f"Generated {len(strong_signals)} valid signals (score >= 70)")
            run_stats['signals_generated'] = len(strong_signals)

            # Step 3: Update existing positions (check stop loss / take profit)
            logger.info("Updating open positions...")
            closed_trades = self._update_open_positions(scored_stocks)
            for trade in closed_trades:
                self.trade_logger.log_closed_trade(trade)
            logger.info(f"Closed {len(closed_trades)} positions")
            run_stats['trades_closed'] = len(closed_trades)

            # Step 4: Check AI availability
            ai_available = self.ai_decider.is_available()
            run_stats['ai_available'] = ai_available
            logger.info(f"Ollama AI: {'AVAILABLE' if ai_available else 'UNAVAILABLE'}")

            # Step 5: Get candidates for AI review (score >= 70)
            candidates = self.screener.get_ai_review_candidates(strong_signals, top_n=15)
            auto_approve = [s for s in strong_signals if s.get('score', 0) >= 85]

            logger.info(f"AI review candidates: {len(candidates)}, Auto-approve: {len(auto_approve)}")

            # Step 6: Get AI decisions
            decisions = []

            # Auto-approve high-confidence trades (score >= 85)
            for signal in auto_approve:
                decisions.append({
                    'symbol': signal['symbol'],
                    'action': 'BUY',
                    'confidence': min(100, signal['score']),
                    'position_size_percent': self.config['trading']['position_size_percent'],
                    'stop_loss_percent': self.config['trading']['stop_loss_percent'],
                    'take_profit_percent': self.config['trading']['take_profit_percent'],
                    'reasoning': 'auto_approved',
                    'price': signal.get('price', 0)
                })

            # Get AI decisions for borderline signals (70-85)
            if candidates and ai_available:
                portfolio_state = {
                    'cash': self.portfolio.get_cash(),
                    'open_positions': len(self.portfolio.open_positions),
                    'max_positions': self.config['trading']['max_open_positions'],
                    'equity': self.portfolio.equity
                }
                ai_decisions = self.ai_decider.get_ai_decisions(candidates, portfolio_state)
                if ai_decisions:
                    decisions.extend(ai_decisions)

            logger.info(f"Total decisions: {len(decisions)}")

            # Step 7: Execute trades
            for decision in decisions:
                symbol = decision['symbol']
                price = decision.get('price', 0)

                if price > 0:
                    trade = self.execution_engine.execute_trade(decision, price)
                    if trade:
                        run_stats['trades_opened'] += 1
                        # Sync to cloud
                        if self.cloud_sync:
                            self.cloud_sync.push_trade(trade)

            # Step 8: Save portfolio
            self.portfolio.save_portfolio()
            run_stats['portfolio_equity'] = self.portfolio.equity

            # Step 9: Log run
            self.trade_logger.log_run(run_stats)

            # Step 10: Sync to cloud
            if self.cloud_sync:
                self.cloud_sync.push_portfolio(self.portfolio.to_dict())
                self.cloud_sync.push_signals(strong_signals[:20])

            logger.info(f"Cycle complete: Equity=${self.portfolio.equity:.2f}, "
                       f"Cash=${self.portfolio.get_cash():.2f}, "
                       f"Win rate: {self.portfolio.win_rate:.1f}%")

            return True

        except Exception as e:
            logger.error(f"Cycle failed: {str(e)}", exc_info=True)
            run_stats['status'] = 'failed'
            self.trade_logger.log_run(run_stats)
            return False

    def _update_open_positions(self, scored_stocks: list) -> list:
        """Update open positions with current prices and check exits"""
        closed_trades = []

        # Create lookup dict
        stock_dict = {s['symbol']: s for s in scored_stocks}

        for position in list(self.portfolio.open_positions):
            symbol = position['symbol']

            if symbol in stock_dict:
                current_price = stock_dict[symbol]['price']

                # Check stop loss / take profit
                entry_price = position['entry_price']
                change_percent = ((current_price - entry_price) / entry_price) * 100

                # Stop loss
                if change_percent <= -self.config['trading']['stop_loss_percent']:
                    closed_trade = self.execution_engine.close_position(symbol, current_price, 'stop_loss')
                    if closed_trade:
                        closed_trades.append(closed_trade)

                # Take profit
                elif change_percent >= self.config['trading']['take_profit_percent']:
                    closed_trade = self.execution_engine.close_position(symbol, current_price, 'take_profit')
                    if closed_trade:
                        closed_trades.append(closed_trade)

        return closed_trades

    def _is_trading_day(self) -> bool:
        """Check if today is a trading day."""
        from datetime import datetime as dt
        today = dt.now()

        # Skip weekends
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        return True

    def print_status(self):
        """Print current portfolio status."""
        logger.info("\n" + "=" * 60)
        logger.info("PORTFOLIO STATUS")
        logger.info("=" * 60)
        stats = self.portfolio.to_dict()
        for key, value in stats.items():
            logger.info(f"{key:.<40} {value}")
        logger.info("=" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Trading Bot V2 - Finnhub + Supabase')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--force', action='store_true', help='Force run even outside market hours')
    parser.add_argument('--status', action='store_true', help='Print portfolio status and exit')
    args = parser.parse_args()

    # Setup logging
    config = json.load(open(args.config)) if Path(args.config).exists() else {}
    setup_logging(config)

    # Create bot
    bot = TradingBotV2(args.config)

    # Run based on arguments
    if args.status:
        bot.print_status()
    else:
        bot.run_cycle(force=args.force)

if __name__ == '__main__':
    main()
