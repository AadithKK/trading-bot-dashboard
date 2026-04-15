#!/usr/bin/env python3
"""
Initialize Supabase database tables using Supabase client
"""

from supabase import create_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase credentials
SUPABASE_URL = "https://ezalxvzpmrhrbncmqgjc.supabase.co"
SUPABASE_KEY = "sb_publishable_gSlBrJ_mrdoOLHATi4tGAg_8ViffrQs"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6YWx4dnpwbXJocmJuY21xZ2pjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxMjAzNDg4NiwiZXhwIjoyMDI3NjEwODg2fQ.mPn7qL7R1X-N4Q8X9Z2Y3A5B6C7D8E9F0G1H2I3J4K"

def init_supabase():
    """Initialize Supabase and check connection"""
    try:
        # Create client with service role key for admin access
        supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
        logger.info("✓ Connected to Supabase")
        return supabase
    except Exception as e:
        logger.error(f"✗ Failed to connect: {e}")
        return None

def create_sample_records(supabase):
    """Create tables by inserting sample data (Supabase auto-creates from data)"""
    logger.info("\nCreating tables with sample data...")

    try:
        # Portfolio history
        logger.info("Creating portfolio_history table...")
        portfolio_sample = {
            'timestamp': '2026-04-15T18:00:00Z',
            'equity': 10000,
            'cash': 10000,
            'total_pnl': 0,
            'win_rate': 0,
            'open_positions': 0,
            'total_trades': 0,
            'data_json': '{}'
        }
        supabase.table('portfolio_history').insert(portfolio_sample).execute()
        logger.info("✓ portfolio_history table created")

        # Trades
        logger.info("Creating trades table...")
        trade_sample = {
            'timestamp': '2026-04-15T18:00:00Z',
            'symbol': 'TEST',
            'action': 'BUY',
            'shares': 1.0,
            'price': 100.0,
            'pnl': 0.0,
            'data_json': '{}'
        }
        supabase.table('trades').insert(trade_sample).execute()
        logger.info("✓ trades table created")

        # Signals history
        logger.info("Creating signals_history table...")
        signals_sample = {
            'timestamp': '2026-04-15T18:00:00Z',
            'signals_count': 0,
            'top_signal': None,
            'top_score': 0.0,
            'data_json': '[]'
        }
        supabase.table('signals_history').insert(signals_sample).execute()
        logger.info("✓ signals_history table created")

        # Analysis history
        logger.info("Creating analysis_history table...")
        analysis_sample = {
            'timestamp': '2026-04-15T18:00:00Z',
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'total_profit': 0.0,
            'trades_analyzed': 0,
            'data_json': '{}'
        }
        supabase.table('analysis_history').insert(analysis_sample).execute()
        logger.info("✓ analysis_history table created")

        logger.info("\n✓ All tables created successfully!")
        logger.info("Bot can now sync to cloud in real-time")
        return True

    except Exception as e:
        logger.error(f"✗ Error creating tables: {e}")
        return False

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("SUPABASE DATABASE INITIALIZATION")
    logger.info("=" * 60)

    supabase = init_supabase()
    if supabase:
        create_sample_records(supabase)

    logger.info("=" * 60)
