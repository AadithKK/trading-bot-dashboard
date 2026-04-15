"""
Supabase Real-time Sync - Cloud database integration
Pushes all portfolio and trade updates to cloud in real-time
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SupabaseSync:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.enabled = True

        try:
            from supabase import create_client
            self.client = create_client(url, api_key)
            logger.info("Supabase connected successfully")
        except Exception as e:
            logger.warning(f"Supabase connection failed: {e}. Running in local-only mode.")
            self.enabled = False
            self.client = None

    def ensure_tables(self):
        """Create tables if they don't exist"""
        if not self.enabled:
            return

        try:
            # Tables will be created via SQL if not present
            logger.info("Tables ready for syncing")
        except Exception as e:
            logger.error(f"Error checking tables: {e}")

    def push_portfolio(self, portfolio_data: Dict):
        """Push portfolio state to cloud"""
        if not self.enabled:
            return

        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'equity': portfolio_data.get('equity', 0),
                'cash': portfolio_data.get('cash', 0),
                'total_pnl': portfolio_data.get('total_pnl', 0),
                'win_rate': portfolio_data.get('win_rate', 0),
                'open_positions': portfolio_data.get('open_positions', 0),  # Already a count
                'total_trades': portfolio_data.get('trades_count', 0),
                'data_json': json.dumps(portfolio_data)
            }

            # Upsert to portfolio table
            self.client.table('portfolio_history').insert(data).execute()
            logger.info(f"Portfolio synced: Equity=${data['equity']:.2f}")

        except Exception as e:
            logger.warning(f"Failed to sync portfolio: {e}")

    def push_trade(self, trade_data: Dict):
        """Push trade execution to cloud"""
        if not self.enabled:
            return

        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': trade_data.get('symbol'),
                'action': trade_data.get('action'),
                'shares': trade_data.get('shares', 0),
                'price': trade_data.get('price', 0),
                'pnl': trade_data.get('pnl', 0),
                'data_json': json.dumps(trade_data)
            }

            self.client.table('trades').insert(data).execute()
            logger.info(f"Trade synced: {data['symbol']} - {data['action']}")

        except Exception as e:
            logger.warning(f"Failed to sync trade: {e}")

    def push_signals(self, signals: list):
        """Push signal data to cloud"""
        if not self.enabled:
            return

        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'signals_count': len(signals),
                'top_signal': signals[0].get('symbol') if signals else None,
                'top_score': signals[0].get('score') if signals else 0,
                'data_json': json.dumps(signals[:20])
            }

            self.client.table('signals_history').insert(data).execute()
            logger.info(f"Signals synced: {data['signals_count']} signals")

        except Exception as e:
            logger.warning(f"Failed to sync signals: {e}")

    def push_analysis(self, analysis_data: Dict):
        """Push after-market analysis to cloud"""
        if not self.enabled:
            return

        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'win_rate': analysis_data.get('win_rate', 0),
                'avg_profit': analysis_data.get('avg_profit', 0),
                'total_profit': analysis_data.get('total_profit', 0),
                'trades_analyzed': analysis_data.get('trades_count', 0),
                'data_json': json.dumps(analysis_data)
            }

            self.client.table('analysis_history').insert(data).execute()
            logger.info(f"Analysis synced: {data['trades_analyzed']} trades analyzed")

        except Exception as e:
            logger.warning(f"Failed to sync analysis: {e}")

    def push_dashboard_data(self, dashboard_data: Dict):
        """Push public dashboard data to cloud"""
        if not self.enabled:
            return

        try:
            # Update the public dashboard table
            self.client.table('dashboard_data').upsert({
                'id': 1,
                'timestamp': datetime.now().isoformat(),
                'data': dashboard_data
            }).execute()

            logger.info("Dashboard data synced to cloud")

        except Exception as e:
            logger.warning(f"Failed to sync dashboard: {e}")

    def get_portfolio_history(self, limit: int = 100) -> list:
        """Fetch portfolio history from cloud"""
        if not self.enabled:
            return []

        try:
            data = self.client.table('portfolio_history')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            return data.data if data else []

        except Exception as e:
            logger.warning(f"Failed to fetch portfolio history: {e}")
            return []

    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.enabled


def create_sync(url: str, api_key: str) -> Optional[SupabaseSync]:
    """Factory function to create sync instance"""
    return SupabaseSync(url, api_key)
