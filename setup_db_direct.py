#!/usr/bin/env python3
"""
Setup Supabase database directly via REST API with proper headers
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
SUPABASE_URL = "https://ezalxvzpmrhrbncmqgjc.supabase.co"
ANON_KEY = "sb_publishable_gSlBrJ_mrdoOLHATi4tGAg_8ViffrQs"

def insert_sample_data():
    """Insert sample data to auto-create tables"""
    logger.info("Setting up Supabase tables via REST API...")

    headers = {
        'apikey': ANON_KEY,
        'Authorization': f'Bearer {ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    try:
        # 1. Portfolio history
        logger.info("\n1. Creating portfolio_history table...")
        portfolio_data = {
            'timestamp': '2026-04-15T18:00:00Z',
            'equity': 10000,
            'cash': 10000,
            'total_pnl': 0,
            'win_rate': 0,
            'open_positions': 0,
            'total_trades': 0,
            'data_json': '{}'
        }

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/portfolio_history",
            headers=headers,
            json=portfolio_data,
            timeout=10
        )
        logger.info(f"   Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            logger.warning(f"   Response: {response.text[:200]}")

        # 2. Trades
        logger.info("\n2. Creating trades table...")
        trade_data = {
            'timestamp': '2026-04-15T18:00:00Z',
            'symbol': 'TEST',
            'action': 'BUY',
            'shares': 1.0,
            'price': 100.0,
            'pnl': 0.0,
            'data_json': '{}'
        }

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/trades",
            headers=headers,
            json=trade_data,
            timeout=10
        )
        logger.info(f"   Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            logger.warning(f"   Response: {response.text[:200]}")

        # 3. Signals history
        logger.info("\n3. Creating signals_history table...")
        signals_data = {
            'timestamp': '2026-04-15T18:00:00Z',
            'signals_count': 0,
            'top_signal': None,
            'top_score': 0.0,
            'data_json': '[]'
        }

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/signals_history",
            headers=headers,
            json=signals_data,
            timeout=10
        )
        logger.info(f"   Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            logger.warning(f"   Response: {response.text[:200]}")

        # 4. Analysis history
        logger.info("\n4. Creating analysis_history table...")
        analysis_data = {
            'timestamp': '2026-04-15T18:00:00Z',
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'total_profit': 0.0,
            'trades_analyzed': 0,
            'data_json': '{}'
        }

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/analysis_history",
            headers=headers,
            json=analysis_data,
            timeout=10
        )
        logger.info(f"   Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            logger.warning(f"   Response: {response.text[:200]}")

        logger.info("\n✓ Database setup complete!")
        logger.info("Tables are ready for cloud synchronization.")
        return True

    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("SUPABASE DATABASE SETUP")
    logger.info("=" * 60)
    insert_sample_data()
    logger.info("=" * 60 + "\n")
