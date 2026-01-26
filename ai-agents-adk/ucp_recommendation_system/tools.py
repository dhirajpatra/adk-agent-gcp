"""
Tool Definitions for Recommendation System
File: recommendation_system/tools.py
"""

from typing import List, Optional
from .functions import (
    generate_recommendations,
    log_interaction,
    fetch_trending_items
)

def get_product_recommendations(
    user_id: str,
    browsing_history: List[str],
    cart_items: Optional[List[str]] = None,
    category: Optional[str] = None
):
    """
    Generate product recommendations based on user behavior.
    
    Args:
        user_id: Unique user identifier
        browsing_history: List of recently viewed product IDs
        cart_items: Current items in cart (optional)
        category: Filter by product category (optional)
    
    Returns:
        Dict with recommended products and scores
    """
    try:
        recommendations = generate_recommendations(
            user_id=user_id,
            browsing_history=browsing_history,
            cart_items=cart_items or [],
            category=category
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations,
            "category_filter": category
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def track_user_interaction(
    user_id: str,
    product_id: str,
    interaction_type: str
):
    """
    Track user interactions for recommendation improvement.
    
    Args:
        user_id: User identifier
        product_id: Product interacted with
        interaction_type: Type of interaction (view, click, purchase, add_to_cart)
    
    Returns:
        Confirmation of tracked interaction
    """
    valid_interactions = ["view", "click", "purchase", "add_to_cart", "wishlist"]
    
    if interaction_type not in valid_interactions:
        return {
            "status": "error",
            "message": f"Invalid interaction type. Must be one of: {valid_interactions}"
        }
    
    try:
        result = log_interaction(
            user_id=user_id,
            product_id=product_id,
            interaction_type=interaction_type
        )
        
        return {
            "status": "success",
            "tracked": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def get_trending_products(
    category: Optional[str] = None,
    limit: int = 10,
    time_period: str = "7d"
):
    """
    Get currently trending products.
    
    Args:
        category: Filter by category (optional)
        limit: Number of products to return (default: 10)
        time_period: Time period for trends (7d, 30d, 90d)
    
    Returns:
        Dict with list of trending products
    """
    if limit > 50:
        limit = 50  # Max limit
    
    try:
        trending = fetch_trending_items(
            category=category,
            limit=limit,
            time_period=time_period
        )
        
        return {
            "status": "success",
            "trending_products": trending,
            "category": category,
            "period": time_period
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }