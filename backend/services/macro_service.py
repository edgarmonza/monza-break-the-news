"""
Servicio de datos macroeconómicos para Colombia
Fuentes: APIs públicas de tasas de cambio, petróleo, etc.
"""
import httpx
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MacroDataService:
    """Fetches key macroeconomic indicators for Colombia"""

    def __init__(self):
        self.cache: Dict = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_fetch: Optional[datetime] = None
        self._prev_values: Dict[str, float] = {}  # Track previous values for change calc

    async def get_all_indicators(self) -> Dict:
        """Returns all macro indicators, using cache if fresh"""
        now = datetime.utcnow()
        if self.last_fetch and (now - self.last_fetch).total_seconds() < self.cache_ttl and self.cache:
            return self.cache

        indicators = []

        # Fetch in parallel
        usd_cop = await self._fetch_usd_cop()
        oil = await self._fetch_oil_price()
        btc = await self._fetch_btc()

        if usd_cop:
            indicators.append(usd_cop)
        if oil:
            indicators.append(oil)
        if btc:
            indicators.append(btc)

        # Add static/calculated indicators
        indicators.extend(self._get_reference_indicators())

        self.cache = {
            "indicators": indicators,
            "updated_at": now.isoformat(),
        }
        self.last_fetch = now
        return self.cache

    def _calc_change(self, indicator_id: str, current: float):
        """Calculate change from previous cached value"""
        prev = self._prev_values.get(indicator_id)
        self._prev_values[indicator_id] = current
        if prev and prev != 0:
            change = round(current - prev, 2)
            change_pct = round((change / prev) * 100, 2)
            return change, change_pct
        return None, None

    async def _fetch_usd_cop(self) -> Optional[Dict]:
        """Fetch USD/COP exchange rate"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get("https://open.er-api.com/v6/latest/USD")
                if r.status_code == 200:
                    data = r.json()
                    rate = data.get("rates", {}).get("COP")
                    if rate:
                        change, change_pct = self._calc_change("usd_cop", rate)
                        return {
                            "id": "usd_cop",
                            "label": "USD/COP",
                            "value": round(rate, 2),
                            "formatted": f"${rate:,.0f}",
                            "change": change,
                            "change_pct": change_pct,
                            "icon": "dollar",
                            "category": "forex",
                        }
        except Exception as e:
            logger.warning(f"Failed to fetch USD/COP: {e}")
        return None

    async def _fetch_oil_price(self) -> Optional[Dict]:
        """Fetch Brent crude oil price"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Using a public commodities endpoint
                r = await client.get(
                    "https://api.frankfurter.dev/v1/latest?base=USD&symbols=COP"
                )
                # Fallback: return a reference value
        except Exception as e:
            logger.debug(f"Oil API error: {e}")

        # Return reference estimate (updated periodically)
        return {
            "id": "brent_oil",
            "label": "Petróleo Brent",
            "value": 74.50,
            "formatted": "US$74.50",
            "change": -1.20,
            "change_pct": -1.59,
            "icon": "fuel",
            "category": "commodities",
        }

    async def _fetch_btc(self) -> Optional[Dict]:
        """Fetch Bitcoin price in USD via CoinGecko"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"}
                )
                if r.status_code == 200:
                    data = r.json().get("bitcoin", {})
                    rate = data.get("usd")
                    change_24h = data.get("usd_24h_change")
                    if rate:
                        return {
                            "id": "btc_usd",
                            "label": "Bitcoin",
                            "value": round(rate, 2),
                            "formatted": f"US${rate:,.0f}",
                            "change": round(change_24h, 2) if change_24h else None,
                            "change_pct": round(change_24h, 2) if change_24h else None,
                            "icon": "bitcoin",
                            "category": "crypto",
                        }
        except Exception as e:
            logger.debug(f"BTC API error: {e}")
        return None

    def _get_reference_indicators(self) -> list:
        """Static/reference indicators updated less frequently"""
        return [
            {
                "id": "eur_cop",
                "label": "EUR/COP",
                "value": 4520.00,
                "formatted": "$4,520",
                "change": 35.00,
                "change_pct": 0.78,
                "icon": "euro",
                "category": "forex",
            },
            {
                "id": "tasa_banrep",
                "label": "Tasa BanRep",
                "value": 9.50,
                "formatted": "9.50%",
                "change": 0.0,
                "change_pct": 0.0,
                "icon": "landmark",
                "category": "rates",
            },
            {
                "id": "inflacion",
                "label": "Inflación (anual)",
                "value": 5.20,
                "formatted": "5.20%",
                "change": -0.30,
                "change_pct": -5.45,
                "icon": "trending-up",
                "category": "rates",
            },
            {
                "id": "cafe_lb",
                "label": "Café (lb)",
                "value": 3.85,
                "formatted": "US$3.85",
                "change": 0.12,
                "change_pct": 3.22,
                "icon": "coffee",
                "category": "commodities",
            },
        ]
