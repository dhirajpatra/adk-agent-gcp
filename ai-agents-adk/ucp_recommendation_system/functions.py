"""
Business Logic Functions for Recommendation System
File: recommendation_system/functions.py
"""

from typing import List, Dict
from datetime import datetime
import json

# ==================== RECOMMENDATION ENGINE ====================

def generate_recommendations(
    user_id: str,
    browsing_history: List[str],
    cart_items: List[str],
    category: str = None
) -> List[Dict]:
    """
    Core recommendation algorithm.
    Replace this with your ML model or database query.
    
    Args:
        user_id: User identifier
        browsing_history: Recently viewed products
        cart_items: Current cart contents
        category: Optional category filter
    
    Returns:
        List of recommended products with scores
    """
    # Simulated recommendation logic
    # In production, replace with:
    # - ML model predictions (TensorFlow, PyTorch)
    # - Collaborative filtering
    # - Content-based filtering
    # - Hybrid approaches
    
    base_recommendations = [
        {
            "product_id": "P001",
            "name": "Wireless Earbuds Pro",
            "category": "electronics",
            "price": 79.99,
            "score": 0.95,
            "reason": "Based on your browsing history"
        },
        {
            "product_id": "P002",
            "name": "Premium Phone Case",
            "category": "accessories",
            "price": 24.99,
            "score": 0.88,
            "reason": "Frequently bought together with items in your cart"
        },
        {
            "product_id": "P003",
            "name": "Screen Protector Ultra",
            "category": "accessories",
            "price": 12.99,
            "score": 0.82,
            "reason": "Similar users also purchased"
        },
        {
            "product_id": "P004",
            "name": "Portable Charger 20000mAh",
            "category": "electronics",
            "price": 45.99,
            "score": 0.78,
            "reason": "Trending in your area"
        },
        {
            "product_id": "P005",
            "name": "USB-C Cable 3-Pack",
            "category": "accessories",
            "price": 15.99,
            "score": 0.75,
            "reason": "Complements your recent purchases"
        }
    ]
    
    # Apply category filter if specified
    if category:
        recommendations = [
            r for r in base_recommendations 
            if r["category"].lower() == category.lower()
        ]
    else:
        recommendations = base_recommendations
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    return recommendations


# ==================== INTERACTION TRACKING ====================

def log_interaction(
    user_id: str,
    product_id: str,
    interaction_type: str
) -> Dict:
    """
    Log user interaction for analytics and ML training.
    
    In production, save to:
    - BigQuery for analytics
    - Cloud Firestore for real-time
    - Pub/Sub for streaming processing
    
    Args:
        user_id: User identifier
        product_id: Product ID
        interaction_type: Type of interaction
    
    Returns:
        Logged interaction details
    """
    interaction_data = {
        "user_id": user_id,
        "product_id": product_id,
        "interaction": interaction_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": f"sess_{user_id}_{datetime.now().timestamp()}"
    }
    
    # TODO: Replace with actual storage
    # Example: Save to BigQuery
    # from google.cloud import bigquery
    # client = bigquery.Client()
    # table_id = "your-project.dataset.interactions"
    # errors = client.insert_rows_json(table_id, [interaction_data])
    
    # For now, just return the data (you could log to file)
    print(f"[INTERACTION LOGGED] {json.dumps(interaction_data)}")
    
    return interaction_data


# ==================== TRENDING ANALYSIS ====================

def fetch_trending_items(
    category: str = None,
    limit: int = 10,
    time_period: str = "7d"
) -> List[Dict]:
    """
    Fetch trending products based on recent activity.
    
    In production, query from:
    - BigQuery analytics
    - Redis cache for hot items
    - Real-time analytics pipeline
    
    Args:
        category: Optional category filter
        limit: Max number of items
        time_period: Time window for trends
    
    Returns:
        List of trending products
    """
    # Simulated trending data
    # Replace with actual analytics query
    
    all_trending = [
        {
            "product_id": "T001",
            "name": "Smart Watch Series 5",
            "category": "electronics",
            "price": 299.99,
            "trend_score": 98,
            "views_24h": 15420,
            "purchases_24h": 342
        },
        {
            "product_id": "T002",
            "name": "Ergonomic Laptop Stand",
            "category": "accessories",
            "price": 49.99,
            "trend_score": 95,
            "views_24h": 12350,
            "purchases_24h": 289
        },
        {
            "product_id": "T003",
            "name": "USB-C Hub 7-in-1",
            "category": "electronics",
            "price": 39.99,
            "trend_score": 92,
            "views_24h": 10890,
            "purchases_24h": 245
        },
        {
            "product_id": "T004",
            "name": "Wireless Keyboard & Mouse",
            "category": "accessories",
            "price": 59.99,
            "trend_score": 89,
            "views_24h": 9876,
            "purchases_24h": 198
        },
        {
            "product_id": "T005",
            "name": "4K Webcam",
            "category": "electronics",
            "price": 129.99,
            "trend_score": 87,
            "views_24h": 8765,
            "purchases_24h": 176
        }
    ]
    
    # Apply category filter
    if category:
        trending = [
            t for t in all_trending 
            if t["category"].lower() == category.lower()
        ]
    else:
        trending = all_trending
    
    # Apply limit
    return trending[:limit]


# ==================== UTILITY FUNCTIONS ====================

def calculate_similarity_score(product_a: str, product_b: str) -> float:
    """
    Calculate similarity between two products.
    Replace with actual similarity algorithm.
    """
    # Placeholder - implement cosine similarity, embeddings, etc.
    return 0.75


def get_user_preferences(user_id: str) -> Dict:
    """
    Fetch user preferences and history.
    Query from user database.
    """
    # Placeholder - query from Cloud Firestore or SQL
    return {
        "user_id": user_id,
        "preferred_categories": ["electronics", "accessories"],
        "price_range": {"min": 10, "max": 200},
        "last_purchase": "2026-01-20T15:30:00Z"
    }