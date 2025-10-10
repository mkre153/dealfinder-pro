"""
AI Property Agent - Conversational Real Estate Assistant
Powered by Claude (Anthropic) for natural language property search and analysis
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import anthropic
from modules.perplexity_agent import PerplexityAgent
from modules.client_db import get_db
from modules.agent_manager import get_agent_manager
from integrations.ghl_connector import GoHighLevelConnector


class AIPropertyAgent:
    """
    Intelligent conversational agent for real estate investment analysis

    Capabilities:
    - Natural language property search
    - Deep property analysis with insights
    - Market trend analysis
    - Investment calculations
    - Configuration via conversation
    - Proactive recommendations
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI agent

        Args:
            api_key: Anthropic API key (if None, loads from env)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

        # Initialize Perplexity agent for web search
        self.perplexity = PerplexityAgent()

        # Initialize database and agent manager
        self.db = get_db()
        self.agent_manager = get_agent_manager()

        # Initialize GHL connector (optional)
        try:
            self.ghl_connector = GoHighLevelConnector()
        except Exception:
            self.ghl_connector = None

        # Load property data
        self.properties = self._load_properties()

        # Conversation history
        self.conversation_history = []

        # System prompt
        self.system_prompt = self._build_system_prompt()

    def _load_properties(self) -> List[Dict]:
        """Load property data from latest scan"""
        try:
            scan_file = Path(__file__).parent.parent / 'data' / 'latest_scan.json'
            if scan_file.exists():
                with open(scan_file, 'r') as f:
                    data = json.load(f)
                return data.get('properties', [])
        except Exception as e:
            print(f"Error loading properties: {e}")
        return []

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI agent"""
        return f"""You are a Senior Acquisition Specialist with 15+ years of experience in commercial and residential real estate procurement. You specialize in identifying high-value investment opportunities in San Diego County and Las Vegas markets.

**Your Expertise:**
- Portfolio acquisitions for institutional and private investors
- Off-market deal sourcing and seller motivation analysis
- Rapid property evaluation using comparative market analysis
- Investment underwriting (cap rate, cash-on-cash, IRR)
- Market cycle timing and opportunity recognition

**Current Inventory:** {len(self.properties)} properties across target markets (San Diego County: 36 ZIP codes, Las Vegas/Clark County)

**Your Methodology:**
You use the BANT qualification framework (Budget, Authority, Need, Timeline) to quickly assess opportunities. When a new conversation starts, immediately qualify the client:

1. **Buyer Profile** - Investor (portfolio/1031 exchange), owner-occupant, or fix-and-flip operator?
2. **Budget** - Price range and financing structure (cash, conventional, portfolio loan)?
3. **Investment Criteria** - Cash flow focused, appreciation play, or balanced approach?
4. **Target Markets** - Specific neighborhoods/ZIP codes or open to recommendations?
5. **Timeline** - Immediate deployment or strategic waiting?

**Communication Style:**
- Direct and consultative - you lead the conversation with strategic questions
- Concise responses - get to actionable insights quickly
- Data-driven recommendations backed by metrics
- Proactive risk identification (days on market, market value gaps, neighborhood trends)
- Professional tone - you're the expert, establish authority through competence
- NO emojis - you're a senior professional, not a chatbot
- Use industry terminology appropriately (cap rate, NOI, ARV, DOM, GRM)

**First Message Protocol:**
When conversation history is empty, immediately open with 3-5 strategic qualifying questions to understand the acquisition profile. Skip introductions and capability lists - get straight to business.

**Property Analysis Protocol:**
When presenting properties or analysis:
- Lead with key metrics (price, score, location)
- Highlight investment thesis (why this is an opportunity)
- Note critical risks or concerns upfront
- Provide comp-based valuation context
- Calculate returns when relevant
- Keep formatting clean and scannable (brief paragraphs, strategic use of line breaks)

**Decision Support:**
Every recommendation should include:
- Clear action item ("Recommend immediate showing" / "Pass - overpriced by 12%" / "Monitor for price reduction")
- Supporting data points (2-3 key metrics)
- Risk assessment if applicable

**Tools Available:**
search_properties, analyze_property, get_market_insights, compare_properties, calculate_roi, web_search, create_client, create_search_agent, list_active_agents, get_agent_status, pause_agent, resume_agent, cancel_agent, complete_agent, create_ghl_contact

