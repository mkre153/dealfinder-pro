"""
Perplexity AI Integration for Real-Time Web Search
Provides real-time market intelligence, neighborhood data, and trend analysis
"""

import os
import json
import requests
from typing import Dict, List, Optional, Literal
from datetime import datetime


class PerplexityAgent:
    """
    Perplexity AI agent for real-time web search capabilities

    Use Cases:
    - Real-time market news and trends
    - Neighborhood intelligence (schools, crime, demographics)
    - Recent comparable sales beyond database
    - Economic indicators and regulations
    - Development projects and zoning changes
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity agent

        Args:
            api_key: Perplexity API key (or use PERPLEXITY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai"

        # Model selection
        self.models = {
            "quick": "llama-3.1-sonar-small-128k-online",  # Fast, cost-effective
            "deep": "llama-3.1-sonar-large-128k-online",   # Comprehensive analysis
            "huge": "llama-3.1-sonar-huge-128k-online"     # Maximum depth
        }

        # Default model for different query types
        self.default_models = {
            "news": "quick",
            "statistics": "deep",
            "neighborhood": "deep",
            "comparables": "quick",
            "regulations": "deep",
            "general": "quick"
        }

    def search(
        self,
        query: str,
        search_domain: Literal["news", "statistics", "neighborhood", "comparables", "regulations", "general"] = "general",
        depth: Literal["quick", "deep", "huge"] = None,
        include_citations: bool = True
    ) -> Dict:
        """
        Search the web using Perplexity AI

        Args:
            query: Natural language search query
            search_domain: Type of search (determines model selection and prompting)
            depth: Search depth override (quick/deep/huge)
            include_citations: Include source citations in response

        Returns:
            Dict with 'answer', 'citations', 'model_used', 'tokens_used'
        """
        if not self.api_key:
            return {
                "answer": "⚠️ Perplexity API key not configured. Add PERPLEXITY_API_KEY to .env file.",
                "citations": [],
                "model_used": None,
                "tokens_used": 0,
                "error": "API_KEY_MISSING"
            }

        # Select model based on search domain and depth
        model_depth = depth or self.default_models.get(search_domain, "quick")
        model = self.models[model_depth]

        # Build system prompt based on search domain
        system_prompt = self._build_system_prompt(search_domain)

        # Make API request
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.2,  # Lower for factual accuracy
                    "return_citations": include_citations,
                    "return_images": False
                },
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extract answer and citations
            answer = data['choices'][0]['message']['content']
            citations = data.get('citations', [])

            return {
                "answer": answer,
                "citations": citations,
                "model_used": model,
                "tokens_used": data.get('usage', {}).get('total_tokens', 0),
                "timestamp": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                "answer": f"Error querying Perplexity: {str(e)}",
                "citations": [],
                "model_used": model,
                "tokens_used": 0,
                "error": str(e)
            }

    def _build_system_prompt(self, search_domain: str) -> str:
        """Build specialized system prompt based on search domain"""

        base_prompt = "You are a real estate market intelligence assistant. Provide accurate, well-cited information."

        domain_prompts = {
            "news": (
                f"{base_prompt} Focus on recent news, market trends, and developments. "
                "Include dates and sources. Prioritize information from the last 30 days."
            ),
            "statistics": (
                f"{base_prompt} Focus on numerical data, statistics, and market metrics. "
                "Provide median prices, average days on market, inventory levels, and trends. "
                "Include time ranges and data sources."
            ),
            "neighborhood": (
                f"{base_prompt} Focus on neighborhood characteristics: schools, crime rates, "
                "demographics, amenities, walkability, development projects, and quality of life. "
                "Provide balanced information with sources."
            ),
            "comparables": (
                f"{base_prompt} Focus on recent comparable sales. Provide addresses, sale prices, "
                "dates, property characteristics, and price per square foot. "
                "Prioritize sales from the last 6 months."
            ),
            "regulations": (
                f"{base_prompt} Focus on regulations, zoning, permits, HOA rules, rent control, "
                "tax policies, and legal considerations. Cite official sources."
            ),
            "general": base_prompt
        }

        return domain_prompts.get(search_domain, base_prompt)

    # Pre-built search methods for common use cases

    def get_market_news(self, location: str, days: int = 30) -> Dict:
        """Get recent real estate market news for a location"""
        query = f"What are the latest real estate market trends and news in {location} from the last {days} days? Include price movements, inventory changes, and notable developments."
        return self.search(query, search_domain="news", depth="quick")

    def get_neighborhood_intelligence(self, neighborhood: str, city: str, state: str) -> Dict:
        """Get comprehensive neighborhood analysis"""
        query = f"""Analyze {neighborhood} in {city}, {state} for real estate investment:
        1. School ratings and quality
        2. Crime statistics and safety
        3. Demographics and income levels
        4. Walkability and transit access
        5. Amenities (parks, shopping, restaurants)
        6. Recent or planned development projects
        7. Overall neighborhood trajectory (improving/declining)

        Provide data-driven insights with sources."""

        return self.search(query, search_domain="neighborhood", depth="deep")

    def get_comparable_sales(self, address: str, city: str, state: str, property_type: str) -> Dict:
        """Find recent comparable sales"""
        query = f"""Find recent comparable sales near {address}, {city}, {state}:
        - Property type: {property_type}
        - Sales from last 6 months
        - Within 0.5 mile radius

        For each comparable, provide:
        - Address
        - Sale price and date
        - Bedrooms/bathrooms
        - Square footage
        - Price per sqft

        List 5-10 most relevant comparables."""

        return self.search(query, search_domain="comparables", depth="quick")

    def get_market_statistics(self, city: str, state: str, property_type: str = "single-family") -> Dict:
        """Get current market statistics"""
        query = f"""What are the current real estate market statistics for {property_type} homes in {city}, {state}?

        Include:
        - Median sale price (current and 12-month trend)
        - Average days on market
        - Inventory levels (months of supply)
        - Price per square foot
        - Year-over-year price change %
        - Buyer vs seller market indicator

        Provide recent data (last 30-60 days) with sources."""

        return self.search(query, search_domain="statistics", depth="deep")

    def get_investment_forecast(self, location: str) -> Dict:
        """Get investment outlook and predictions"""
        query = f"""What is the real estate investment outlook for {location}?

        Analyze:
        1. Price appreciation forecast (next 1-3 years)
        2. Rental market demand and trends
        3. Economic factors (job growth, population trends)
        4. Major employers and industries
        5. Infrastructure projects
        6. Risks and opportunities

        Provide expert perspectives and data sources."""

        return self.search(query, search_domain="news", depth="deep")

    def check_regulations(self, city: str, state: str, query_type: str = "rental") -> Dict:
        """Check regulations affecting real estate investment"""

        regulation_queries = {
            "rental": f"What are the current rental regulations, rent control policies, and landlord-tenant laws in {city}, {state}?",
            "zoning": f"What are the zoning regulations and ADU (accessory dwelling unit) rules in {city}, {state}?",
            "tax": f"What are the property tax rates, assessment practices, and tax incentives in {city}, {state}?",
            "short_term": f"What are the short-term rental (Airbnb/VRBO) regulations and restrictions in {city}, {state}?"
        }

        query = regulation_queries.get(query_type, f"What are the real estate investment regulations in {city}, {state}?")
        return self.search(query, search_domain="regulations", depth="deep")

    def format_response_for_chat(self, search_result: Dict) -> str:
        """Format Perplexity search result for chat display"""

        if search_result.get('error'):
            return search_result['answer']

        answer = search_result['answer']
        citations = search_result.get('citations', [])

        # Build formatted response
        formatted = f"{answer}\n\n"

        # Add citations if available
        if citations:
            formatted += "**Sources:**\n"
            for i, citation in enumerate(citations[:5], 1):  # Limit to top 5 sources
                formatted += f"{i}. {citation}\n"

        return formatted


# Standalone testing
if __name__ == "__main__":
    """Test Perplexity integration"""

    print("🔍 Perplexity AI Integration Test\n")

    agent = PerplexityAgent()

    # Test 1: Market news
    print("Test 1: Market News for San Diego")
    print("-" * 50)
    result = agent.get_market_news("San Diego, CA", days=30)
    print(agent.format_response_for_chat(result))
    print("\n")

    # Test 2: Neighborhood intelligence
    print("Test 2: Neighborhood Analysis - La Jolla")
    print("-" * 50)
    result = agent.get_neighborhood_intelligence("La Jolla", "San Diego", "CA")
    print(agent.format_response_for_chat(result))
    print("\n")

    # Test 3: Market statistics
    print("Test 3: Market Statistics - Las Vegas")
    print("-" * 50)
    result = agent.get_market_statistics("Las Vegas", "NV", property_type="single-family")
    print(agent.format_response_for_chat(result))
