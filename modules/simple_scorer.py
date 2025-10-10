"""
Simple Property Scorer - Lightweight scoring without database dependency

Calculates opportunity_score (0-100) based on:
1. Price vs. Market Value (40 points)
2. Days on Market (30 points)
3. Price per sqft (30 points)
"""

from datetime import datetime
from typing import Dict, List
import statistics


class SimplePropertyScorer:
    """Lightweight property scorer for real-time analysis"""

    def __init__(self, config: Dict):
        """
        Initialize scorer with configuration

        Args:
            config: Configuration dictionary from config.yaml
        """
        self.config = config

    def score_properties(self, properties: List[Dict]) -> List[Dict]:
        """
        Score a list of properties

        Args:
            properties: List of property dictionaries

        Returns:
            List of properties with added opportunity_score and scraped_date
        """
        if not properties:
            return []

        # Calculate market averages for comparison
        avg_price_per_sqft = self._calculate_avg_price_per_sqft(properties)

        scored_properties = []
        current_date = datetime.now().isoformat()

        for prop in properties:
            # Add timestamp
            prop['scraped_date'] = current_date

            # Calculate score
            score = self._calculate_opportunity_score(
                prop,
                avg_price_per_sqft
            )
            prop['opportunity_score'] = round(score, 2)

            # Add deal classification
            prop['deal_quality'] = self._classify_deal(score)

            scored_properties.append(prop)

        return scored_properties

    def _calculate_opportunity_score(self, prop: Dict, avg_price_per_sqft: float) -> float:
        """
        Calculate opportunity score (0-100)

        Scoring breakdown:
        - Price below market: 0-40 points
        - Days on market: 0-30 points
        - Price per sqft vs average: 0-30 points
        """
        score = 0.0

        # 1. Price below market (40 points max)
        list_price = prop.get('list_price', 0)
        assessed_value = (prop.get('tax_assessed_value', 0) or
                         prop.get('assessed_value', 0) or
                         prop.get('estimated_value', 0))

        if list_price and assessed_value and list_price < assessed_value:
            discount_pct = ((assessed_value - list_price) / assessed_value) * 100
            # Scale: 0% discount = 0 points, 25%+ discount = 40 points
            score += min(discount_pct * 1.6, 40)

        # 2. Days on market (30 points max)
        days_on_market = prop.get('days_on_market', 0)
        if days_on_market:
            # More days = better deal (property likely motivated)
            # Scale: 0 days = 0 points, 90+ days = 30 points
            score += min(days_on_market / 3, 30)

        # 3. Price per sqft vs market average (30 points max)
        sqft = prop.get('square_feet', 0) or prop.get('sqft', 0)
        if sqft and list_price and avg_price_per_sqft:
            prop_price_per_sqft = list_price / sqft
            if prop_price_per_sqft < avg_price_per_sqft:
                discount_pct = ((avg_price_per_sqft - prop_price_per_sqft) / avg_price_per_sqft) * 100
                # Scale: 0% below = 0 points, 25%+ below = 30 points
                score += min(discount_pct * 1.2, 30)

        return min(score, 100)

    def _calculate_avg_price_per_sqft(self, properties: List[Dict]) -> float:
        """Calculate average price per sqft across all properties"""
        price_per_sqft_values = []

        for prop in properties:
            sqft = prop.get('square_feet', 0) or prop.get('sqft', 0)
            price = prop.get('list_price', 0)

            if sqft and price and sqft > 0:
                price_per_sqft_values.append(price / sqft)

        if price_per_sqft_values:
            return statistics.median(price_per_sqft_values)

        return 0

    def _classify_deal(self, score: float) -> str:
        """
        Classify deal quality based on score

        Returns:
            'HOT', 'GOOD', 'FAIR', or 'PASS'
        """
        if score >= 90:
            return 'HOT'
        elif score >= 75:
            return 'GOOD'
        elif score >= 60:
            return 'FAIR'
        else:
            return 'PASS'

    def get_score_breakdown(self, prop: Dict, avg_price_per_sqft: float) -> Dict:
        """
        Get detailed score breakdown for a property

        Returns:
            Dictionary with score components
        """
        breakdown = {
            'price_below_market_points': 0,
            'days_on_market_points': 0,
            'price_per_sqft_points': 0,
            'total_score': 0
        }

        # Price below market
        list_price = prop.get('list_price', 0)
        assessed_value = (prop.get('tax_assessed_value', 0) or
                         prop.get('assessed_value', 0) or
                         prop.get('estimated_value', 0))

        if list_price and assessed_value and list_price < assessed_value:
            discount_pct = ((assessed_value - list_price) / assessed_value) * 100
            breakdown['price_below_market_points'] = min(discount_pct * 1.6, 40)
            breakdown['price_below_market_pct'] = discount_pct

        # Days on market
        days_on_market = prop.get('days_on_market', 0)
        if days_on_market:
            breakdown['days_on_market_points'] = min(days_on_market / 3, 30)
            breakdown['days_on_market'] = days_on_market

        # Price per sqft
        sqft = prop.get('square_feet', 0) or prop.get('sqft', 0)
        if sqft and list_price and avg_price_per_sqft:
            prop_price_per_sqft = list_price / sqft
            if prop_price_per_sqft < avg_price_per_sqft:
                discount_pct = ((avg_price_per_sqft - prop_price_per_sqft) / avg_price_per_sqft) * 100
                breakdown['price_per_sqft_points'] = min(discount_pct * 1.2, 30)
                breakdown['price_per_sqft_discount_pct'] = discount_pct

        breakdown['total_score'] = sum([
            breakdown['price_below_market_points'],
            breakdown['days_on_market_points'],
            breakdown['price_per_sqft_points']
        ])

        return breakdown
