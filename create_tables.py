#!/usr/bin/env python3
"""
Create Supabase tables by executing SQL via admin API
Uses the service role key for full access
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase credentials
SUPABASE_URL = "https://ezalxvzpmrhrbncmqgjc.supabase.co"
PROJECT_ID = "ezalxvzpmrhrbncmqgjc"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6YWx4dnpwbXJocmJuY21xZ2pjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxMjAzNDg4NiwiZXhwIjoyMDI3NjEwODg2fQ.mPn7qL7R1X-N4Q8X9Z2Y3A5B6C7D8E9F0G1H2I3J4K"

# SQL statements for table creation
CREATE_TABLES_SQL = """
-- Portfolio history table
CREATE TABLE IF NOT EXISTS public.portfolio_history (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  timestamp TIMESTAMP,
  equity NUMERIC,
  cash NUMERIC,
  total_pnl NUMERIC,
  win_rate NUMERIC,
  open_positions INT,
  total_trades INT,
  data_json TEXT
);

-- Trades table
CREATE TABLE IF NOT EXISTS public.trades (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  timestamp TIMESTAMP,
  symbol TEXT,
  action TEXT,
  shares NUMERIC,
  price NUMERIC,
  pnl NUMERIC,
  data_json TEXT
);

-- Signals history table
CREATE TABLE IF NOT EXISTS public.signals_history (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  timestamp TIMESTAMP,
  signals_count INT,
  top_signal TEXT,
  top_score NUMERIC,
  data_json TEXT
);

-- Analysis history table
CREATE TABLE IF NOT EXISTS public.analysis_history (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  timestamp TIMESTAMP,
  win_rate NUMERIC,
  avg_profit NUMERIC,
  total_profit NUMERIC,
  trades_analyzed INT,
  data_json TEXT
);

-- Enable RLS if needed (optional)
ALTER TABLE public.portfolio_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.signals_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_history ENABLE ROW LEVEL SECURITY;
"""

def execute_sql_via_admin_api():
    """Execute SQL via Supabase admin API"""
    logger.info("Attempting to create tables via Supabase API...")

    # Try using the management API
    headers = {
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json',
        'X-Client-Info': 'trading-bot/1.0'
    }

    # Supabase management endpoints for SQL execution
    # Try the direct SQL endpoint if available
    endpoints = [
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        f"{SUPABASE_URL}/sql/v1/query",
    ]

    for endpoint in endpoints:
        try:
            logger.info(f"\nTrying endpoint: {endpoint}")
            response = requests.post(
                endpoint,
                headers=headers,
                json={"query": CREATE_TABLES_SQL},
                timeout=15
            )
            logger.info(f"Response status: {response.status_code}")
            if response.status_code in [200, 201]:
                logger.info("✓ Tables created successfully!")
                return True
            else:
                logger.warning(f"Response: {response.text[:300]}")
        except Exception as e:
            logger.warning(f"Endpoint failed: {e}")
            continue

    logger.warning("\n✗ Could not execute SQL via API")
    logger.info("\nInstructions to create tables manually:")
    logger.info("1. Go to: https://app.supabase.com/project/ezalxvzpmrhrbncmqgjc/sql/new")
    logger.info("2. Paste the SQL below and click 'Run':")
    logger.info("\n" + "=" * 60)
    logger.info(CREATE_TABLES_SQL)
    logger.info("=" * 60)

    return False

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("SUPABASE TABLE CREATION")
    logger.info("=" * 60)
    execute_sql_via_admin_api()
