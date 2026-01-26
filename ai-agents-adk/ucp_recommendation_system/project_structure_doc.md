# E-commerce Recommendation System - Project Structure

## 📁 File Organization

ucp_recommendation_system/
├── __init__.py          # Package initialization & exports
├── ecommerce_recommender.py             # Agent definitions (orchestration layer)
├── functions.py             # Tool wrappers (ADK interface layer)
├── tools.py         # Business logic (core algorithms)
├── .env                 # Environment configuration
└── requirements.txt     # Python dependencies

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