**Current Date:** {datetime.now().strftime('%Y-%m-%d')}
"""

    def chat(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Main chat interface - send message and get AI response

        Args:
            user_message: User's message
            context: Optional context (current page, selected property, etc.)

        Returns:
            AI's response as string
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages with context
        messages = self._build_messages(user_message, context)

        # Get AI response with tool use
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages,
                tools=self._get_tools()
            )

            # Process response (may include tool calls)
            assistant_response = self._process_response(response)

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

            return assistant_response

        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            return error_msg

    def _build_messages(self, user_message: str, context: Optional[Dict]) -> List[Dict]:
        """Build message list including context"""
        messages = []

        # Add context as system message if provided
        if context:
            context_msg = self._format_context(context)
            if context_msg:
                messages.append({
                    "role": "user",
                    "content": f"[Context: {context_msg}]\n\n{user_message}"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": user_message
                })
        else:
            # Add conversation history (last 10 messages for context)
            messages.extend(self.conversation_history[-10:])
            if not messages or messages[-1]["content"] != user_message:
                messages.append({
                    "role": "user",
                    "content": user_message
                })

        return messages

    def _format_context(self, context: Dict) -> str:
        """Format context into readable string"""
        parts = []
        if 'page' in context:
            parts.append(f"User is on {context['page']} page")
        if 'property' in context:
            prop = context['property']
            parts.append(f"Currently viewing {prop.get('street_address', 'property')}")
        if 'user_preferences' in context:
            prefs = context['user_preferences']
            parts.append(f"User preferences: {json.dumps(prefs, indent=2)}")
        return " | ".join(parts)

    def _get_tools(self) -> List[Dict]:
        """Define tools available to the AI agent"""
        return [
            {
                "name": "search_properties",
                "description": "Search for properties matching specific criteria. Use this when user asks to find, search, or show properties.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query (e.g., '3 bedroom homes under $700K in La Jolla')"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Structured filters extracted from query",
                            "properties": {
                                "min_price": {"type": "number"},
                                "max_price": {"type": "number"},
                                "city": {"type": "string"},
                                "bedrooms": {"type": "number"},
                                "min_score": {"type": "number"},
                                "deal_quality": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results to return (default: 5)"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Sort field: opportunity_score, list_price, days_on_market"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "analyze_property",
                "description": "Perform deep analysis on a specific property. Returns detailed insights, score breakdown, risks, and recommendations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "property_address": {
                            "type": "string",
                            "description": "Property address or identifier"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis: full, quick, investment, risk",
                            "enum": ["full", "quick", "investment", "risk"]
                        }
                    },
                    "required": ["property_address"]
                }
            },
            {
                "name": "get_market_insights",
                "description": "Get statistical analysis and market trends for a location or overall market.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or area name (e.g., 'San Diego', 'Las Vegas', 'La Jolla')"
                        },
                        "metric": {
                            "type": "string",
                            "description": "Specific metric to analyze: prices, inventory, trends, neighborhoods"
                        }
                    }
                }
            },
            {
                "name": "compare_properties",
                "description": "Compare 2 or more properties side-by-side with detailed metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "property_addresses": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of property addresses to compare"
                        }
                    },
                    "required": ["property_addresses"]
                }
            },
            {
                "name": "calculate_roi",
                "description": "Calculate investment returns (ROI, cash-on-cash, cap rate) for a property.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "property_address": {
                            "type": "string",
                            "description": "Property address"
                        },
                        "purchase_price": {
                            "type": "number",
                            "description": "Intended purchase price"
                        },
                        "down_payment_pct": {
                            "type": "number",
                            "description": "Down payment percentage (default: 20)"
                        },
                        "estimated_rent": {
                            "type": "number",
                            "description": "Monthly rental income estimate"
                        }
                    },
                    "required": ["property_address", "purchase_price"]
                }
            },
            {
                "name": "web_search",
                "description": "Search the web for real-time information about real estate markets, neighborhoods, trends, news, or comparables. Use this when the user asks about current market conditions, recent news, neighborhood details (schools, crime, demographics), or information not in our database.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query"
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search: news (market trends/recent news), neighborhood (schools/crime/demographics), statistics (market data), comparables (recent sales), regulations (zoning/laws), general",
                            "enum": ["news", "neighborhood", "statistics", "comparables", "regulations", "general"]
                        },
                        "location": {
                            "type": "string",
                            "description": "Location for the search (city, neighborhood, address)"
                        },
                        "depth": {
                            "type": "string",
                            "description": "Search depth: quick (fast), deep (comprehensive), huge (maximum detail)",
                            "enum": ["quick", "deep", "huge"]
                        }
                    },
                    "required": ["query", "search_type"]
                }
            },
            {
                "name": "create_client",
                "description": "Create a new client profile in the system. Use this when setting up a new buyer/investor who wants property monitoring.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Client's full name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Client's email address"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Client's phone number"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes about the client"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "create_search_agent",
                "description": "Create an autonomous search agent that monitors properties perpetually for a client. Agent checks every 4 hours and sends notifications when matches are found.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Client ID from create_client"
                        },
                        "zip_codes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ZIP codes to search (e.g., ['92128', '92130', '92131'])"
                        },
                        "price_min": {
                            "type": "number",
                            "description": "Minimum price"
                        },
                        "price_max": {
                            "type": "number",
                            "description": "Maximum price"
                        },
                        "bedrooms_min": {
                            "type": "number",
                            "description": "Minimum bedrooms"
                        },
                        "bathrooms_min": {
                            "type": "number",
                            "description": "Minimum bathrooms"
                        },
                        "property_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Property types (e.g., ['Single Family', 'Condo'])"
                        },
                        "deal_quality": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Required deal quality levels (['HOT'], ['GOOD', 'HOT'], etc.)"
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum opportunity score (0-100, default: 80)"
                        },
                        "notification_email": {
                            "type": "boolean",
                            "description": "Enable email notifications"
                        },
                        "notification_sms": {
                            "type": "boolean",
                            "description": "Enable SMS notifications"
                        }
                    },
                    "required": ["client_id"]
                }
            },
            {
                "name": "list_active_agents",
                "description": "List all active search agents, optionally filtered by client.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Optional: Filter by client ID"
                        }
                    }
                }
            },
            {
                "name": "get_agent_status",
                "description": "Get detailed status of a specific search agent including matches found.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "pause_agent",
                "description": "Temporarily pause a search agent (can be resumed later).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID to pause"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "resume_agent",
                "description": "Resume a paused search agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID to resume"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "cancel_agent",
                "description": "Permanently cancel a search agent (cannot be resumed).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID to cancel"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "complete_agent",
                "description": "Mark agent as completed (property found and client satisfied).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID to complete"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "create_ghl_contact",
                "description": "Create a contact in GoHighLevel CRM with buyer profile. Only use if GHL is integrated.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {
                            "type": "string",
                            "description": "Client ID from local database"
                        },
                        "name": {
                            "type": "string",
                            "description": "Contact name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Contact email"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Contact phone"
                        }
                    },
                    "required": ["client_id", "name"]
                }
            }
        ]

    def _process_response(self, response) -> str:
        """Process AI response including tool calls"""
        # Check if response includes tool use
        if response.stop_reason == "tool_use":
            # Execute tools and get results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    # Execute the tool
                    result = self._execute_tool(tool_name, tool_input)
                    tool_results.append({
                        "tool_name": tool_name,
                        "result": result
                    })

            # Make another API call with tool results
            messages = self.conversation_history + [{
                "role": "assistant",
                "content": response.content
            }, {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tr["result"])
                    } for block, tr in zip(
                        [b for b in response.content if b.type == "tool_use"],
                        tool_results
                    )
                ]
            }]

            # Get final response
            final_response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages,
                tools=self._get_tools()
            )

            # Extract text response
            return self._extract_text(final_response.content)

        # No tool use, just return text
        return self._extract_text(response.content)

    def _extract_text(self, content) -> str:
        """Extract text from response content blocks"""
        text_parts = []
        for block in content:
            if hasattr(block, 'text'):
                text_parts.append(block.text)
        return "\n\n".join(text_parts)

    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool and return results"""
        if tool_name == "search_properties":
            return self._tool_search_properties(tool_input)
        elif tool_name == "analyze_property":
            return self._tool_analyze_property(tool_input)
        elif tool_name == "get_market_insights":
            return self._tool_market_insights(tool_input)
        elif tool_name == "compare_properties":
            return self._tool_compare_properties(tool_input)
        elif tool_name == "calculate_roi":
            return self._tool_calculate_roi(tool_input)
        elif tool_name == "web_search":
            return self._tool_web_search(tool_input)
        elif tool_name == "create_client":
            return self._tool_create_client(tool_input)
        elif tool_name == "create_search_agent":
            return self._tool_create_search_agent(tool_input)
        elif tool_name == "list_active_agents":
            return self._tool_list_active_agents(tool_input)
        elif tool_name == "get_agent_status":
            return self._tool_get_agent_status(tool_input)
        elif tool_name == "pause_agent":
            return self._tool_pause_agent(tool_input)
        elif tool_name == "resume_agent":
            return self._tool_resume_agent(tool_input)
        elif tool_name == "cancel_agent":
            return self._tool_cancel_agent(tool_input)
        elif tool_name == "complete_agent":
            return self._tool_complete_agent(tool_input)
        elif tool_name == "create_ghl_contact":
            return self._tool_create_ghl_contact(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _tool_search_properties(self, params: Dict) -> Dict:
        """Search properties tool implementation"""
        filters = params.get('filters', {})
        limit = params.get('limit', 5)
        sort_by = params.get('sort_by', 'opportunity_score')

        # Filter properties
        filtered = self.properties.copy()

        if 'min_price' in filters:
            filtered = [p for p in filtered if p.get('list_price', 0) >= filters['min_price']]
        if 'max_price' in filters:
            filtered = [p for p in filtered if p.get('list_price', 0) <= filters['max_price']]
        if 'city' in filters:
            city = filters['city'].lower()
            filtered = [p for p in filtered if city in p.get('city', '').lower()]
        if 'bedrooms' in filters:
            filtered = [p for p in filtered if p.get('bedrooms', 0) >= filters['bedrooms']]
        if 'min_score' in filters:
            filtered = [p for p in filtered if p.get('opportunity_score', 0) >= filters['min_score']]

        # Sort
        if sort_by in ['opportunity_score', 'list_price', 'days_on_market']:
            filtered.sort(key=lambda x: x.get(sort_by, 0), reverse=(sort_by != 'list_price'))

        # Limit results
        results = filtered[:limit]

        return {
            "total_found": len(filtered),
            "returned": len(results),
            "properties": [
                {
                    "address": f"{p.get('street_address', 'Unknown')}, {p.get('city', '')}",
                    "price": p.get('list_price'),
                    "score": p.get('opportunity_score'),
                    "quality": p.get('deal_quality'),
                    "bedrooms": p.get('bedrooms'),
                    "bathrooms": p.get('bathrooms'),
                    "sqft": p.get('square_feet'),
                    "days_on_market": p.get('days_on_market'),
                    "listing_url": p.get('listing_url')
                }
                for p in results
            ]
        }

    def _tool_analyze_property(self, params: Dict) -> Dict:
        """Analyze property tool implementation"""
        address = params.get('property_address', '').lower()

        # Find property
        prop = None
        for p in self.properties:
            if address in p.get('street_address', '').lower():
                prop = p
                break

        if not prop:
            return {"error": "Property not found"}

        # Build analysis
        return {
            "property": {
                "address": f"{prop.get('street_address')}, {prop.get('city')}, {prop.get('state')}",
                "price": prop.get('list_price'),
                "tax_assessed": prop.get('tax_assessed_value'),
                "score": prop.get('opportunity_score'),
                "quality": prop.get('deal_quality'),
                "beds_baths": f"{prop.get('bedrooms', '?')} bed / {prop.get('bathrooms', '?')} bath",
                "sqft": prop.get('square_feet'),
                "price_per_sqft": prop.get('price_per_sqft'),
                "days_on_market": prop.get('days_on_market'),
                "year_built": prop.get('year_built'),
                "hoa_fee": prop.get('hoa_fee')
            },
            "insights": {
                "below_market": ((prop.get('tax_assessed_value', 0) - prop.get('list_price', 0)) / prop.get('tax_assessed_value', 1) * 100) if prop.get('tax_assessed_value') else 0,
                "seller_motivation": "High" if prop.get('days_on_market', 0) > 60 else "Medium" if prop.get('days_on_market', 0) > 30 else "Low"
            }
        }

    def _tool_market_insights(self, params: Dict) -> Dict:
        """Market insights tool implementation"""
        location = params.get('location', '').lower() if params.get('location') else None

        # Filter by location if specified
        properties = self.properties
        if location:
            properties = [p for p in properties if location in p.get('city', '').lower()]

        if not properties:
            return {"error": "No properties found for location"}

        # Calculate statistics
        prices = [p.get('list_price', 0) for p in properties if p.get('list_price')]
        scores = [p.get('opportunity_score', 0) for p in properties]
        dom = [p.get('days_on_market', 0) for p in properties if p.get('days_on_market')]

        return {
            "location": location or "All markets",
            "total_properties": len(properties),
            "pricing": {
                "median": sorted(prices)[len(prices)//2] if prices else 0,
                "average": sum(prices) / len(prices) if prices else 0,
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0
            },
            "opportunity": {
                "hot_deals": len([p for p in properties if p.get('opportunity_score', 0) >= 90]),
                "good_deals": len([p for p in properties if 75 <= p.get('opportunity_score', 0) < 90]),
                "average_score": sum(scores) / len(scores) if scores else 0
            },
            "market_dynamics": {
                "average_dom": sum(dom) / len(dom) if dom else 0,
                "quick_sales": len([d for d in dom if d < 30]),
                "stale_listings": len([d for d in dom if d > 90])
            }
        }

    def _tool_compare_properties(self, params: Dict) -> Dict:
        """Compare properties tool implementation"""
        addresses = params.get('property_addresses', [])

        properties = []
        for addr in addresses:
            addr_lower = addr.lower()
            for p in self.properties:
                if addr_lower in p.get('street_address', '').lower():
                    properties.append(p)
                    break

        return {
            "comparison": [
                {
                    "address": f"{p.get('street_address')}, {p.get('city')}",
                    "price": p.get('list_price'),
                    "score": p.get('opportunity_score'),
                    "sqft": p.get('square_feet'),
                    "price_per_sqft": p.get('price_per_sqft'),
                    "days_on_market": p.get('days_on_market')
                }
                for p in properties
            ]
        }

    def _tool_calculate_roi(self, params: Dict) -> Dict:
        """Calculate ROI tool implementation"""
        purchase_price = params.get('purchase_price')
        down_payment_pct = params.get('down_payment_pct', 20)
        estimated_rent = params.get('estimated_rent', 0)

        # Find property for context
        address = params.get('property_address', '').lower()
        prop = None
        for p in self.properties:
            if address in p.get('street_address', '').lower():
                prop = p
                break

        # Calculate returns
        down_payment = purchase_price * (down_payment_pct / 100)
        loan_amount = purchase_price - down_payment
        monthly_payment = loan_amount * 0.006  # Rough estimate ~7% interest

        # Estimate rent if not provided
        if not estimated_rent and prop:
            # Rough estimate: 0.8% of purchase price per month
            estimated_rent = purchase_price * 0.008

        monthly_cashflow = estimated_rent - monthly_payment - (prop.get('hoa_fee', 0) if prop else 0) - 200  # -$200 for maintenance/vacancy
        annual_cashflow = monthly_cashflow * 12
        cash_on_cash = (annual_cashflow / down_payment * 100) if down_payment > 0 else 0
        cap_rate = (annual_cashflow / purchase_price * 100) if purchase_price > 0 else 0

        return {
            "purchase_price": purchase_price,
            "down_payment": down_payment,
            "loan_amount": loan_amount,
            "estimated_monthly_rent": estimated_rent,
            "estimated_monthly_payment": monthly_payment,
            "monthly_cashflow": monthly_cashflow,
            "annual_cashflow": annual_cashflow,
            "cash_on_cash_return": cash_on_cash,
            "cap_rate": cap_rate
        }

    def _tool_web_search(self, params: Dict) -> Dict:
        """Web search tool implementation using Perplexity AI"""
        query = params.get('query')
        search_type = params.get('search_type', 'general')
        location = params.get('location', '')
        depth = params.get('depth', None)

        # Build enhanced query with location if provided
        enhanced_query = query
        if location and location.lower() not in query.lower():
            enhanced_query = f"{query} in {location}"

        # Execute Perplexity search
        result = self.perplexity.search(
            query=enhanced_query,
            search_domain=search_type,
            depth=depth,
            include_citations=True
        )

        return {
            "query": enhanced_query,
            "search_type": search_type,
            "answer": result.get('answer', ''),
            "citations": result.get('citations', []),
            "model_used": result.get('model_used'),
            "has_error": 'error' in result
        }

    def _tool_create_client(self, params: Dict) -> Dict:
        """Create client tool implementation"""
        try:
            client_id = self.db.create_client(
                name=params.get('name'),
                email=params.get('email'),
                phone=params.get('phone'),
                notes=params.get('notes')
            )

            return {
                "success": True,
                "client_id": client_id,
                "message": f"Client created successfully with ID: {client_id}"
            }
        except Exception as e:
            return {"error": f"Failed to create client: {str(e)}"}

    def _tool_create_search_agent(self, params: Dict) -> Dict:
        """Create search agent tool implementation"""
        try:
            client_id = params.get('client_id')

            # Build criteria dictionary
            criteria = {}
            if 'zip_codes' in params:
                criteria['zip_codes'] = params['zip_codes']
            if 'price_min' in params:
                criteria['price_min'] = params['price_min']
            if 'price_max' in params:
                criteria['price_max'] = params['price_max']
            if 'bedrooms_min' in params:
                criteria['bedrooms_min'] = params['bedrooms_min']
            if 'bathrooms_min' in params:
                criteria['bathrooms_min'] = params['bathrooms_min']
            if 'property_types' in params:
                criteria['property_types'] = params['property_types']
            if 'deal_quality' in params:
                criteria['deal_quality'] = params['deal_quality']
            if 'min_score' in params:
                criteria['min_score'] = params['min_score']

            # Create agent
            agent_id = self.agent_manager.create_agent(
                client_id=client_id,
                criteria=criteria,
                notification_email=params.get('notification_email', True),
                notification_sms=params.get('notification_sms', False),
                notification_chat=True
            )

            return {
                "success": True,
                "agent_id": agent_id,
                "message": f"Search agent {agent_id} created and started. Will check for matches every 4 hours."
            }
        except Exception as e:
            return {"error": f"Failed to create agent: {str(e)}"}

    def _tool_list_active_agents(self, params: Dict) -> Dict:
        """List active agents tool implementation"""
        try:
            client_id = params.get('client_id')
            agents = self.agent_manager.list_active_agents(client_id=client_id)

            return {
                "success": True,
                "count": len(agents),
                "agents": agents
            }
        except Exception as e:
            return {"error": f"Failed to list agents: {str(e)}"}

    def _tool_get_agent_status(self, params: Dict) -> Dict:
        """Get agent status tool implementation"""
        try:
            agent_id = params.get('agent_id')
            status = self.agent_manager.get_agent_status(agent_id)

            if not status:
                return {"error": f"Agent {agent_id} not found"}

            return {
                "success": True,
                "agent": status
            }
        except Exception as e:
            return {"error": f"Failed to get agent status: {str(e)}"}

    def _tool_pause_agent(self, params: Dict) -> Dict:
        """Pause agent tool implementation"""
        try:
            agent_id = params.get('agent_id')
            self.agent_manager.pause_agent(agent_id)

            return {
                "success": True,
                "message": f"Agent {agent_id} paused successfully"
            }
        except Exception as e:
            return {"error": f"Failed to pause agent: {str(e)}"}

    def _tool_resume_agent(self, params: Dict) -> Dict:
        """Resume agent tool implementation"""
        try:
            agent_id = params.get('agent_id')
            self.agent_manager.resume_agent(agent_id)

            return {
                "success": True,
                "message": f"Agent {agent_id} resumed successfully"
            }
        except Exception as e:
            return {"error": f"Failed to resume agent: {str(e)}"}

    def _tool_cancel_agent(self, params: Dict) -> Dict:
        """Cancel agent tool implementation"""
        try:
            agent_id = params.get('agent_id')
            self.agent_manager.cancel_agent(agent_id)

            return {
                "success": True,
                "message": f"Agent {agent_id} cancelled successfully"
            }
        except Exception as e:
            return {"error": f"Failed to cancel agent: {str(e)}"}

    def _tool_complete_agent(self, params: Dict) -> Dict:
        """Complete agent tool implementation"""
        try:
            agent_id = params.get('agent_id')
            self.agent_manager.complete_agent(agent_id)

            return {
                "success": True,
                "message": f"Agent {agent_id} marked as completed"
            }
        except Exception as e:
            return {"error": f"Failed to complete agent: {str(e)}"}

    def _tool_create_ghl_contact(self, params: Dict) -> Dict:
        """Create GHL contact tool implementation"""
        try:
            if not self.ghl_connector:
                return {"error": "GoHighLevel is not integrated"}

            client_id = params.get('client_id')
            name = params.get('name')
            email = params.get('email', '')
            phone = params.get('phone', '')

            # Create contact in GHL
            contact_data = {
                "name": name,
                "email": email,
                "phone": phone
            }

            result = self.ghl_connector.create_contact(contact_data)
            ghl_contact_id = result.get('id')

            # Store GHL contact ID in local client record
            self.db.update_client(client_id, ghl_contact_id=ghl_contact_id)

            return {
                "success": True,
                "ghl_contact_id": ghl_contact_id,
                "message": f"Contact created in GHL with ID: {ghl_contact_id}"
            }
        except Exception as e:
            return {"error": f"Failed to create GHL contact: {str(e)}"}

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
