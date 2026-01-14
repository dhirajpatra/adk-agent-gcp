from google.adk.agents import Agent
from google.adk.tools import google_search
import os
from dotenv import load_dotenv

# --- Load .env values ---
load_dotenv()

model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


# Create an agent with google search tool as a search specialist
google_search_agent = Agent(
    model=model,
    name="google_search_agent",
    description="A search agent that uses google search to get latest information about current events, weather, or business hours.",
    instruction="Use google search to answer user questions about real-time, logistical information.",
    tools=[google_search],
)
