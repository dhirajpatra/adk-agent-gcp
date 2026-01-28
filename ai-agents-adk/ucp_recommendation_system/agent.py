"""
UCP-Connected Recommendation Agent
File: recommendation_system/agent.py

Now connects to real UCP merchant servers!
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .ucp_tools import (
    search_ucp_products,
    get_ucp_recommendations,
    create_ucp_checkout,
    track_ucp_interaction,
    discover_merchant_capabilities
)

# ==================== UCP-ENABLED AGENTS ====================

UCP_WP_CLIENT_BASE_URL = os.getenv("UCP_WP_CLIENT_BASE_URL")
UCP_WP_CLIENT_API_KEY = os.getenv("UCP_WP_CLIENT_API_KEY")
model = os.getenv("MODEL")

# Product Discovery Agent
discovery_agent = Agent(
    model=model,
    name='discovery_agent',
    description='Discovers products from UCP-compliant merchants',
    instruction="""
    You help users discover products from UCP-enabled merchants.
    
    Use search_ucp_products to find products matching user needs.
    You can search specific merchants or across all available merchants.
    Always explain which merchant the products come from.
    """,
    tools=[
        FunctionTool(search_ucp_products),
        FunctionTool(discover_merchant_capabilities)
    ]
)

# Recommendation Agent (UCP-powered)
recommendation_agent = Agent(
    model=model,
    name='recommendation_agent',
    description='Provides UCP-powered personalized recommendations',
    instruction="""
    You provide personalized recommendations from UCP merchants.
    
    Use get_ucp_recommendations to fetch personalized suggestions.
    Explain why each product is recommended.
    Track user interactions with track_ucp_interaction.
    
    Available merchants: shopify, custom
    """,
    tools=[
        FunctionTool(get_ucp_recommendations),
        FunctionTool(track_ucp_interaction)
    ]
)

# Checkout Agent
checkout_agent = Agent(
    model=model,
    name='checkout_agent',
    description='Creates UCP checkout sessions for purchases',
    instruction="""
    You help users complete purchases via UCP checkout.
    
    Use create_ucp_checkout to generate secure checkout sessions.
    Provide users with the checkout URL to complete their purchase.
    The merchant remains the seller of record (UCP standard).
    """,
    tools=[
        FunctionTool(create_ucp_checkout)
    ]
)

# Root Orchestrator Agent
root_agent = Agent(
    model=model,
    name='ucp_shopping_assistant',
    description='UCP-powered shopping assistant',
    instruction="""
    Welcome! I help you shop across UCP-enabled merchants.
    
    I can:
    - Discover products from multiple merchants (via UCP)
    - Provide personalized recommendations (via UCP)
    - Create secure checkout sessions (via UCP)
    - Track your interests for better suggestions
    
    When users want to:
    - Search/browse products → transfer to discovery_agent
    - Get recommendations → transfer to recommendation_agent  
    - Make a purchase → transfer to checkout_agent
    
    Always mention that we use Universal Commerce Protocol (UCP)
    for secure, standardized shopping across merchants.
    """,
    sub_agents=[discovery_agent, recommendation_agent, checkout_agent]
)


# ==================== CONFIGURATION ====================

"""
UCP Merchant Configuration:

1. Add your merchants in ucp_client.py:

    UCPMerchant(
        base_url="https://your-shop.myshopify.com",
        merchant_id="your_shop",
        capabilities=["Checkout", "Catalog", "Orders"]
    )

2. Supported UCP capabilities:
   - Checkout: Create checkout sessions
   - Catalog: Product search and discovery
   - Orders: Order management
   - Recommendations: Personalized suggestions
   - Identity: User account linking

3. UCP Endpoints (standard):
   - /.well-known/ucp.json (capability discovery)
   - /ucp/catalog/search (product search)
   - /ucp/checkout/sessions (checkout)
   - /ucp/recommendations (personalized)
   - /ucp/events (analytics tracking)

4. Compatible with:
   - Shopify (with UCP support)
   - Google AI Mode in Search
   - Gemini app
   - WordPress with WooCommerce Store API and UCP Adapter plugin from dhirajpatra
   - Any UCP-compliant merchant

Run with: adk web
"""