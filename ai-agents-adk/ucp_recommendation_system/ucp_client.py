"""
UCP Integration Module
File: recommendation_system/ucp_client.py

Connects to UCP-compliant merchant servers for:
- Product discovery
- Checkout capabilities
- Order management
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

load_dotenv()

@dataclass
@dataclass
class UCPMerchant:
    """UCP Merchant configuration"""
    base_url: str
    merchant_id: str
    capabilities: List[str]
    api_key: Optional[str] = None

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
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UCP-Version': '1.0',
            'User-Agent': 'UCP-Agent/1.0'
        }
        
        if merchant.api_key:
            headers['X-UCP-API-Key'] = merchant.api_key
            
        self.session.headers.update(headers)
    
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
        """
        try:
            # Update for Ramdev (WordPress UCP) to use the new GET endpoint
            if self.merchant.merchant_id == "ramdev_clothing":
                return self._search_ucp_wp_endpoint(query, category, limit)

            payload = {
                "query": query,
                "filters": {
                    "category": category
                } if category else {},
                "limit": limit
            }
            
            response = self.session.post(
                f"{self.merchant.base_url}/catalog/search",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_products(data.get("products", []))
            
        except Exception as e:
            print(f"[UCP] Product search failed: {e}")
            return []

    def _search_ucp_wp_endpoint(self, query: str, category: str, limit: int) -> List[UCPProduct]:
        """
        Search using the new GET /product/search endpoint.
        Endpoint: GET /wp-json/ucp/v1/product/search
        """
        try:
            # base_url is expected to be .../wp-json/ucp/v1
            url = f"{self.merchant.base_url}/product/search"
            
            params = {
                "search": query,
                "limit": limit
            }
            if category:
                params["category"] = category

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # WP UCP Endpoint returns: { "success": true, "data": [ ... ], "meta": ... }
            products_data = []
            if isinstance(data, dict):
                products_data = data.get("data", [])
            elif isinstance(data, list):
                products_data = data
            
            products = []
            for item in products_data:
                # Parse WP-style product fields
                price_str = item.get("price", "0")
                try:
                    price_val = float(price_str)
                except:
                    price_val = 0.0
                
                products.append(UCPProduct(
                    id=str(item.get("id")),
                    name=item.get("name"),
                    price=price_val,
                    currency="INR", # Defaulting to INR as it is a specific Indian store (Ramdev), or 'USD' if safer.
                    # Given the context 'ramdevitworld' / Indian pricing (2499 for adapter), INR is likely.
                    # But UCPProduct defaults to USD. Let's use currency code if available or assume INR for this client.
                    # The response doesn't seem to have currency, but likely INR.
                    # I will assume 'USD' to be safe with existing types or 'INR' if I can. 
                    # Let's check if there is a currency field. Not in debug output.
                    image_url=item.get("image"), # Key is 'image' in WP response
                    description=item.get("short_description") or item.get("name")
                ))
            
            return products
            
        except Exception as e:
            print(f"[UCP-WP] Search failed: {e}")
            return []

    def _search_woocommerce_store_api(self, query: str, category: str, limit: int) -> List[UCPProduct]:
        """Fallback to WooCommerce Store API (Legacy/Backup)"""
        try:
            # Construct Store API URL from base URL (strip /ucp/v1)
            # Expecting base_url like .../wp-json/ucp/v1
            root_api = self.merchant.base_url.replace("/ucp/v1", "")
            url = f"{root_api}/wc/store/products"
            
            params = {
                "search": query,
                "per_page": limit
            }
            if category:
                params["category"] = category

            # Store API uses GET
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            products = []
            for item in data:
                # Store API Item adaptation
                image = item.get("images", [{}])[0].get("src")
                price = item.get("prices", {}).get("price", "0")
                currency = item.get("prices", {}).get("currency_code", "USD")
                
                # Price often comes as string in cents/smallest unit or formatted. 
                # Store API usually returns formatted string in 'price', but integers in 'regular_price'
                # We'll take a best effort approach
                try:
                    price_val = float(price) / 100 if float(price) > 1000 else float(price) # heuristic for cents
                except:
                    price_val = 0.0

                products.append(UCPProduct(
                    id=str(item.get("id")),
                    name=item.get("name"),
                    price=price_val,
                    currency=currency,
                    image_url=image,
                    description=item.get("short_description")
                ))
            return products
            
        except Exception as e:
            print(f"[WC-API] Search failed: {e}")
            return []

    def _parse_products(self, raw_products: List[Dict]) -> List[UCPProduct]:
        """Helper to parse standard UCP products"""
        products = []
        for item in raw_products:
            products.append(UCPProduct(
                id=item["id"],
                name=item["name"],
                price=item["price"]["amount"],
                currency=item["price"]["currency"],
                image_url=item.get("image_url"),
                description=item.get("description")
            ))
        return products
    
    def get_product_details(self, product_id: str) -> Optional[Dict]:
        """
        Get detailed product information via UCP Catalog.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product details or None
        """
        try:
            # Special handling for Ramdev (WordPress UCP)
            if self.merchant.merchant_id == "ramdev":
                # Fallback: Use WooCommerce Store API
                try:
                    # Construct Store API URL
                    root_api = self.merchant.base_url.replace("/ucp/v1", "")
                    url = f"{root_api}/wc/store/products/{product_id}"
                    
                    response = self.session.get(url)
                    response.raise_for_status()
                    item = response.json()
                    
                    # Parse Store API format
                    # Price is usually in minor units (e.g., cents/paisa)
                    # "prices": { "price": "249900", "currency_minor_unit": 2 ... }
                    price_data = item.get("prices", {})
                    raw_price = float(price_data.get("price", 0))
                    minor_unit = int(price_data.get("currency_minor_unit", 2))
                    price_val = raw_price / (10 ** minor_unit) if raw_price > 0 else 0.0
                    
                    # Get image
                    images = item.get("images", [])
                    image_url = images[0].get("src") if images else None
                    
                    return {
                        "id": str(item.get("id")),
                        "name": item.get("name"),
                        "price": {
                            "amount": price_val,
                            "currency": price_data.get("currency_code", "USD")
                        },
                        "image_url": image_url,
                        "description": item.get("description") or item.get("short_description")
                    }
                except Exception as wc_e:
                    print(f"[WC-API] Details fetch failed: {wc_e}")
                    return None

            response = self.session.get(
                f"{self.merchant.base_url}/catalog/products/{product_id}"
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
                f"{self.merchant.base_url}/checkout/sessions",
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
                f"{self.merchant.base_url}/recommendations",
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
                f"{self.merchant.base_url}/events",
                json=payload
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"[UCP] Event tracking failed: {e}")
            return False
            
    def create_session(self, user_data: Dict = None) -> Dict:
        """
        Create a new session (WP UCP Adapter specific).
        Endpoint: POST /session
        """
        try:
            payload = {"user_data": user_data or {}}
            response = self.session.post(
                f"{self.merchant.base_url}/session",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[UCP] Create session failed: {e}")
            return {"error": str(e)}

    def update_session(self, session_id: str, data: Dict) -> Dict:
        """
        Update session data.
        Endpoint: PUT /update/{session_id}
        """
        try:
            response = self.session.put(
                f"{self.merchant.base_url}/update/{session_id}",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[UCP] Update session failed: {e}")
            return {"error": str(e)}

    def complete_session(self, session_id: str) -> Dict:
        """
        Complete a session.
        Endpoint: POST /complete/{session_id}
        """
        try:
            response = self.session.post(
                f"{self.merchant.base_url}/complete/{session_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[UCP] Complete session failed: {e}")
            return {"error": str(e)}

    def get_session_status(self, session_id: str) -> Dict:
        """
        Check session status.
        Endpoint: GET /status/{session_id}
        """
        try:
            response = self.session.get(
                f"{self.merchant.base_url}/status/{session_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[UCP] Get session status failed: {e}")
            return {"error": str(e)}

    def get_sessions(self, limit: int = 10, status: Optional[str] = None) -> List[Dict]:
        """
        List all sessions.
        Endpoint: GET /sessions
        """
        try:
            params = {"limit": limit}
            if status:
                params["status"] = status
                
            response = self.session.get(
                f"{self.merchant.base_url}/sessions",
                params=params
            )
            response.raise_for_status()
            # Assuming it returns a list of sessions or a dict with 'sessions' key
            data = response.json()
            if isinstance(data, list):
                return data
            return data.get("sessions", [])
        except Exception as e:
            print(f"[UCP] Get sessions failed: {e}")
            return []


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
            base_url="https://your-shop.myshopify.com/ucp",
            merchant_id="shopify_store_123",
            capabilities=["Checkout", "Catalog", "Orders"]
        )
        self.merchants["shopify"] = UCPClient(shopify_merchant)
        
        # Example: Custom UCP merchant
        custom_merchant = UCPMerchant(
            base_url="https://api.yourstore.com/ucp",
            merchant_id="custom_store_456",
            capabilities=["Checkout", "Catalog", "Recommendations"]
        )
        self.merchants["custom"] = UCPClient(custom_merchant)

        # Ramdev Electronics (UCP Adapter for WooCommerce)
        ramdev_base_url = os.getenv("UCP_WP_CLIENT_BASE_URL")
        ramdev_api_key = os.getenv("UCP_WP_CLIENT_API_KEY")

        if ramdev_base_url and ramdev_api_key:
            ramdev_merchant = UCPMerchant(
                base_url=ramdev_base_url,
                merchant_id="ramdev_clothing",
                capabilities=["Checkout", "Catalog", "Recommendations", "Session"],
                api_key=ramdev_api_key
            )
            self.merchants["ramdev"] = UCPClient(ramdev_merchant)
        else:
            print("[Warning] UCP_WP_CLIENT_BASE_URL or UCP_WP_CLIENT_API_KEY not set. 'ramdev' client disabled.")
    
    def get_client(self, merchant_id: str) -> Optional[UCPClient]:
        """Get UCP client for specific merchant"""
        if merchant_id == "ramdevitworld":
            return self.merchants.get("ramdev")
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