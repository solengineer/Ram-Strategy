"""
RAM Price Monitor
Continuously scans multiple marketplaces for RAM hardware prices
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from redis import Redis
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAMType(Enum):
    """Types of RAM supported for arbitrage"""
    DDR4 = "DDR4"
    DDR5 = "DDR5"
    HBM = "HBM"
    ECC = "ECC"
    LPDDR5 = "LPDDR5"


class StockStatus(Enum):
    """Product availability status"""
    IN_STOCK = "in-stock"
    PRE_ORDER = "pre-order"
    OUT_OF_STOCK = "out-of-stock"
    LIMITED = "limited-stock"


@dataclass
class RAMPrice:
    """Data structure for RAM pricing information"""
    sku: str
    marketplace: str
    ram_type: RAMType
    capacity_gb: int
    speed_mhz: int
    price_usd: float
    timestamp: datetime
    url: str
    availability: StockStatus
    seller_rating: Optional[float] = None
    shipping_cost: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['ram_type'] = self.ram_type.value
        data['availability'] = self.availability.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def get_total_cost(self) -> float:
        """Calculate total cost including shipping"""
        return self.price_usd + (self.shipping_cost or 0.0)


class PriceMonitor:
    """
    Main price monitoring service
    Orchestrates scraping across multiple marketplaces
    """
    
    def __init__(
        self,
        marketplaces: List[str],
        redis_client: Optional[Redis] = None,
        update_interval: int = 300  # 5 minutes
    ):
        self.marketplaces = marketplaces
        self.redis = redis_client
        self.update_interval = update_interval
        self.running = False
        
    async def start(self):
        """Start continuous price monitoring"""
        self.running = True
        logger.info(f"Starting price monitor for marketplaces: {self.marketplaces}")
        
        while self.running:
            try:
                await self._scan_all_marketplaces()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Price monitor stopped")
        
    async def _scan_all_marketplaces(self):
        """Scan all configured marketplaces in parallel"""
        tasks = []
        for marketplace in self.marketplaces:
            tasks.append(self._scan_marketplace(marketplace))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        total_prices = 0
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Marketplace scan failed: {result}")
            else:
                total_prices += len(result)
                await self._store_prices(result)
        
        logger.info(f"Scanned {len(self.marketplaces)} marketplaces, found {total_prices} prices")
        
    async def _scan_marketplace(self, marketplace: str) -> List[RAMPrice]:
        """Scan a single marketplace for RAM prices"""
        logger.info(f"Scanning {marketplace}...")
        
        # Route to appropriate connector
        if marketplace == "newegg":
            return await self._scan_newegg()
        elif marketplace == "ebay":
            return await self._scan_ebay()
        elif marketplace == "amazon":
            return await self._scan_amazon()
        elif marketplace == "aliexpress":
            return await self._scan_aliexpress()
        else:
            logger.warning(f"Unknown marketplace: {marketplace}")
            return []
    
    async def _scan_newegg(self) -> List[RAMPrice]:
        """Newegg marketplace scanner"""
        # In production, this would use Newegg API
        # For now, returning mock data
        logger.info("Scanning Newegg (MOCK MODE)")
        
        mock_prices = [
            RAMPrice(
                sku="N82E16820242729",
                marketplace="newegg",
                ram_type=RAMType.DDR5,
                capacity_gb=32,
                speed_mhz=6000,
                price_usd=119.99,
                timestamp=datetime.now(),
                url="https://www.newegg.com/...",
                availability=StockStatus.IN_STOCK,
                seller_rating=4.8,
                shipping_cost=7.99
            ),
            RAMPrice(
                sku="N82E16820236892",
                marketplace="newegg",
                ram_type=RAMType.DDR5,
                capacity_gb=64,
                speed_mhz=5600,
                price_usd=239.99,
                timestamp=datetime.now(),
                url="https://www.newegg.com/...",
                availability=StockStatus.IN_STOCK,
                seller_rating=4.9,
                shipping_cost=0.0  # Free shipping
            )
        ]
        
        return mock_prices
    
    async def _scan_ebay(self) -> List[RAMPrice]:
        """eBay marketplace scanner"""
        logger.info("Scanning eBay (MOCK MODE)")
        
        mock_prices = [
            RAMPrice(
                sku="EBAY-DDR5-32GB-001",
                marketplace="ebay",
                ram_type=RAMType.DDR5,
                capacity_gb=32,
                speed_mhz=6000,
                price_usd=164.99,
                timestamp=datetime.now(),
                url="https://www.ebay.com/itm/...",
                availability=StockStatus.IN_STOCK,
                seller_rating=4.7,
                shipping_cost=12.50
            ),
            RAMPrice(
                sku="EBAY-DDR5-64GB-001",
                marketplace="ebay",
                ram_type=RAMType.DDR5,
                capacity_gb=64,
                speed_mhz=5600,
                price_usd=289.99,
                timestamp=datetime.now(),
                url="https://www.ebay.com/itm/...",
                availability=StockStatus.LIMITED,
                seller_rating=4.9,
                shipping_cost=0.0
            )
        ]
        
        return mock_prices
    
    async def _scan_amazon(self) -> List[RAMPrice]:
        """Amazon marketplace scanner"""
        logger.info("Scanning Amazon (MOCK MODE)")
        
        mock_prices = [
            RAMPrice(
                sku="B0CL6Z4J8Q",
                marketplace="amazon",
                ram_type=RAMType.DDR5,
                capacity_gb=32,
                speed_mhz=6000,
                price_usd=149.99,
                timestamp=datetime.now(),
                url="https://www.amazon.com/dp/...",
                availability=StockStatus.IN_STOCK,
                seller_rating=4.6,
                shipping_cost=0.0  # Prime shipping
            )
        ]
        
        return mock_prices
    
    async def _scan_aliexpress(self) -> List[RAMPrice]:
        """AliExpress marketplace scanner"""
        logger.info("Scanning AliExpress (MOCK MODE)")
        
        # Typically cheaper but longer shipping
        mock_prices = [
            RAMPrice(
                sku="ALI-DDR5-32GB-001",
                marketplace="aliexpress",
                ram_type=RAMType.DDR5,
                capacity_gb=32,
                speed_mhz=5600,
                price_usd=89.99,
                timestamp=datetime.now(),
                url="https://www.aliexpress.com/item/...",
                availability=StockStatus.IN_STOCK,
                seller_rating=4.3,
                shipping_cost=15.00  # International shipping
            )
        ]
        
        return mock_prices
    
    async def _store_prices(self, prices: List[RAMPrice]):
        """Store prices in Redis cache"""
        if not self.redis or not prices:
            return
        
        try:
            for price in prices:
                # Create unique key
                key = f"price:{price.marketplace}:{price.sku}"
                
                # Store with 1-hour expiration
                self.redis.setex(
                    key,
                    3600,  # 1 hour TTL
                    json.dumps(price.to_dict())
                )
            
            logger.info(f"Stored {len(prices)} prices in Redis")
        except Exception as e:
            logger.error(f"Failed to store prices in Redis: {e}")
    
    def get_arbitrage_opportunities(
        self,
        min_profit_usd: float = 20.0,
        min_margin_pct: float = 15.0
    ) -> List[Dict]:
        """
        Identify arbitrage opportunities from cached prices
        
        Args:
            min_profit_usd: Minimum profit in dollars
            min_margin_pct: Minimum profit margin percentage
        
        Returns:
            List of arbitrage opportunities
        """
        if not self.redis:
            logger.warning("Redis not configured, cannot check opportunities")
            return []
        
        opportunities = []
        
        # Get all cached prices
        keys = self.redis.keys("price:*")
        prices: List[RAMPrice] = []
        
        for key in keys:
            data = json.loads(self.redis.get(key))
            # Reconstruct RAMPrice object
            data['ram_type'] = RAMType(data['ram_type'])
            data['availability'] = StockStatus(data['availability'])
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            prices.append(RAMPrice(**data))
        
        # Group by capacity and speed to find comparable products
        products = {}
        for price in prices:
            key = (price.capacity_gb, price.speed_mhz, price.ram_type)
            if key not in products:
                products[key] = []
            products[key].append(price)
        
        # Find arbitrage opportunities
        for product_key, product_prices in products.items():
            if len(product_prices) < 2:
                continue
            
            # Sort by total cost
            product_prices.sort(key=lambda p: p.get_total_cost())
            
            lowest = product_prices[0]
            highest = product_prices[-1]
            
            # Calculate potential profit
            buy_cost = lowest.get_total_cost()
            sell_price = highest.price_usd  # Assume free shipping when selling
            
            # Estimate fees (10% typical marketplace fee)
            fees = sell_price * 0.10
            
            net_profit = sell_price - buy_cost - fees
            margin_pct = (net_profit / buy_cost) * 100
            
            if net_profit >= min_profit_usd and margin_pct >= min_margin_pct:
                opportunities.append({
                    'product': {
                        'capacity_gb': product_key[0],
                        'speed_mhz': product_key[1],
                        'type': product_key[2].value
                    },
                    'buy_from': lowest.marketplace,
                    'buy_sku': lowest.sku,
                    'buy_cost': buy_cost,
                    'sell_on': highest.marketplace,
                    'sell_price': highest.price_usd,
                    'estimated_fees': fees,
                    'net_profit': round(net_profit, 2),
                    'margin_pct': round(margin_pct, 2),
                    'confidence': self._calculate_confidence(lowest, highest)
                })
        
        # Sort by profit
        opportunities.sort(key=lambda x: x['net_profit'], reverse=True)
        
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        return opportunities
    
    def _calculate_confidence(
        self,
        buy_listing: RAMPrice,
        sell_listing: RAMPrice
    ) -> float:
        """
        Calculate confidence score for an arbitrage opportunity
        
        Factors:
        - Seller ratings
        - Stock availability
        - Price freshness
        """
        score = 0.5  # Base confidence
        
        # Seller rating factor
        if buy_listing.seller_rating:
            score += (buy_listing.seller_rating - 4.0) * 0.1  # Max +0.1
        
        if sell_listing.seller_rating:
            score += (sell_listing.seller_rating - 4.0) * 0.1
        
        # Availability factor
        if buy_listing.availability == StockStatus.IN_STOCK:
            score += 0.1
        elif buy_listing.availability == StockStatus.LIMITED:
            score += 0.05
        
        # Price freshness (within last hour = fresh)
        age_minutes = (datetime.now() - buy_listing.timestamp).seconds / 60
        if age_minutes < 60:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0


async def main():
    """Entry point for standalone execution"""
    import sys
    
    # Parse command-line arguments
    dry_run = "--dry-run" in sys.argv
    marketplaces = ["newegg", "ebay", "amazon"]
    
    if "--marketplaces" in sys.argv:
        idx = sys.argv.index("--marketplaces")
        if idx + 1 < len(sys.argv):
            marketplaces = sys.argv[idx + 1].split(",")
    
    logger.info(f"Starting Ram Strategy Price Monitor")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
    logger.info(f"Marketplaces: {marketplaces}")
    
    # Initialize (Redis optional for testing)
    monitor = PriceMonitor(
        marketplaces=marketplaces,
        redis_client=None,  # Would use Redis(host='localhost') in prod
        update_interval=300
    )
    
    # Run one scan
    await monitor._scan_all_marketplaces()
    
    # Show opportunities
    opportunities = monitor.get_arbitrage_opportunities(
        min_profit_usd=20.0,
        min_margin_pct=15.0
    )
    
    if opportunities:
        logger.info("\n" + "="*60)
        logger.info("ARBITRAGE OPPORTUNITIES DETECTED")
        logger.info("="*60)
        for i, opp in enumerate(opportunities, 1):
            logger.info(f"\n#{i}")
            logger.info(f"  Product: {opp['product']['capacity_gb']}GB {opp['product']['type']} @ {opp['product']['speed_mhz']}MHz")
            logger.info(f"  Buy: {opp['buy_from']} @ ${opp['buy_cost']:.2f}")
            logger.info(f"  Sell: {opp['sell_on']} @ ${opp['sell_price']:.2f}")
            logger.info(f"  Net Profit: ${opp['net_profit']:.2f} ({opp['margin_pct']:.1f}% margin)")
            logger.info(f"  Confidence: {opp['confidence']:.2f}")
    else:
        logger.info("No profitable opportunities found at this time")
    
    if not dry_run:
        # Start continuous monitoring
        logger.info("\nStarting continuous monitoring...")
        await monitor.start()


if __name__ == "__main__":
    asyncio.run(main())
