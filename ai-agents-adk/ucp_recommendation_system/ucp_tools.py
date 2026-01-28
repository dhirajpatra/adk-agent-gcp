"""
UCP-Enhanced Tools for ADK Agent
File: recommendation_system/ucp_tools.py

Integrates real UCP merchant connections with ADK agents
"""

from typing import List, Dict, Optional
from .ucp_client import UCPMerchantRegistry, UCPProduct

# Initialize UCP merchant registry
ucp_registry = UCPMerchantRegistry()


def search_ucp_products(
    query: str,
    merchant_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10
):
    """
    Search products from UCP-compliant merchants.
    
    Args:
        query: Search query
        merchant_id: Specific merchant or search all
        category: Filter by category
        limit: Max results
        
    Returns:
        Dict with products from UCP merchants
    """
    try:
        if merchant_id:
            # Search specific merchant
            client = ucp_registry.get_client(merchant_id)
            if not client:
                return {
                    "status": "error",
                    "message": f"Merchant {merchant_id} not found"
                }
            
            products = client.search_products(query, category, limit)
        else:
            # Search all merchants
            products = ucp_registry.search_all_merchants(query, limit)
        
        # Convert to dict format
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "currency": p.currency,
                "image_url": p.image_url,
                "description": p.description
            }
            for p in products
        ]
        
        return {
            "status": "success",
            "query": query,
            "products": product_list,
            "count": len(product_list),
            "merchant": merchant_id or "all"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def get_ucp_recommendations(
    user_id: str,
    browsing_history: List[str],
    merchant_id: str = "shopify"
):
    """
    Get personalized recommendations from UCP merchant.
    
    Args:
        user_id: User identifier
        browsing_history: Recently viewed products
        merchant_id: Target merchant
        
    Returns:
        Personalized recommendations from UCP
    """
    try:
        client = ucp_registry.get_client(merchant_id)
        if not client:
            return {
                "status": "error",
                "message": f"Merchant {merchant_id} not configured"
            }
        
        context = {
            "browsing_history": browsing_history,
            "platform": "adk_agent"
        }
        
        products = client.get_recommendations(user_id, context)
        
        recommendations = [
            {
                "product_id": p.id,
                "name": p.name,
                "price": p.price,
                "currency": p.currency,
                "reason": "Recommended by UCP merchant"
            }
            for p in products
        ]
        
        return {
            "status": "success",
            "user_id": user_id,
            "merchant": merchant_id,
            "recommendations": recommendations,
            "source": "UCP"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def create_ucp_checkout(
    product_ids: List[str],
    quantities: List[int],
    user_id: str,
    merchant_id: str = "shopify"
):
    """
    Create UCP checkout session for selected products.
    
    Args:
        product_ids: List of product IDs
        quantities: Corresponding quantities
        user_id: User identifier
        merchant_id: Target merchant
        
    Returns:
        Checkout session with URL
    """
    try:
        client = ucp_registry.get_client(merchant_id)
        if not client:
            return {
                "status": "error",
                "message": f"Merchant {merchant_id} not configured"
            }
        
        # Build line items
        line_items = [
            {
                "product_id": pid,
                "quantity": qty
            }
            for pid, qty in zip(product_ids, quantities)
        ]
        
        # Create checkout session via UCP
        session = client.create_checkout_session(line_items, user_id)
        
        if "error" in session:
            return {
                "status": "error",
                "message": session["error"]
            }
        
        return {
            "status": "success",
            "session_id": session.get("session_id"),
            "checkout_url": session.get("checkout_url"),
            "merchant": merchant_id,
            "total": session.get("total"),
            "message": "Checkout session created. User can complete purchase via the URL."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def track_ucp_interaction(
    user_id: str,
    product_id: str,
    interaction_type: str,
    merchant_id: str = "shopify"
):
    """
    Track user interaction via UCP analytics.
    
    Args:
        user_id: User identifier
        product_id: Product ID
        interaction_type: view, click, purchase, add_to_cart
        merchant_id: Target merchant
        
    Returns:
        Tracking confirmation
    """
    try:
        client = ucp_registry.get_client(merchant_id)
        if not client:
            return {
                "status": "error",
                "message": f"Merchant {merchant_id} not configured"
            }
        
        success = client.track_event(
            event_type=interaction_type,
            product_id=product_id,
            user_id=user_id
        )
        
        if success:
            return {
                "status": "success",
                "tracked": {
                    "user_id": user_id,
                    "product_id": product_id,
                    "interaction": interaction_type,
                    "merchant": merchant_id,
                    "protocol": "UCP"
                }
            }
        else:
            return {
                "status": "error",
                "message": "Tracking failed"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def discover_merchant_capabilities(merchant_id: str = "shopify"):
    """
    Discover UCP capabilities of a merchant.
    
    Args:
        merchant_id: Target merchant
        
    Returns:
        Merchant capabilities (Checkout, Catalog, Orders, etc.)
    """
    try:
        client = ucp_registry.get_client(merchant_id)
        if not client:
            return {
                "status": "error",
                "message": f"Merchant {merchant_id} not configured"
            }
        
        capabilities = client.discover_capabilities()
        
        return {
            "status": "success",
            "merchant_id": merchant_id,
            "capabilities": capabilities,
            "protocol": "UCP"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }