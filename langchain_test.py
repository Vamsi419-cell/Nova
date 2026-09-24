import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from nova.tools.caliculator import caliculator as caliculator_fn
from nova.tools.whether import whether as whether_fn
from nova.tools.websearch import websearch as websearch_fn
from nova.schemas.tools import (
    caliculator_val,
    whether_val,
    websearch_val,
)


load_dotenv()


model = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
)


@tool("caliculator", args_schema=caliculator_val)
def caliculator(expression: str):
    """Evaluate a mathematical expression and return the result."""
    return caliculator_fn(expression)


@tool("whether", args_schema=whether_val)
def whether(location: str, units: str = "celsius"):
    """Get the weather for a location."""
    return whether_fn(location, units)


@tool("websearch", args_schema=websearch_val)
def websearch(query: str):
    """Perform a web search and return the results."""
    return websearch_fn(query)


tools = [
    caliculator,
    whether,
    websearch,
]


checkpoint = InMemorySaver()


agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=checkpoint,
)


config = {
    "configurable": {
        "thread_id": "vamsi-session",
    }
}


while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        break

    if not user_input:
        continue

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        },
        config=config,
    )

    print("Nova:", result["messages"][-1].content)