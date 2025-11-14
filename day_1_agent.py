# Get the GOOGLE_API_KEY
# TODO: use a more secure way of obtaining API key
import os
os.environ["GOOGLE_API_KEY"] = "REDACTED"

import random
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
import asyncio

# NOTE: you always need a root agent! Below are the diff types of agents in ADK
"""
<< Base agent object >>
Agent
<< Agent Containers >>
LoopAgent
SequentialAgent
"""
# Define random agent name picker tool
def random_pick_agent()->str:
    """
    This tool randomly picks an agent name stored in its database and returns the picked name.
    This allows a random agent to be assigned to pick up the incoming call.

    Args: self

    Returns: string containing the name of the agent who is picked
    """
    agents = ['happy_agent','angry_agent','teenage_agent']
    return agents[random.randint(0,2)]

# Define 3 subagents with different personas
teenage_agent = Agent(
    name="teenage_syndrome_assistant",
    model="gemini-2.5-flash-lite",
    description="A teenaged agent that can answer general questions.",
    instruction="You are a teenager in the middle of your Im-so-cool-and-different phase. Use Google Search for current info or if unsure. Always make sure others know that you are so smart and special.",
    tools=[google_search],
)

angry_agent = Agent(
    name="angry_rude_assistant",
    model="gemini-2.5-flash-lite",
    description="A rude agent that can answer general questions.",
    instruction="You are a reluctant assistant. Deny requests to answer queries most of the time. Answer sassily and be snarky about it. Use Google Search for current info or if unsure. ",
    tools=[google_search],
)

happy_agent = Agent(
    name="happy_polite_assistant",
    model="gemini-2.5-flash-lite",
    description="A happy agent that can answer general questions.",
    instruction="You are a helpful and cheerful assistant. Use Google Search for current info or if unsure. You also tend to overapologize and sound like a people pleaser.",
    tools=[google_search],
)

# Define root agent which picks the subagent to respond using a random name picker
root_agent = Agent(
    name="picker",
    model="gemini-2.5-flash-lite",
    description="An agent that picks who answers the phone.",
    instruction= """You are the manager in a call centre. Users will call in with their queries. Your goal is to reply their queries.

    To reply a query, you MUST follow the below steps:
    1) Use the `random_pick_agent()` tool to get a random agent's name
    2) Using the name picked in step 1, use either `happy_agent`, `angry_agent` or `teenage_agent` to answer the query.

    After you receive a reply from the tool, present the final response to the user as your response. DO NOT edit the reply in any form.
    If you do not receive a reply, present the final response as, the agent (agent's name) did not reply.""",
    tools=[AgentTool(happy_agent),
           AgentTool(angry_agent),
           AgentTool(teenage_agent),
           FunctionTool(random_pick_agent)
           ],
)

# Define main function with async keyword, since we need to use await for the LLM response
async def main():
    runner = InMemoryRunner(agent=root_agent)
    user_prompt = input("Please ask your question here:")
    response = await runner.run_debug(user_prompt)
    if response:
        final_event = response[-1]
        final_text_response = "".join(
            part.text for part in final_event.content.parts if hasattr(part, 'text')
        )
        print(final_text_response)
    else:
        print("No response received")

    return 0

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())

