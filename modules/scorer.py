from typing import Dict, Tuple
import logging

class OpportunityScorer:
    """Calculates opportunity scores based on multiple factors"""

    def __init__(self, config: Dict):
        self.config = config
        self.weights = config.get('scoring_weights', {
            'price_advantage': 30,
            'days_on_market': 20,
            'financial_returns': 25,
            'condition_price': 15,
            'location_quality': 10
        })
        self.logger = logging.getLogger(__name__)

    def calculate_score(self, property_data: Dict, market_data: Dict,
                       investment_metrics: Dict) -> Tuple[int, str, Dict]:
        """
        Calculate 0-100 opportunity score

        Scoring factors (configurable weights):
        1. Price Advantage (30 points default) - How much below market
        2. Days on Market (20 points default) - Seller motivation
        3. Financial Returns (25 points default) - Cap rate, profit potential
        4. Condition/Price Indicators (15 points default) - Distressed signals
        5. Location Quality (10 points default) - Area desirability

        Args:
            property_data: Property details
            market_data: Market comparison data
            investment_metrics: Calculated investment metrics

        Returns:
            Tuple of (total_score, deal_quality, breakdown_dict)
            - total_score: 0-100 integer
            - deal_quality: "HOT DEAL" | "GOOD OPPORTUNITY" | "FAIR DEAL" | "PASS"
            - breakdown_dict: Component scores and details
        """
        try:
            # Factor 1: Price Advantage (30 points max)
            price_score, price_pct = self._calculate_price_score(
                property_data, market_data
            )

            # Factor 2: Days on Market (20 points max)
            dom_score = self._calculate_dom_score(property_data, market_data)

            # Factor 3: Financial Returns (25 points max)
            financial_score = self._calculate_financial_score(
                property_data, investment_metrics
            )

            # Factor 4: Condition/Price Indicators (15 points max)
            condition_score = self._calculate_condition_score(property_data)

            # Factor 5: Location Quality (10 points max)
            location_score = self._calculate_location_score(property_data)

            # Apply weights and calculate total
            # Normalize each component to its max possible points, then apply weight
            total_score = int(round(
                (price_score / 30) * self.weights['price_advantage'] +
                (dom_score / 20) * self.weights['days_on_market'] +
                (financial_score / 25) * self.weights['financial_returns'] +
                (condition_score / 15) * self.weights['condition_price'] +
                (location_score / 10) * self.weights['location_quality']
            ))

            # Ensure score is within bounds
            total_score = max(0, min(100, total_score))

            # Classify deal quality based on thresholds
            if total_score >= 90:
                deal_quality = "HOT DEAL"
            elif total_score >= 75:
                deal_quality = "GOOD OPPORTUNITY"
            elif total_score >= 60:
                deal_quality = "FAIR DEAL"
            else:
                deal_quality = "PASS"

            breakdown = {
                'price_score': price_score,
                'price_advantage_pct': price_pct,
                'dom_score': dom_score,
                'financial_score': financial_score,
                'condition_score': condition_score,
                'location_score': location_score,
                'total_score': total_score,
                'deal_quality': deal_quality
            }

            self.logger.info(f"Scored property: {total_score}/100 ({deal_quality})")
            return total_score, deal_quality, breakdown

        except Exception as e:
            self.logger.error(f"Error calculating score: {e}", exc_info=True)
            return 0, "PASS", {}

    def _calculate_price_score(self, property_data: Dict,
                               market_data: Dict) -> Tuple[int, float]:
        """
        Price per sqft vs market average (30 points max)

        Scoring:
        - 20%+ below market = 30 points
        - 15-20% below = 25 points
        - 10-15% below = 20 points
        - 5-10% below = 10 points
        - <5% below = 0 points

        Returns:
            Tuple of (score, advantage_percentage)
        """
        try:
            sqft = property_data.get('square_feet', 0)
            list_price = property_data.get('list_price', 0)

            if sqft <= 0 or list_price <= 0:
                return 0, 0.0

            price_per_sqft = list_price / sqft
            market_avg = market_data.get('median_price_per_sqft', 250)

            # Calculate percentage below market
            advantage_pct = ((market_avg - price_per_sqft) / market_avg) * 100

            # Score based on advantage
            if advantage_pct >= 20:
                return 30, advantage_pct
            elif advantage_pct >= 15:
                return 25, advantage_pct
            elif advantage_pct >= 10:
                return 20, advantage_pct
            elif advantage_pct >= 5:
                return 10, advantage_pct
            else:
                return 0, advantage_pct

        except Exception as e:
            self.logger.error(f"Error calculating price score: {e}")
            return 0, 0.0

    def _calculate_dom_score(self, property_data: Dict,
                            market_data: Dict) -> int:
        """
        Days on market score (20 points max)

        Longer DOM = more motivated seller

        Scoring:
        - 90+ days = 20 points
        - 60-89 days = 15 points
        - 30-59 days = 10 points
        - <30 days = 5 points

        Args:
            property_data: Property details
            market_data: Market comparison data

        Returns:
            Score (0-20)
        """
        try:
            dom = property_data.get('days_on_market', 0)

            if dom >= 90:
                return 20
            elif dom >= 60:
                return 15
            elif dom >= 30:
                return 10
            else:
                return 5

        except Exception as e:
            self.logger.error(f"Error calculating DOM score: {e}")
            return 5

    def _calculate_financial_score(self, property_data: Dict,
                                   metrics: Dict) -> int:
        """
        Investment returns score (25 points max)

        Evaluates both rental potential and flip profit

        Scoring (rental):
        - Cap rate >= 10% = 25 points
        - Cap rate >= 8% = 20 points
        - Cap rate >= 6% = 15 points
        - Cap rate >= 4% = 10 points
        - Cap rate < 4% = 5 points

        Scoring (flip):
        - Profit >= 25% = 25 points
        - Profit >= 20% = 20 points
        - Profit >= 15% = 15 points
        - Profit >= 10% = 10 points
        - Profit < 10% = 5 points

        Uses whichever metric scores higher

        Args:
            property_data: Property details
            metrics: Investment metrics dict

        Returns:
            Score (0-25)
        """
        try:
            # Rental scoring (cap rate)
            cap_rate = metrics.get('cap_rate', 0)

            if cap_rate >= 10:
                rental_score = 25
            elif cap_rate >= 8:
                rental_score = 20
            elif cap_rate >= 6:
                rental_score = 15
            elif cap_rate >= 4:
                rental_score = 10
            else:
                rental_score = 5

            # Flip scoring (profit percentage)
            list_price = property_data.get('list_price', 1)
            profit = metrics.get('estimated_profit', 0)

            profit_pct = (profit / list_price * 100) if list_price > 0 else 0

            if profit_pct >= 25:
                flip_score = 25
            elif profit_pct >= 20:
                flip_score = 20
            elif profit_pct >= 15:
                flip_score = 15
            elif profit_pct >= 10:
                flip_score = 10
            else:
                flip_score = 5

            # Return whichever strategy scores higher
            return max(rental_score, flip_score)

        except Exception as e:
            self.logger.error(f"Error calculating financial score: {e}")
            return 10

    def _calculate_condition_score(self, property_data: Dict) -> int:
        """
        Distressed indicators score (15 points max)

        Looks for signs of motivated seller:
        - Price reductions
        - Distressed keywords
        - Below tax assessment

        Scoring:
        - Price reduction >= $20k = 5 points
        - Price reduction >= $10k = 3 points
        - 3+ distressed keywords = 10 points
        - 1-2 distressed keywords = 5 points
        - Below tax assessment = bonus points

        Args:
            property_data: Property details

        Returns:
            Score (0-15)
        """
        try:
            score = 0

            # Price reductions
            price_reduction = property_data.get('price_reduction_amount', 0)
            if price_reduction >= 20000:
                score += 5
            elif price_reduction >= 10000:
                score += 3

            # Distressed keywords
            description = property_data.get('description', '').lower()
            distressed_keywords = [
                'motivated', 'as-is', 'fixer', 'needs work',
                'estate sale', 'must sell', 'tlc', 'handyman',
                'cash only', 'investor special', 'potential',
                'bring offers'
            ]

            keyword_count = sum(1 for kw in distressed_keywords if kw in description)

            if keyword_count >= 3:
                score += 10
            elif keyword_count >= 1:
                score += 5

            # Ensure score doesn't exceed maximum
            return min(score, 15)

        except Exception as e:
            self.logger.error(f"Error calculating condition score: {e}")
            return 0

    def _calculate_location_score(self, property_data: Dict) -> int:
        """
        Location quality score (10 points max)

        Currently uses basic heuristics. In future could integrate:
        - School ratings (GreatSchools API)
        - Crime statistics
        - Appreciation trends
        - Walkability scores
        - Nearby amenities

        Current scoring:
        - Default neutral score = 5 points
        - High-value ZIP codes = +3 points
        - Low-value ZIP codes = -2 points

        Args:
            property_data: Property details

        Returns:
            Score (0-10)
        """
        try:
            score = 5  # Default neutral score

            # Could add premium ZIP code detection
            # For now, maintain neutral score
            # Future enhancement: integrate with external APIs

            return score

        except Exception as e:
            self.logger.error(f"Error calculating location score: {e}")
            return 5
