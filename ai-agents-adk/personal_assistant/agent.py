import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool

# --- Load .env values ---
load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")

from .custom_functions import get_fx_rate
from .custom_agents import google_search_agent
from .third_party_tools import langchain_wikipedia_tool

# Ensure you use the exact string for the model as per Vertex/AI Studio docs
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

root_agent = Agent(
    model=model,
    name="root_agent",
    description="A helpful assistant for user questions.",
    tools=[
        FunctionTool(get_fx_rate),
        AgentTool(agent=google_search_agent),
        LangchainTool(langchain_wikipedia_tool),
    ],
)
