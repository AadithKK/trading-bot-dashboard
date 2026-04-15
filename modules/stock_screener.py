"""
Stock Screener - Score 500+ stocks for trading signals
Ranks by profit potential
"""

import logging
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class StockScreener:
    def __init__(self, config: Dict):
        self.config = config
        self.thresholds = config.get('signal_thresholds', {})

    def score_stock(self, symbol: str, quote: Dict, trend: float = 0) -> Dict:
        """Score a stock 0-100 based on profit potential"""

        try:
            price = quote.get('c', 0)
            change = quote.get('dp', 0)  # Percent change
            volume = quote.get('v', 0)
            prev_volume = quote.get('prevC', 1)

            if price <= 0:
                return {'symbol': symbol, 'score': 0, 'reason': 'No price data'}

            # Volume ratio
            volume_ratio = volume / max(prev_volume, 1)

            # Volatility (price movement magnitude)
            volatility = abs(change)

            # Score components (0-100)
            score = 0
            components = {}

            # 1. PRICE ACTION (+30 points)
            # Stocks with 2-8% daily move are optimal
            if 2 <= volatility <= 8:
                price_score = 30
            elif 1 <= volatility < 2:
                price_score = 15
            elif 8 < volatility <= 12:
                price_score = 20
            else:
                price_score = 0

            score += price_score
            components['price_action'] = price_score

            # 2. VOLUME (+25 points)
            # High volume = easier to execute trades
            if volume_ratio >= 1.5:
                volume_score = 25
            elif volume_ratio >= 1.2:
                volume_score = 15
            elif volume_ratio >= 0.8:
                volume_score = 8
            else:
                volume_score = 0

            score += volume_score
            components['volume'] = volume_score

            # 3. MOMENTUM (+20 points)
            # Positive momentum = higher probability of profit
            if change > 1:
                momentum_score = 20
            elif change > 0:
                momentum_score = 10
            elif change > -1:
                momentum_score = 5
            else:
                momentum_score = 0

            score += momentum_score
            components['momentum'] = momentum_score

            # 4. VOLATILITY PENALTY (-15 points)
            # Too much volatility = risky, hard to predict
            if volatility > 12:
                volatility_penalty = -15
            elif volatility > 8:
                volatility_penalty = -10
            else:
                volatility_penalty = 0

            score += volatility_penalty
            components['volatility_penalty'] = volatility_penalty

            # 5. LIQUIDITY (+10 points)
            # Good liquidity = can enter/exit quickly
            if volume > 5000000:
                liquidity_score = 10
            elif volume > 1000000:
                liquidity_score = 5
            else:
                liquidity_score = 0

            score += liquidity_score
            components['liquidity'] = liquidity_score

            # Ensure score is 0-100
            score = max(0, min(100, score))

            return {
                'symbol': symbol,
                'score': round(score, 1),
                'components': components,
                'price': price,
                'change': round(change, 2),
                'volume': volume,
                'volume_ratio': round(volume_ratio, 2)
            }

        except Exception as e:
            logger.error(f"Error scoring {symbol}: {e}")
            return {'symbol': symbol, 'score': 0, 'reason': str(e)}

    def screen_batch(self, stocks: List[Dict]) -> List[Dict]:
        """Score a batch of stocks and rank by profit potential"""

        try:
            logger.info(f"Screening {len(stocks)} stocks...")

            scored = []

            for stock in stocks:
                symbol = stock.get('symbol')
                quote = stock

                score_result = self.score_stock(symbol, quote)
                scored.append(score_result)

            # Sort by score (highest first)
            scored.sort(key=lambda x: x.get('score', 0), reverse=True)

            # Save to file
            with open('data/screened_stocks.json', 'w') as f:
                json.dump(scored[:150], f, indent=2)

            logger.info(f"Screening complete. Top 10:")
            for stock in scored[:10]:
                logger.info(f"  {stock['symbol']}: {stock['score']}")

            return scored

        except Exception as e:
            logger.error(f"Batch screening failed: {e}")
            return []

    def get_ai_review_candidates(self, scored_stocks: List[Dict], top_n: int = 15) -> List[Dict]:
        """Get stocks scoring 70+ for Ollama AI review"""

        candidates = [s for s in scored_stocks if s.get('score', 0) >= 70][:top_n]

        logger.info(f"AI review candidates: {len(candidates)} stocks")

        return candidates
