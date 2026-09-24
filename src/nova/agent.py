import os

from dotenv import load_dotenv
from groq import Groq

from nova.tools.caliculator import caliculator
from nova.tools.whether import whether
from nova.tools.websearch import websearch

from nova.schemas.tools import (
    caliculator_val,
    whether_val,
    websearch_val,
    caliculator_output,
    whether_output,
    websearch_output
)


load_dotenv()


tools = [
    {
        "type": "function",
        "function": {
            "name": "caliculator",
            "description": "Use this tool whenever the user asks you to calculate, multiply, divide, add, subtract, or evaluate a mathematical expression. Do not calculate arithmetic yourself.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate."
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "whether",
            "description": "Use this tool whenever the user asks you about the weather in a specific location. Do not provide weather information yourself.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location for which to retrieve weather information."
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "websearch",
            "description": "Use this tool whenever the user asks you to search for information on the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to use for the web search."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


tools_map = {
    "caliculator": caliculator,
    "whether": whether,
    "websearch": websearch,
}


validation_map = {
    "caliculator": caliculator_val,
    "whether": whether_val,
    "websearch": websearch_val,
}
output_validation_map = {
    "caliculator": caliculator_output,
    "whether": whether_output,
    "websearch": websearch_output
}

SYSTEM_PROMPT = """
You are Nova, an AI agent that uses tools to complete tasks.

Tool usage rules:

1. ALWAYS use the caliculator tool for arithmetic.
   Never perform arithmetic yourself, even if the calculation is simple.

2. ALWAYS use the whether tool for weather requests.
   Never provide weather information from your own knowledge.

3. ALWAYS use the websearch tool when the user explicitly asks
   you to search, look up, or verify something on the web.

For multi-step tasks:
- determine the next appropriate action
- use the appropriate tool
- inspect the tool result
- continue until the user's goal is completed.

Do not stop until the user's goal is completed.
"""


client = Groq(api_key=os.getenv("GROQ_API_KEY"))