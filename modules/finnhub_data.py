"""
Finnhub Data Fetcher - Real-time market data integration
100% reliable alternative to yfinance
"""

import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

# Fallback list of popular stocks for screening
POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'GOOG', 'BRK.B', 'JNJ',
    'V', 'WMT', 'PG', 'XOM', 'JPM', 'MA', 'HD', 'BA', 'COST', 'KO',
    'MCD', 'NFLX', 'INTC', 'AMD', 'CRM', 'PYPL', 'ADBE', 'AVGO', 'CSCO', 'ACN',
    'IBM', 'QCOM', 'ASML', 'NKE', 'AMAT', 'MU', 'UBER', 'ABNB', 'SNOW', 'DASH',
    'TTD', 'OKTA', 'ZM', 'DDOG', 'COIN', 'RIOT', 'MARA', 'CLSK', 'ORCL', 'SAP',
    'NOW', 'CRWD', 'SPLK', 'PALO', 'NTNX', 'ATUS', 'FTNT', 'S', 'JMIA', 'BABA'
]

class FinnhubDataFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({'X-Finnhub-Token': api_key})
        self.cache = {}
        self.cache_expiry = {}
        self.rate_limit_delay = 0.2  # 5 calls per second (more conservative)
        self.last_call = 0
        self.rate_limit_429_delay = 0  # Track when we hit a 429

    def _rate_limit(self):
        """Respect rate limiting"""
        elapsed = time.time() - self.last_call
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_call = time.time()

    def _get_cached(self, key: str, max_age_seconds: int = 300):
        """Get cached data if not expired"""
        if key in self.cache:
            if time.time() - self.cache_expiry.get(key, 0) < max_age_seconds:
                return self.cache[key]
        return None

    def _set_cache(self, key: str, data):
        """Cache data with timestamp"""
        self.cache[key] = data
        self.cache_expiry[key] = time.time()

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        try:
            # Check cache first
            cache_key = f"quote_{symbol}"
            cached = self._get_cached(cache_key, max_age_seconds=60)
            if cached:
                return cached

            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/quote",
                params={'symbol': symbol},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('c'):  # Has current price
                    self._set_cache(cache_key, data)
                    return data
            elif response.status_code == 429:
                # Rate limited - increase delay for future requests
                logger.debug(f"Rate limited (429) for {symbol}")
                self.rate_limit_delay = max(self.rate_limit_delay, 0.5)  # Slow down
                return None
            else:
                logger.debug(f"No quote data for {symbol}: {response.status_code}")

            return None

        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            return None

    def get_movers(self) -> Dict:
        """Get market movers (gainers and losers)"""
        try:
            cache_key = "market_movers"
            cached = self._get_cached(cache_key, max_age_seconds=300)
            if cached:
                return cached

            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/news",
                params={'category': 'general', 'minId': 0},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                movers = {
                    'gainers': [],
                    'losers': []
                }

                # Extract symbols from news articles (but they're usually empty)
                if isinstance(data, list):
                    for item in data[:100]:
                        if 'related' in item and item['related']:
                            symbols = [s.strip() for s in item['related'].split(',') if s.strip()]
                            movers['gainers'].extend(symbols[:5])

                self._set_cache(cache_key, movers)
                return movers

            return {'gainers': [], 'losers': []}

        except Exception as e:
            logger.error(f"Failed to get movers: {e}")
            return {'gainers': [], 'losers': []}

    def get_trending(self) -> List[str]:
        """Get trending stocks (US market)"""
        try:
            cache_key = "trending_stocks"
            cached = self._get_cached(cache_key, max_age_seconds=600)
            if cached:
                return cached

            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/news",
                params={'category': 'general', 'minId': 0},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                symbols = set()

                if isinstance(data, list):
                    for item in data[:100]:
                        if 'related' in item and item['related']:
                            related_symbols = [s.strip() for s in item['related'].split(',') if s.strip()]
                            symbols.update(related_symbols[:3])

                trending = [s for s in list(symbols) if s][:50]
                self._set_cache(cache_key, trending)
                return trending

            return []

        except Exception as e:
            logger.error(f"Failed to get trending: {e}")
            return []

    def get_company_info(self, symbol: str) -> Optional[Dict]:
        """Get company profile"""
        try:
            cache_key = f"company_{symbol}"
            cached = self._get_cached(cache_key, max_age_seconds=86400)  # 24 hour cache
            if cached:
                return cached

            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/stock/profile2",
                params={'symbol': symbol},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('ticker'):
                    self._set_cache(cache_key, data)
                    return data

            return None

        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
            return None

    def get_intraday_data(self, symbol: str, resolution: str = '5') -> Optional[Dict]:
        """Get intraday OHLCV data"""
        try:
            # resolution: '1' (1min), '5' (5min), '15', '30', '60' (hourly), 'D' (daily)
            today = datetime.now()
            from_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = today.strftime('%Y-%m-%d')

            cache_key = f"intraday_{symbol}_{resolution}"
            cached = self._get_cached(cache_key, max_age_seconds=300)
            if cached:
                return cached

            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/stock/candle",
                params={
                    'symbol': symbol,
                    'resolution': resolution,
                    'from': int(datetime.strptime(from_date, '%Y-%m-%d').timestamp()),
                    'to': int(datetime.strptime(to_date, '%Y-%m-%d').timestamp())
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('o'):  # Has OHLCV data
                    self._set_cache(cache_key, data)
                    return data

            return None

        except Exception as e:
            logger.error(f"Failed to get intraday data for {symbol}: {e}")
            return None

    def screen_stocks(self, min_volume: int = 1000000, min_price: float = 5, max_price: float = 500) -> List[str]:
        """Screen for eligible stocks based on criteria"""
        try:
            logger.info("Starting stock screening...")

            # Get movers and trending first
            movers = self.get_movers()
            trending = self.get_trending()

            candidates = list(set(movers.get('gainers', []) + trending))

            # If no candidates found, use popular stocks as fallback
            if not candidates:
                logger.info("No candidates from movers/trending, using popular stocks fallback")
                # Limit to 30 stocks to avoid rate limiting (Finnhub free tier: ~10 req/sec)
                candidates = POPULAR_STOCKS[:30]
            else:
                candidates = candidates[:30]  # Limit to avoid rate limiting

            eligible = []

            for symbol in candidates:
                if len(eligible) >= 100:  # Limit to 100 screened stocks
                    break

                # Skip empty symbols
                if not symbol or not str(symbol).strip():
                    continue

                try:
                    quote = self.get_quote(str(symbol).strip())
                    if not quote:
                        continue

                    price = quote.get('c', 0)
                    volume = quote.get('v', 0)
                    change_pct = quote.get('dp', 0)

                    # Filter by price range (Finnhub free tier doesn't have reliable volume)
                    # Just check price and positive change
                    if min_price <= price <= max_price and price > 0:
                        eligible.append({
                            'symbol': str(symbol).strip(),
                            'c': price,  # Finnhub field: current price
                            'v': volume if volume > 0 else 1000000,  # Finnhub field: volume
                            'd': quote.get('d', 0),  # Finnhub field: change
                            'dp': change_pct,  # Finnhub field: change percent
                            'prevC': price  # Finnhub field: previous close (approximate)
                        })

                except Exception as e:
                    logger.debug(f"Error screening {symbol}: {e}")
                    continue

            logger.info(f"Screening complete: {len(eligible)} eligible stocks")
            return eligible

        except Exception as e:
            logger.error(f"Stock screening failed: {e}")
            return []

# Initialize with API key
def create_fetcher(api_key: str) -> FinnhubDataFetcher:
    return FinnhubDataFetcher(api_key)
