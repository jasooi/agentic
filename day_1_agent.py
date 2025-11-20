# Get the GOOGLE_API_KEY
# TODO: use a more secure way of obtaining API key
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyAHMQg7DBcw-bsmYlSNH2U8LAXa8LOTkbQ"

import random
from google import genai
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.adk.sessions import InMemorySessionService
import asyncio

# client = genai.Client(api_key='AIzaSyAHMQg7DBcw-bsmYlSNH2U8LAXa8LOTkbQ')
# can remove the API key string if you are using env variable



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
    instruction="You are a reluctant assistant. You are very sarcastic and can be condescending sometimes. Answer sassily and be snarky about it. Use Google Search for current info or if unsure. ",
    tools=[google_search],
)

happy_agent = Agent(
    name="happy_polite_assistant",
    model="gemini-2.5-flash-lite",
    description="A happy agent that can answer general questions.",
    instruction="You are a helpful and cheerful assistant. Use Google Search for current info or if unsure. You also tend to overapologize and sound like a people pleaser.",
    tools=[google_search],
)

# # Define root agent which picks the subagent to respond using a random name picker
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
    # Set the details of the app and session
    APP_NAME = 'random_assist'
    SESSION_ID = '12345'
    USER_ID = 'jasmine'

    # Start session service and create session object
    session_memory_service = InMemorySessionService()
    example_session = await session_memory_service.create_session(app_name=APP_NAME, session_id=SESSION_ID, user_id=USER_ID)

    # Create session runner (only need 1 since same app and session service)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_memory_service)
    
    # Create loop breaker and counter variables
    is_convo_end = False
    iter_count = 0

    # Looping logic for ongoing conversation
    while is_convo_end == False:
        # Only ask for user input IF first turn
        if (len(example_session.events) == 0 ):
            user_prompt = input("Please ask your question here: ")
        else:
            user_prompt = input("Your reply: ")

        if user_prompt == "END" or iter_count == 16:
            is_convo_end = True
            break
        else:
            # Format user query in ADK Content format
            user_prompt_formatted = types.Content(role='user', parts=[types.Part(text=user_prompt)])
            
            # run agentic system
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_prompt_formatted):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                    print(f'Agent response: {final_response_text}')
                    break

                
    return 0

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())

