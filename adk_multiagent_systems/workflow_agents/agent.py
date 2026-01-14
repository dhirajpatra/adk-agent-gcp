"""
Defines the agents for the second part of the lab (workflow agents example).

This module builds a multi-agent system to generate a movie pitch.
It includes initial definitions for:
- 'researcher': An agent that uses Wikipedia to find facts.
- 'screenwriter': An agent that writes a plot outline.
- 'file_writer': An agent that saves the final pitch to a file.
- 'film_concept_team': A SequentialAgent that orchestrates the simple workflow.
- 'root_agent' ('greeter'): The parent agent that starts the user interaction.
- Helper tools: 'append_to_state' and 'write_file'.
"""
import os
import logging
import google.cloud.logging

from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent, Orchestrator
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool  # import
from google.genai import types
from google.adk.tools import exit_loop

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import Callable, List


cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)

# Tools

def append_to_state(
    tool_context: ToolContext, field: str, response: str
) -> dict[str, str]:
    """Append new output to an existing state key.

    Args:
        field (str): a field name to append to
        response (str): a string to append to the field

    Returns:
        dict[str, str]: {"status": "success"}
    """
    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    logging.info(f"[Added to {field}] {response}")
    return {"status": "success"}


def write_file(
    tool_context: ToolContext,
    directory: str,
    filename: str,
    content: str
) -> dict[str, str]:
    target_path = os.path.join(directory, filename)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write(content)
    return {"status": "success"}

# Custom Workflow Agent

class ConditionalAgent(SequentialAgent):
    """A custom agent that runs one of two sequences of sub-agents based on a condition."""

    def __init__(
        self,
        condition: Callable[[ToolContext], bool],
        if_true_agents: List[Orchestrator],
        if_false_agents: List[Orchestrator],
        **kwargs,
    ):
        """Initializes the ConditionalAgent.

        Args:
            condition: A callable that takes a ToolContext and returns a boolean.
            if_true_agents: A list of sub-agents to run if the condition is true.
            if_false_agents: A list of sub-agents to run if the condition is false.
            **kwargs: Additional arguments for the base SequentialAgent.
        """
        super().__init__(sub_agents=[], **kwargs)
        self._condition = condition
        self._if_true_agents = if_true_agents
        self._if_false_agents = if_false_agents

    def plan(self, tool_context: ToolContext) -> Orchestrator.Plan:
        """Overrides the plan to choose a workflow based on the condition."""
        if self._condition(tool_context):
            logging.info(f"Condition for '{self.name}' was true. Running 'if_true' agents.")
            self.sub_agents = self._if_true_agents
        else:
            logging.info(f"Condition for '{self.name}' was false. Running 'if_false' agents.")
            self.sub_agents = self._if_false_agents
        return super().plan(tool_context)

# Agents

box_office_researcher = Agent(
    name="box_office_researcher",
    model=model_name,
    description="Considers the box office potential of this film",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    Write a report on the box office potential of a movie like that described in PLOT_OUTLINE based on the reported box office performance of other recent films.
    """,
    output_key="box_office_report"
)

casting_agent = Agent(
    name="casting_agent",
    model=model_name,
    description="Generates casting ideas for this film",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    Generate ideas for casting for the characters described in PLOT_OUTLINE
    by suggesting actors who have received positive feedback from critics and/or
    fans when they have played similar roles.
    """,
    output_key="casting_report"
)

