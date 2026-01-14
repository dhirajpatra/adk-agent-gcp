# Google Cloud ADK AI Agents Tutorial

## Overview
This tutorial guides you through creating AI agents using Google Cloud's ADK (Agent Development Kit) with various tools and capabilities including currency exchange, web search, and Wikipedia integration.

## Prerequisites
- Google Cloud account with billing enabled
- Access to Google Cloud Shell

## Setup Instructions

### 1. Launch Cloud Shell
Navigate to [shell.cloud.google.com](https://shell.cloud.google.com) and authorize if prompted.

### 2. Set Project ID
```bash
gcloud config set project <your-project-id>
```

### 3. Enable Required APIs
```bash
gcloud services enable aiplatform.googleapis.com
```

### 4. Create Python Virtual Environment
```bash
# 1. Create project directory
mkdir ai-agents-adk
cd ai-agents-adk

# 2. Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate

# 3. Install ADK package
uv pip install google-adk
```

### 5. Create an Agent
```bash
adk create personal_assistant
```
Follow the prompts:
- Choose model: Select `1` for gemini-2.5-flash
- Choose backend: Select `2` for Vertex AI
- Confirm Project ID: Press Enter if correct
- Confirm region: Press Enter for us-central1

### 6. Explore Agent Code
Open the `ai-agents-adk` folder in Cloud Shell Editor:
1. Click **File > Open Folder...**
2. Select the `ai-agents-adk` folder
3. Click **OK**

Key files:
- `agent.py` - Main agent configuration
- `__init__.py` - Package initialization
- `.env` - Environment variables (hidden by default)

To view hidden files:
- Click **View > Toggle Hidden Files**

Example `.env` content:
```bash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=project-003dc6bc-7774-47c5-26b
GOOGLE_CLOUD_LOCATION=us-central1
```

### 7. Run the Agent in Terminal
```bash
adk run personal_assistant
```
Type `exit` to exit the chat session.

### 8. Troubleshooting

**Issue: "This API method requires billing to be enabled"**
- Verify Project ID in `.env` file
- Ensure billing account is linked
- Link to Google Cloud Platform Trial Billing Account if needed

**Issue: "Vertex AI API has not been used in project"**
```bash
gcloud services enable aiplatform.googleapis.com
```

### 9. Run the Agent in Web UI
```bash
adk web
```
Access options:
1. **Terminal**: Ctrl/Cmd + Click the link (http://127.0.0.1:8000)
2. **Web Preview**: 
   - Click Web Preview button
   - Select Change Port
   - Enter port 8000
   - Click Change and Preview

## Adding Custom Tools

### 10. Build Currency Exchange Tool

**a. Create custom_functions.py**
```bash
touch personal_assistant/custom_functions.py
```

**Folder structure:**
```
ai-agents-adk/
└── personal_assistant/
    ├── .env
    ├── __init__.py
    ├── agent.py
    └── custom_functions.py
```

**b. Add currency exchange function** (`custom_functions.py`):
```python
import requests

def get_fx_rate(base: str, target: str):
    """
    Fetches the current exchange rate between two currencies.

    Args:
        base: The base currency (e.g., "SGD").
        target: The target currency (e.g., "JPY").

    Returns:
        The exchange rate information as a json response,
        or None if the rate could not be fetched.
    """
    base_url = "https://hexarate.paikama.co/api/rates/latest"
    api_url = f"{base_url}/{base}?target={target}"

    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
```

**c. Update agent.py:**
```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .custom_functions import get_fx_rate

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[FunctionTool(get_fx_rate)]
)
```

**d. Test the agent:**
```bash
adk web
```
Ask: "What is the exchange rate from Singapore dollars to Japanese yen?"

### 11. Integrate Google Search Tool

**a. Create custom_agents.py:**
```bash
touch personal_assistant/custom_agents.py
```

**Folder structure:**
```
ai-agents-adk/
└── personal_assistant/
    ├── .env
    ├── __init__.py
    ├── agent.py
    ├── custom_functions.py
    └── custom_agents.py
```

**b. Add search agent** (`custom_agents.py`):
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

google_search_agent = Agent(
    model='gemini-2.5-flash',
    name='google_search_agent',
    description='A search agent that uses google search to get latest information about current events, weather, or business hours.',
    instruction='Use google search to answer user questions about real-time, logistical information.',
    tools=[google_search],
)
```

**c. Update agent.py:**
```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from .custom_functions import get_fx_rate
from .custom_agents import google_search_agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    tools=[
        FunctionTool(get_fx_rate), 
        AgentTool(agent=google_search_agent),
    ]
)
```

**d. Test with:**
Ask: "What is the weather forecast in Tokyo, Japan for next month?"

### 12. Add LangChain Wikipedia Tool

**a. Install dependencies:**
```bash
uv pip install langchain-community wikipedia
```

**b. Create third_party_tools.py:**
```bash
touch personal_assistant/third_party_tools.py
```

**Folder structure:**
```
ai-agents-adk/
└── personal_assistant/
    ├── .env
    ├── __init__.py
    ├── agent.py
    ├── custom_functions.py
    ├── custom_agents.py
    └── third_party_tools.py
```

**c. Add Wikipedia tool** (`third_party_tools.py`):
```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

langchain_wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=3000)
)

langchain_wikipedia_tool.description = (
    "Provides deep historical and cultural information on landmarks, concepts, and places."
    "Use this for 'tell me about' or 'what is the history of' type questions."
)
```

**d. Final agent.py:**
```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from .custom_functions import get_fx_rate
from .custom_agents import google_search_agent
from .third_party_tools import langchain_wikipedia_tool

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    tools=[
        FunctionTool(get_fx_rate), 
        AgentTool(agent=google_search_agent),
        LangchainTool(langchain_wikipedia_tool),
    ]
)
```

**e. Test with:**
Ask: "Tell me about the history of Kyoto"

**f. View event details:**
In the ADK web UI, click the **Events** tab and select the most recent `functionCall` event to see how the agent made decisions.

## GitHub Setup (Optional)

To publish code to GitHub from Cloud Shell:

```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --list

# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Set permissions
chmod 600 ~/.ssh/id_ed25519

# Test connection
ssh -T git@github.com
```

## Cleanup

### Remove Local Files Only
```bash
cd ~
rm -rf ai-agents-adk
gcloud services disable aiplatform.googleapis.com
```

### Disable Vertex AI API
```bash
gcloud services disable aiplatform.googleapis.com
```

### Shut Down Entire Google Cloud Project
Visit: https://cloud.google.com/resource-manager/docs/creating-managing-projects#shut_down_a_project

## Next Steps

### 13. Build Advanced Multi-Agent Systems
- **Travel Planning Agent**: Transfer conversations between specialized agents
- **Movie Pitch Generator**: Create automated writer's room with researcher, screenwriter, and critic agents
- **Workflow Agents**: Control flow automatically without user input at every step
- **Session State**: Pass information between agents

## Notes
- ADK supports three tool categories:
  1. **Function Tools**: Custom tools for unique requirements
  2. **Built-in Tools**: Ready-to-use tools (Google Search, Code Execution)
  3. **Third-party Tools**: External libraries (Serper, LangChain, CrewAI)
- Use `AgentTool` wrapper to make agents act as tools
- Use `LangchainTool` wrapper to integrate LangChain tools
- The `root_agent` acts as an orchestrator to delegate tasks to specialized tools/agents