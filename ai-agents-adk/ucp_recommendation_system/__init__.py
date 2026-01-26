"""
Package Initialization
File: recommendation_system/__init__.py
"""

from .agent import root_agent, recommendation_agent
from .tools import (
    get_product_recommendations,
    track_user_interaction,
    get_trending_products
)
from .functions import (
    generate_recommendations,
    log_interaction,
    fetch_trending_items
)

__version__ = "1.0.0"
__all__ = [
    "root_agent",
    "recommendation_agent",
    "get_product_recommendations",
    "track_user_interaction",
    "get_trending_products",
    "generate_recommendations",
    "log_interaction",
    "fetch_trending_items"
]