indian_line_producer = Agent(
    name="indian_line_producer",
    model=model_name,
    description="Estimates the production cost for this film if it were made in India.",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    You are a line producer for the Indian film industry.
    Based on the provided PLOT_OUTLINE, create a rough budget estimate for producing this movie in India.
    Consider factors like locations (historical vs. modern), potential for special effects, and cast size.
    Provide the estimate in Indian Rupees (INR) and US Dollars (USD).
    """,
    output_key="indian_budget_estimate"
)

preproduction_team = ParallelAgent(
    name="preproduction_team",
    sub_agents=[
        box_office_researcher,
        casting_agent,
        indian_line_producer
    ]
)

producer = Agent(
    name="producer",
    model=model_name,
    description="Makes a final decision on the movie pitch.",
    instruction="""
    INSTRUCTIONS:
    You are the Producer. You have the final say.
    Review the PLOT_OUTLINE and the CRITICAL_FEEDBACK.
    If the pitch is strong and ready, say "This is a hit! Let's make this movie!".
    If the pitch is weak and needs more work, say "This isn't ready yet. Back to the drawing board."

    PLOT_OUTLINE: { PLOT_OUTLINE? }
    CRITICAL_FEEDBACK: { CRITICAL_FEEDBACK? }
    """
)
critic = Agent(
    name="critic",
    model=model_name,
    description="Reviews the outline so that it can be improved.",
    instruction="""
    INSTRUCTIONS:
    Consider these questions about the PLOT_OUTLINE:
    - Does it meet a satisfying three-act cinematic structure?
    - Do the characters' struggles seem engaging?
    - Does it feel grounded in a real time period in history?
    - Does it sufficiently incorporate historical details from the RESEARCH?

    If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.
    If significant improvements can be made, use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
    Explain your decision and briefly summarize the feedback you have provided.

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    RESEARCH:
    { research? }
    """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[append_to_state, exit_loop]
)

file_writer = Agent(
    name="file_writer",
    model=model_name,
    description="Creates marketing details and saves a pitch document.",
    instruction="""
    INSTRUCTIONS:
    - Create a marketable, contemporary movie title suggestion for the movie described in the PLOT_OUTLINE.
    If a title has been suggested in PLOT_OUTLINE, you can use it, or replace it with a better one.
    - Use your 'write_file' tool to create a new txt file with the following arguments:
    - for a filename, use the movie title
    - Write to the 'movie_pitches' directory.
    - For the 'content' to write, include:
    - The PLOT_OUTLINE
    - The BOX_OFFICE_REPORT
    - The CASTING_REPORT
    - The INDIAN_BUDGET_ESTIMATE

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    BOX_OFFICE_REPORT:
    { box_office_report? }

    CASTING_REPORT:
    { casting_report? }

    INDIAN_BUDGET_ESTIMATE:
    { indian_budget_estimate? }
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[write_file],
)

screenwriter = Agent(
    name="screenwriter",
    model=model_name,
    description="As a screenwriter, write a logline and plot outline for a biopic about a historical character.",
    instruction="""
    INSTRUCTIONS:
    Your goal is to write a logline and three-act plot outline for an inspiring movie about the historical character(s) described by the PROMPT: { PROMPT? }

    - If there is CRITICAL_FEEDBACK, use those thoughts to improve upon the outline.
    - If there is RESEARCH provided, feel free to use details from it, but you are not required to use it all.
    - If there is a PLOT_OUTLINE, improve it.
    - Use the 'append_to_state' tool to write your logline and three-act plot outline to the field 'PLOT_OUTLINE'.
    - Summarize what you focused on in this pass.

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    RESEARCH:
    { research? }

    CRITICAL_FEEDBACK:
    { CRITICAL_FEEDBACK? }
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[append_to_state],
)

researcher = Agent(
    name="researcher",
    model=model_name,
    description="Answer research questions using Wikipedia.",
    instruction="""
    PROMPT:
    { PROMPT? }

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    CRITICAL_FEEDBACK:
    { CRITICAL_FEEDBACK? }

    INSTRUCTIONS:
    - If there is a CRITICAL_FEEDBACK, use your wikipedia tool to do research to solve those suggestions
    - If there is a PLOT_OUTLINE, use your wikipedia tool to do research to add more historical detail
    - If these are empty, use your Wikipedia tool to gather facts about the person in the PROMPT
    - Use the 'append_to_state' tool to add your research to the field 'research'.
    - Summarize what you have learned.
    Now, use your Wikipedia tool to do research.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[
        LangchainTool(tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())),
        append_to_state,
    ],
)

writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve a movie plot outline.",
    sub_agents=[
        researcher,
        screenwriter,
        critic
    ],
    max_iterations=5, # to protect from infinite loop
)

def pitch_is_good(tool_context: ToolContext) -> bool:
    """Check if the critical feedback is empty, meaning the critic approved."""
    return not tool_context.state.get("CRITICAL_FEEDBACK")

pitch_approval_workflow = ConditionalAgent(
    name="pitch_approval_workflow",
    description="Decides whether to proceed with pre-production or send it back to the producer.",
    condition=pitch_is_good,
    if_true_agents=[preproduction_team, file_writer],
    if_false_agents=[producer]
)

film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[
        writers_room,
        pitch_approval_workflow,
    ],
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="Guides the user in crafting a movie plot.",
    instruction="""
    - Let the user know you will help them write a pitch for a hit movie. Ask them for   
      a historical figure to create a movie about.
    - When they respond, use the 'append_to_state' tool to store the user's response
      in the 'PROMPT' state key and transfer to the 'film_concept_team' agent
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[append_to_state],
    sub_agents=[film_concept_team],
)