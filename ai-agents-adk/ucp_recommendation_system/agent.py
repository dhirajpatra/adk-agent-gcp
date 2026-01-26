"""
Main Agent Configuration
File: recommendation_system/agent.py
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from .tools import (
    get_product_recommendations,
    track_user_interaction,
    get_trending_products
)

# --- Load .env values ---
load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")

# Ensure you use the exact string for the model as per Vertex/AI Studio docs
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

# ==================== AGENTS ====================

# Specialized Recommendation Agent
recommendation_agent = Agent(
    model=model,
    name='recommendation_agent',
    description='Provides personalized product recommendations for e-commerce platforms',
    instruction="""
    You are an intelligent e-commerce recommendation assistant. Your role:
    
    1. Analyze user browsing history and behavior
    2. Suggest relevant products based on patterns
    3. Explain why each product is recommended
    4. Track user interactions to improve future recommendations
    5. Identify trending products when asked
    
    Be conversational and helpful. Always explain recommendations clearly.
    Format recommendations as numbered lists with clear explanations.
    """,
    tools=[
        FunctionTool(get_product_recommendations),
        FunctionTool(track_user_interaction),
        FunctionTool(get_trending_products)
    ]
)

# Root Orchestrator Agent
root_agent = Agent(
    model=model,
    name='ecommerce_assistant',
    description='Main assistant for e-commerce recommendation system',
    instruction="""
    Welcome users and help them discover products. You can:
    - Provide personalized recommendations
    - Show trending products
    - Track their interests
    - Answer product-related questions
    
    For recommendation requests, transfer to the recommendation_agent.
    Be friendly and guide users to find what they need.
    """,
    sub_agents=[recommendation_agent]
)