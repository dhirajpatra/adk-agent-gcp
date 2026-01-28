# UCP-Connected Recommendation System Setup Guide

## 🔌 What's Changed?

Your recommendation system now **connects to real UCP merchant servers** instead of using mock data!

## ✅ New Features

1. **Real Merchant Integration** - Connects to Shopify, Google merchants, or any UCP-compliant store
2. **Product Discovery** - Search products across UCP merchants
3. **Personalized Recommendations** - Get UCP-powered suggestions
4. **Secure Checkout** - Create UCP checkout sessions
5. **Analytics Tracking** - Track user interactions via UCP

## 📦 Files Added

```
recommendation_system/
├── agent.py              (Updated: UCP-enabled agents)
├── ucp_client.py         (NEW: UCP protocol client)
├── tools.py          (NEW: UCP tools for ADK)
├── functions.py          (Original: Business logic)
└── __init__.py
```

## 🚀 Quick Start

### 1. Install Additional Dependencies

```bash
cd recommendation_system
pip install requests python-dotenv
```

### 2. Configure Your UCP Merchants

Edit `ucp_client.py` and add your merchant URLs:

```python
# Example: Your Shopify store
shopify_merchant = UCPMerchant(
    base_url="https://your-store.myshopify.com",
    merchant_id="your_store",
    capabilities=["Checkout", "Catalog", "Orders"]
)

# Example: Custom UCP merchant
custom_merchant = UCPMerchant(
    base_url="https://api.yourstore.com",
    merchant_id="my_store",
    capabilities=["Checkout", "Catalog", "Recommendations"]
)
```

### 3. Run the Agent

```bash
adk web
```

## 🔧 Testing UCP Connection

### Test Discovery
```python
# In ADK web interface
"Discover capabilities of shopify merchant"
```

### Test Product Search
```python
"Search for wireless headphones"
"Find electronics from shopify merchant"
```

### Test Recommendations
```python
"Get recommendations for user_123 who viewed laptops"
```

### Test Checkout
```python
"Create checkout for products P001 and P002"
```

## 🌐 UCP Endpoints (Standard)

Your system connects to these UCP endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/.well-known/ucp.json` | Capability discovery |
| `/ucp/catalog/search` | Product search |
| `/ucp/catalog/products/{id}` | Product details |
| `/ucp/checkout/sessions` | Create checkout |
| `/ucp/recommendations` | Get recommendations |
| `/ucp/events` | Track analytics |

## 🏪 Supported Merchants

### Shopify (UCP-enabled)
```python
base_url = "https://your-shop.myshopify.com"
```

### Google Merchants (via UCP)
```python
base_url = "https://shopping.googleapis.com/ucp"
```

### Custom UCP Merchants
Any server implementing the [UCP specification](https://github.com/Universal-Commerce-Protocol/ucp)

## 🔐 Security Notes

1. **Merchant of Record**: The merchant remains seller of record (UCP standard)
2. **Secure Payments**: Supports tokenized payments (Google Pay, PayPal, etc.)
3. **User Consent**: All purchases require explicit user consent
4. **Data Privacy**: User data stays with the merchant

## 📊 Architecture

```
User Query
    ↓
ADK Agent (root_agent)
    ↓
UCP Tools (ucp_tools.py)
    ↓
UCP Client (ucp_client.py)
    ↓
[HTTPS/REST API]
    ↓
UCP Merchant Server
    ↓
Response to User
```

## 🔄 Switching Between Mock and Real Data

### Use Real UCP Data (Default)
```python
from recommendation_system.ucp_tools import search_ucp_products
```

### Use Mock Data (Testing)
```python
from recommendation_system.tools import get_product_recommendations
```

## 🧪 Local Testing Without Merchant

For testing without a real merchant, use the mock endpoints:

```python
# In ucp_client.py, add a mock merchant:
mock_merchant = UCPMerchant(
    base_url="http://localhost:8080",  # Your local mock server
    merchant_id="mock",
    capabilities=["Checkout", "Catalog"]
)
```

Start UCP Mock Server:
```bash
python mock_ucp_server.py
```

## 📚 Resources

- [UCP Specification](https://github.com/Universal-Commerce-Protocol/ucp)
- [UCP Documentation](https://ucp.dev)
- [Google UCP Guide](https://developers.google.com/merchant/ucp)
- [Shopify UCP Integration](https://shopify.engineering/ucp)

## 🐛 Troubleshooting

### Merchant Not Found
```
Error: Merchant {id} not found
Solution: Check merchant_id in ucp_client.py matches your usage
```

### Connection Refused
```
Error: Connection refused
Solution: Verify merchant base_url is correct and server is running
```

### Invalid Response
```
Error: JSON decode error
Solution: Ensure merchant implements UCP specification correctly
```

## 🎯 Next Steps

1. ✅ Add your real merchant URLs
2. ✅ Test capability discovery
3. ✅ Test product search
4. ✅ Deploy to Cloud Run for production
5. ✅ Monitor via Cloud Logging

## 🔌 Integration Example

# Get recommendations
response = root_agent.chat(
    "Get recommendations for user user_123 who viewed laptop and mouse"
)
print(response)
```

## 📊 Production Deployment

### Option 1: Cloud Run
```bash
# Deploy as REST API
gcloud run deploy recommendation-agent \
  --source . \
  --region us-central1
```

### Option 2: Cloud Functions
```bash
# Deploy as serverless function
gcloud functions deploy recommend \
  --runtime python312 \
  --trigger-http
```

## 🔐 Environment Variables

```bash
# Optional
LOG_LEVEL=INFO
CACHE_TTL=3600
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test individual components
python -m recommendation_system.tools
python -m recommendation_system.functions
```

## 📚 Further Reading

- [ADK Documentation](https://cloud.google.com/adk)
- [Vertex AI](https://cloud.google.com/vertex-ai)
- [UCP Protocol](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp)