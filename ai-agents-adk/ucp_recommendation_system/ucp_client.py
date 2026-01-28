"""
UCP Integration Module
File: recommendation_system/ucp_client.py

Connects to UCP-compliant merchant servers for:
- Product discovery
- Checkout capabilities
- Order management
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class UCPMerchant:
    """UCP Merchant configuration"""
    base_url: str
    merchant_id: str
    capabilities: List[str]
    
@dataclass
class UCPProduct:
    """UCP Product representation"""
    id: str
    name: str
    price: float
    currency: str = "USD"
    image_url: Optional[str] = None
    description: Optional[str] = None


class UCPClient:
    """
    Client for interacting with UCP-compliant merchant servers.
    Based on Universal Commerce Protocol specification.
    """
    
    def __init__(self, merchant: UCPMerchant):
        self.merchant = merchant
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UCP-Version': '1.0'
        })
    
    def discover_capabilities(self) -> Dict:
        """
        Discover merchant capabilities via UCP discovery endpoint.
        
        Returns:
            Dict with supported capabilities (Checkout, Catalog, Orders, etc.)
        """
        try:
            response = self.session.get(
                f"{self.merchant.base_url}/.well-known/ucp.json"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Fallback to default capabilities
            return {
                "capabilities": self.merchant.capabilities,
                "merchant_id": self.merchant.merchant_id,
                "protocol_version": "1.0"
            }
    
    def search_products(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[UCPProduct]:
        """
        Search products using UCP Catalog capability.
        
        Args:
            query: Search query
            category: Filter by category
            limit: Max results
            
        Returns:
            List of UCP-compliant products
        """
        try:
            payload = {
                "query": query,
                "filters": {
                    "category": category
                } if category else {},
                "limit": limit
            }
            
            response = self.session.post(
                f"{self.merchant.base_url}/ucp/catalog/search",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            products = []
            for item in data.get("products", []):
                products.append(UCPProduct(
                    id=item["id"],
                    name=item["name"],
                    price=item["price"]["amount"],
                    currency=item["price"]["currency"],
                    image_url=item.get("image_url"),
                    description=item.get("description")
                ))
            
            return products
            
        except Exception as e:
            print(f"[UCP] Product search failed: {e}")
            return []
    
    def get_product_details(self, product_id: str) -> Optional[Dict]:
        """
        Get detailed product information via UCP Catalog.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product details or None
        """
        try:
            response = self.session.get(
                f"{self.merchant.base_url}/ucp/catalog/products/{product_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[UCP] Product details fetch failed: {e}")
            return None
    
    def create_checkout_session(
        self,
        line_items: List[Dict],
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Create UCP checkout session.
        
        Args:
            line_items: List of products with quantities
            user_id: Optional user identifier for personalization
            
        Returns:
            Checkout session data with URL
        """
        try:
            payload = {
                "line_items": line_items,
                "metadata": {
                    "user_id": user_id,
                    "source": "recommendation_agent"
                }
            }
            
            response = self.session.post(
                f"{self.merchant.base_url}/ucp/checkout/sessions",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"[UCP] Checkout session creation failed: {e}")
            return {"error": str(e)}
    
    def get_recommendations(
        self,
        user_id: str,
        context: Dict
    ) -> List[UCPProduct]:
        """
        Get personalized recommendations from UCP merchant.
        
        Args:
            user_id: User identifier
            context: Browsing/purchase context
            
        Returns:
            List of recommended products
        """
        try:
            payload = {
                "user_id": user_id,
                "context": context
            }
            
            response = self.session.post(
                f"{self.merchant.base_url}/ucp/recommendations",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            products = []
            for item in data.get("recommendations", []):
                products.append(UCPProduct(
                    id=item["product_id"],
                    name=item["name"],
                    price=item["price"],
                    currency=item.get("currency", "USD")
                ))
            
            return products
            
        except Exception as e:
            print(f"[UCP] Recommendations fetch failed: {e}")
            return []
    
    def track_event(
        self,
        event_type: str,
        product_id: str,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Track user events via UCP analytics endpoint.
        
        Args:
            event_type: view, click, purchase, add_to_cart
            product_id: Product identifier
            user_id: User identifier
            metadata: Additional event data
            
        Returns:
            Success status
        """
        try:
            payload = {
                "event_type": event_type,
                "product_id": product_id,
                "user_id": user_id,
                "metadata": metadata or {},
                "timestamp": "2026-01-27T10:00:00Z"
            }
            
            response = self.session.post(
                f"{self.merchant.base_url}/ucp/events",
                json=payload
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"[UCP] Event tracking failed: {e}")
            return False


# ==================== UCP MERCHANT REGISTRY ====================

class UCPMerchantRegistry:
    """Registry of UCP-compliant merchants"""
    
    def __init__(self):
        self.merchants: Dict[str, UCPClient] = {}
        self._load_merchants()
    
    def _load_merchants(self):
        """Load configured merchants"""
        
        # Example: Shopify merchant with UCP support
        shopify_merchant = UCPMerchant(
            base_url="https://your-shop.myshopify.com",
            merchant_id="shopify_store_123",
            capabilities=["Checkout", "Catalog", "Orders"]
        )
        self.merchants["shopify"] = UCPClient(shopify_merchant)
        
        # Example: Custom UCP merchant
        custom_merchant = UCPMerchant(
            base_url="https://api.yourstore.com",
            merchant_id="custom_store_456",
            capabilities=["Checkout", "Catalog", "Recommendations"]
        )
        self.merchants["custom"] = UCPClient(custom_merchant)
    
    def get_client(self, merchant_id: str) -> Optional[UCPClient]:
        """Get UCP client for specific merchant"""
        return self.merchants.get(merchant_id)
    
    def search_all_merchants(
        self,
        query: str,
        limit: int = 5
    ) -> List[UCPProduct]:
        """Search across all registered merchants"""
        all_products = []
        
        for merchant_id, client in self.merchants.items():
            products = client.search_products(query, limit=limit)
            all_products.extend(products)
        
        return all_products[:limit]


# ==================== USAGE EXAMPLE ====================

"""
Example usage in your ADK agent:

from recommendation_system.ucp_client import UCPMerchantRegistry

registry = UCPMerchantRegistry()

# Search products across UCP merchants
products = registry.search_all_merchants("wireless headphones")

# Get recommendations from specific merchant
client = registry.get_client("shopify")
recommendations = client.get_recommendations(
    user_id="user_123",
    context={"browsing_history": ["product_a", "product_b"]}
)

# Create checkout session
session = client.create_checkout_session(
    line_items=[
        {"product_id": "P001", "quantity": 1}
    ],
    user_id="user_123"
)
"""