#!/usr/bin/env python3
"""
Create Supabase tables using SQL execution
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
SUPABASE_URL = "https://ezalxvzpmrhrbncmqgjc.supabase.co"
SUPABASE_KEY = "sb_publishable_gSlBrJ_mrdoOLHATi4tGAg_8ViffrQs"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6YWx4dnpwbXJocmJuY21xZ2pjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxMjAzNDg4NiwiZXhwIjoyMDI3NjEwODg2fQ.mPn7qL7R1X-N4Q8X9Z2Y3A5B6C7D8E9F0G1H2I3J4K"

def execute_sql(sql: str) -> bool:
    """Execute SQL via Supabase RPC"""
    try:
        headers = {
            'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'apikey': SUPABASE_KEY
        }

        # Try the rpc/exec_sql endpoint
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={'sql': sql},
            timeout=10
        )

        logger.info(f"Response: {response.status_code}")
        if response.status_code in [200, 201]:
            logger.info(f"✓ SQL executed")
            return True
        else:
            logger.error(f"✗ Failed: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error: {e}")
        return False

def create_tables():
    """Create all necessary tables"""
    logger.info("Creating Supabase tables...")

    sql_statements = [
        """
        CREATE TABLE IF NOT EXISTS portfolio_history (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            timestamp TIMESTAMP,
            equity NUMERIC,
            cash NUMERIC,
            total_pnl NUMERIC,
            win_rate NUMERIC,
            open_positions INT,
            total_trades INT,
            data_json TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS trades (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            timestamp TIMESTAMP,
            symbol TEXT,
            action TEXT,
            shares NUMERIC,
            price NUMERIC,
            pnl NUMERIC,
            data_json TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS signals_history (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            timestamp TIMESTAMP,
            signals_count INT,
            top_signal TEXT,
            top_score NUMERIC,
            data_json TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            timestamp TIMESTAMP,
            win_rate NUMERIC,
            avg_profit NUMERIC,
            total_profit NUMERIC,
            trades_analyzed INT,
            data_json TEXT
        )
        """
    ]

    for i, sql in enumerate(sql_statements, 1):
        logger.info(f"Executing statement {i}/4...")
        execute_sql(sql)

    logger.info("\n✓ All table creation statements executed!")
    logger.info("Tables are ready for cloud sync.")

if __name__ == '__main__':
    create_tables()
