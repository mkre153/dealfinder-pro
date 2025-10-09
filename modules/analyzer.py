from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import statistics

class PropertyAnalyzer:
    """Analyzes properties for investment opportunities"""

    def __init__(self, db_manager, config: Dict):
        self.db = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)

    def analyze_property(self, property_data: Dict) -> Dict:
        """
        Complete property analysis

        Args:
            property_data: Property dictionary with all fields

        Returns:
            Analysis dict with:
            - opportunity_score: 0-100
            - deal_quality: HOT DEAL | GOOD OPPORTUNITY | FAIR DEAL | PASS
            - score_breakdown: detailed component scores
            - below_market_percentage: how much below market
            - estimated_market_value: estimated true value
            - estimated_profit: potential profit
            - investment_metrics: cap_rate, cash_on_cash_return, etc.
            - recommendation: text summary
            - distressed_signals: list of motivation indicators
        """
        try:
            # Get market data for comparison
            market_data = self.get_market_data(
                zip_code=property_data.get('zip_code', ''),
                property_type=property_data.get('property_type', 'Single Family'),
                bedrooms=property_data.get('bedrooms', 3)
            )

            # Calculate investment metrics
            metrics = self.calculate_investment_metrics(property_data, market_data)

            # Import scorer for opportunity score calculation
            from modules.scorer import OpportunityScorer
            scorer = OpportunityScorer(self.config)

            # Calculate opportunity score
            score, deal_quality, breakdown = scorer.calculate_score(
                property_data,
                market_data,
                metrics
            )

            # Detect distressed signals
            signals = self.detect_distressed_signals(property_data)

            # Generate recommendation
            recommendation = self.generate_recommendation(
                property_data,
                score,
                deal_quality,
                breakdown,
                signals,
                metrics
            )

            return {
                'opportunity_score': score,
                'deal_quality': deal_quality,
                'score_breakdown': breakdown,
                'below_market_percentage': breakdown.get('price_advantage_pct', 0),
                'estimated_market_value': metrics['estimated_market_value'],
                'estimated_profit': metrics['estimated_profit'],
                'investment_metrics': metrics,
                'recommendation': recommendation,
                'distressed_signals': signals,
                'analysis_date': datetime.now().isoformat(),
                'market_data': market_data
            }
        except Exception as e:
            self.logger.error(f"Error analyzing property: {e}", exc_info=True)
            return self._default_analysis()

    def get_market_data(self, zip_code: str, property_type: str,
                        bedrooms: int) -> Dict:
        """
        Calculate market averages for comparison

        Args:
            zip_code: Property ZIP code
            property_type: Single Family, Condo, etc.
            bedrooms: Number of bedrooms

        Returns:
            Market data dict with:
            - avg_price_per_sqft: average $/sqft
            - median_price_per_sqft: median $/sqft
            - avg_days_on_market: average DOM
            - inventory_count: number of comparable properties
            - price_trend: "rising", "falling", or "stable"
        """
        try:
            # Query similar properties from last 90 days
            similar_properties = self.db.get_properties_by_criteria({
                'zip_code': zip_code,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'created_at_after': (datetime.now() - timedelta(days=90)).isoformat()
            })

            if not similar_properties or len(similar_properties) < 3:
                # Fallback to broader search (same ZIP, any type/beds)
                similar_properties = self.db.get_properties_by_criteria({
                    'zip_code': zip_code,
                    'created_at_after': (datetime.now() - timedelta(days=90)).isoformat()
                })

            if not similar_properties or len(similar_properties) < 3:
                # Final fallback to default values
                self.logger.warning(f"Insufficient market data for ZIP {zip_code}, using defaults")
                return self._default_market_data()

            # Calculate price per sqft for properties with valid data
            prices_per_sqft = []
            for p in similar_properties:
                sqft = p.get('square_feet', 0)
                price = p.get('list_price', 0)
                if sqft > 0 and price > 0:
                    prices_per_sqft.append(price / sqft)

            # Calculate days on market
            dom_values = [p.get('days_on_market', 0) for p in similar_properties
                         if p.get('days_on_market', 0) > 0]

            # Calculate trend
            price_trend = self.calculate_price_trend(similar_properties)

            return {
                'avg_price_per_sqft': statistics.mean(prices_per_sqft) if prices_per_sqft else 250,
                'median_price_per_sqft': statistics.median(prices_per_sqft) if prices_per_sqft else 250,
                'avg_days_on_market': statistics.mean(dom_values) if dom_values else 30,
                'inventory_count': len(similar_properties),
                'price_trend': price_trend
            }
        except Exception as e:
            self.logger.error(f"Error calculating market data: {e}", exc_info=True)
            return self._default_market_data()

    def calculate_price_trend(self, properties: List[Dict]) -> str:
        """
        Calculate if prices are rising, falling, or stable

        Args:
            properties: List of property dicts with created_at and list_price

        Returns:
            "rising", "falling", or "stable"
        """
        try:
            # Split properties into recent (last 30 days) vs older (30-90 days)
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)

            recent_prices = []
            older_prices = []

            for p in properties:
                created_at_str = p.get('created_at', '')
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    price = p.get('list_price', 0)
                    sqft = p.get('square_feet', 1)

                    if price > 0 and sqft > 0:
                        price_per_sqft = price / sqft

                        if created_at >= thirty_days_ago:
                            recent_prices.append(price_per_sqft)
                        else:
                            older_prices.append(price_per_sqft)
                except (ValueError, TypeError):
                    continue

            if not recent_prices or not older_prices:
                return "stable"

            avg_recent = statistics.mean(recent_prices)
            avg_older = statistics.mean(older_prices)

            # Calculate percentage change
            pct_change = ((avg_recent - avg_older) / avg_older) * 100

            if pct_change > 3:
                return "rising"
            elif pct_change < -3:
                return "falling"
            else:
                return "stable"
        except Exception as e:
            self.logger.error(f"Error calculating price trend: {e}")
            return "stable"

    def calculate_investment_metrics(self, property_data: Dict,
                                     market_data: Dict) -> Dict:
        """
        Calculate key investment metrics

        Args:
            property_data: Property details
            market_data: Market comparison data

        Returns:
            Investment metrics dict with:
            - estimated_market_value: ARV (after repair value)
            - estimated_profit: potential profit
            - rehab_estimate: estimated repair costs
            - cap_rate: for rental properties
            - cash_on_cash_return: annual cash return %
            - estimated_monthly_rent: projected rent
            - annual_noi: net operating income
            - gross_rent_multiplier: price / annual_rent
        """
        try:
            list_price = property_data.get('list_price', 0)
            sqft = property_data.get('square_feet', 1)

            if list_price <= 0 or sqft <= 0:
                return self._default_investment_metrics()

            # Estimate market value based on median price per sqft
            market_value = market_data['median_price_per_sqft'] * sqft

            # Estimate rehab costs based on property description
            rehab_estimate = self._estimate_rehab_costs(property_data, list_price)

            # Calculate profit potential (70% ARV rule for flips)
            max_purchase_price = market_value * 0.70 - rehab_estimate
            potential_profit = max_purchase_price - list_price

            # Estimate rental income (1% rule: monthly rent = 1% of property value)
            estimated_monthly_rent = market_value * 0.01
            annual_rental_income = estimated_monthly_rent * 12

            # Calculate annual expenses
            annual_taxes = property_data.get('annual_taxes', list_price * 0.012)
            annual_hoa = property_data.get('hoa_fee', 0) * 12
            annual_insurance = list_price * 0.004  # Estimate 0.4% of value
            annual_maintenance = annual_rental_income * 0.10  # 10% of rent
            annual_vacancy = annual_rental_income * 0.08  # 8% vacancy

            total_annual_expenses = (annual_taxes + annual_hoa + annual_insurance +
                                    annual_maintenance + annual_vacancy)

            # Net Operating Income
            noi = annual_rental_income - total_annual_expenses

            # Cap Rate
            cap_rate = (noi / list_price) * 100 if list_price > 0 else 0

            # Cash on Cash Return (assume 20% down payment)
            down_payment = list_price * 0.20
            annual_mortgage = self._calculate_annual_mortgage(list_price * 0.80, 0.07, 30)
            cash_flow = noi - annual_mortgage
            cash_on_cash = (cash_flow / down_payment) * 100 if down_payment > 0 else 0

            # Gross Rent Multiplier
            grm = list_price / annual_rental_income if annual_rental_income > 0 else 0

            return {
                'estimated_market_value': round(market_value, 2),
                'estimated_profit': round(potential_profit, 2),
                'rehab_estimate': round(rehab_estimate, 2),
                'cap_rate': round(cap_rate, 2),
                'estimated_monthly_rent': round(estimated_monthly_rent, 2),
                'annual_rental_income': round(annual_rental_income, 2),
                'annual_expenses': round(total_annual_expenses, 2),
                'annual_noi': round(noi, 2),
                'cash_on_cash_return': round(cash_on_cash, 2),
                'gross_rent_multiplier': round(grm, 2),
                'price_per_sqft': round(list_price / sqft, 2),
                'market_price_per_sqft': round(market_data['median_price_per_sqft'], 2)
            }
        except Exception as e:
            self.logger.error(f"Error calculating investment metrics: {e}", exc_info=True)
            return self._default_investment_metrics()

    def _estimate_rehab_costs(self, property_data: Dict, list_price: float) -> float:
        """Estimate rehab costs based on description keywords"""
        description = property_data.get('description', '').lower()

        # Heavy rehab indicators
        if any(kw in description for kw in ['fixer upper', 'gut rehab', 'needs work',
                                             'investor special', 'major repairs']):
            return list_price * 0.20  # 20% of purchase

        # Moderate rehab
        elif any(kw in description for kw in ['tlc', 'as-is', 'cosmetic updates',
                                               'potential', 'handyman']):
            return list_price * 0.10  # 10% of purchase

        # Light cosmetic
        else:
            return list_price * 0.05  # 5% for minor updates

    def _calculate_annual_mortgage(self, principal: float, rate: float, years: int) -> float:
        """Calculate annual mortgage payment"""
        monthly_rate = rate / 12
        num_payments = years * 12

        if monthly_rate == 0:
            monthly_payment = principal / num_payments
        else:
            monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                            ((1 + monthly_rate)**num_payments - 1)

        return monthly_payment * 12

    def detect_distressed_signals(self, property_data: Dict) -> List[str]:
        """
        Identify signals of motivated seller

        Returns list of signals found:
        - "Price reduced X times"
        - "Listed X days over market average"
        - "Keywords: motivated seller, as-is"
        - "Below tax assessment"
        """
        signals = []

        try:
            # Price reductions
            price_reduction = property_data.get('price_reduction_amount', 0)
            if price_reduction > 0:
                signals.append(f"Price reduced ${price_reduction:,.0f}")

            # High days on market
            dom = property_data.get('days_on_market', 0)
            if dom > 90:
                signals.append(f"Listed {dom} days (highly motivated)")
            elif dom > 60:
                signals.append(f"Listed {dom} days (motivated seller)")

            # Distressed keywords
            description = property_data.get('description', '').lower()
            distressed_keywords = self.config.get('undervalued_criteria', {}).get(
                'distressed_keywords',
                ['motivated', 'as-is', 'fixer', 'needs work', 'estate sale',
                 'must sell', 'tlc', 'handyman', 'cash only']
            )

            found_keywords = [kw for kw in distressed_keywords if kw in description]
            if found_keywords:
                signals.append(f"Keywords: {', '.join(found_keywords[:3])}")

            # Below tax assessment
            tax_value = property_data.get('tax_assessed_value', 0)
            list_price = property_data.get('list_price', 0)

            if tax_value > 0 and list_price > 0:
                if list_price < tax_value * 0.85:
                    pct = ((tax_value - list_price) / tax_value * 100)
                    signals.append(f"Listed {pct:.1f}% below tax assessment")

        except Exception as e:
            self.logger.error(f"Error detecting distressed signals: {e}")

        return signals

    def generate_recommendation(self, property_data: Dict, score: int,
                               deal_quality: str, breakdown: Dict,
                               signals: List[str], metrics: Dict) -> str:
        """
        Generate human-readable recommendation text

        Args:
            property_data: Property details
            score: Opportunity score (0-100)
            deal_quality: Classification string
            breakdown: Score components
            signals: Distressed signals
            metrics: Investment metrics

        Returns:
            Recommendation text
        """
        try:
            address = f"{property_data.get('street_address', 'Property')}"
            price = property_data.get('list_price', 0)

            # Start with deal quality assessment
            if deal_quality == "HOT DEAL":
                rec = f"IMMEDIATE ACTION: {address} is an exceptional opportunity (Score: {score}/100). "
            elif deal_quality == "GOOD OPPORTUNITY":
                rec = f"STRONG BUY: {address} presents a solid investment (Score: {score}/100). "
            elif deal_quality == "FAIR DEAL":
                rec = f"CONSIDER: {address} is worth evaluating (Score: {score}/100). "
            else:
                rec = f"PASS: {address} does not meet investment criteria (Score: {score}/100). "

            # Add price advantage
            price_adv = breakdown.get('price_advantage_pct', 0)
            if price_adv > 0:
                rec += f"Listed {price_adv:.1f}% below market average. "

            # Add profit potential
            profit = metrics.get('estimated_profit', 0)
            if profit > 0:
                rec += f"Estimated profit potential: ${profit:,.0f}. "

            # Add rental metrics
            cap_rate = metrics.get('cap_rate', 0)
            if cap_rate > 0:
                rec += f"Cap rate: {cap_rate:.1f}%. "

            # Add distressed signals
            if signals:
                rec += f"Motivation signals: {'; '.join(signals[:2])}. "

            # Add action items
            if score >= 75:
                rec += "Recommend immediate property tour and offer preparation."
            elif score >= 60:
                rec += "Schedule showing to verify condition and neighborhood."

            return rec
        except Exception as e:
            self.logger.error(f"Error generating recommendation: {e}")
            return "Analysis completed. Review metrics for investment decision."

    def _default_analysis(self) -> Dict:
        """Return default analysis for error cases"""
        return {
            'opportunity_score': 0,
            'deal_quality': 'PASS',
            'score_breakdown': {},
            'below_market_percentage': 0,
            'estimated_market_value': 0,
            'estimated_profit': 0,
            'investment_metrics': self._default_investment_metrics(),
            'recommendation': 'Unable to analyze property due to insufficient data.',
            'distressed_signals': [],
            'analysis_date': datetime.now().isoformat()
        }

    def _default_market_data(self) -> Dict:
        """Return default market data"""
        return {
            'avg_price_per_sqft': 250,
            'median_price_per_sqft': 250,
            'avg_days_on_market': 30,
            'inventory_count': 0,
            'price_trend': 'stable'
        }

    def _default_investment_metrics(self) -> Dict:
        """Return default investment metrics"""
        return {
            'estimated_market_value': 0,
            'estimated_profit': 0,
            'rehab_estimate': 0,
            'cap_rate': 0,
            'estimated_monthly_rent': 0,
            'annual_rental_income': 0,
            'annual_expenses': 0,
            'annual_noi': 0,
            'cash_on_cash_return': 0,
            'gross_rent_multiplier': 0,
            'price_per_sqft': 0,
            'market_price_per_sqft': 0
        }
