
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    SummarizationMiddleware,
    before_model,
)
from langgraph.checkpoint.memory import InMemorySaver

from nova.tools.caliculator import caliculator as caliculator_fn
from nova.tools.whether import whether as whether_fn
from nova.tools.websearch import websearch as websearch_fn
from nova.tools.send_email import send_email as send_email_fn

from nova.schemas.tools import (
    caliculator_val,
    whether_val,
    websearch_val,
    caliculator_output,
    whether_output,
    websearch_output,
)

from nova.memory import (
    UserContext,
    save_memory,
    save_mem0,
    search_memory,
    search_mem0,
)


load_dotenv()


# --------------------------------------------------
# 1. Models
# --------------------------------------------------

model = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=500,
)

fallback_model = ChatGroq(
    model="qwen/qwen3.8-27",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=500,
)

# Configured for retry and fallback.
# Currently not used by the agent.
reliable_model = model.with_retry().with_fallbacks([fallback_model])


# --------------------------------------------------
# 2. Tools
# --------------------------------------------------

@tool("send_email")
def send_email(to: str, subject: str, body: str):
    """Send an email to the recipient."""
    return send_email_fn(to, subject, body)


@tool("caliculator", args_schema=caliculator_val)
def caliculator(expression: str):
    """Evaluate a mathematical expression."""
    return caliculator_output(
        result=caliculator_fn(expression)
    )


@tool("whether", args_schema=whether_val)
def whether(location: str, units: str = "celsius"):
    """Get the weather for a location."""
    return whether_output(
        result=whether_fn(location, units)
    )


@tool("websearch", args_schema=websearch_val)
def websearch(query: str):
    """Search the web for information."""
    return websearch_output(
        result=websearch_fn(query)
    )


# --------------------------------------------------
# 3. Middleware
# --------------------------------------------------

@before_model
def log_model_call(state, runtime):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"\n[{timestamp}] Model call initiated\n",
        flush=True,
    )

    return None


summarization = SummarizationMiddleware(
    model=model,
    trigger=("messages", 12),
    keep=("messages", 6),
)


hitl_middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email": True,
    },
    description_prefix="Email approval required",
)


# --------------------------------------------------
# 4. System Prompt
# --------------------------------------------------

system_prompt = """
You are Nova, a helpful personal AI assistant.

You have access to long-term memory through two tools:
- save_memory (also available as save_mem0)
- search_memory (also available as search_mem0)

MEMORY RULES:

1. Proactively save useful, stable information about the user,
   including preferences, identity details voluntarily shared,
   ongoing projects and recurring goals.

2. If the user explicitly asks you to remember something,
   save it using save_memory or save_mem0.

3. Do not save every message. Avoid temporary information,
   random conversation details, credentials or sensitive data.

4. Before answering questions about the user's past preferences,
   identity or previously shared information, use search_memory
   or search_mem0.

5. If the user corrects previously saved information,
   save the corrected information using the same category.

6. Never claim that something was saved unless the tool
   successfully confirms it.

7. Never invent memories. If you cannot find relevant information,
   say that you don't have it.

8. Memories belong to the current user.
   Never mix information between different users.
"""


# --------------------------------------------------
# 5. Agent
# --------------------------------------------------

agent = create_agent(
    model=model,
    tools=[
        caliculator,
        whether,
        websearch,
        send_email,
        save_memory,
        save_mem0,
        search_memory,
        search_mem0,
    ],
    checkpointer=InMemorySaver(),
    middleware=[
        hitl_middleware,
        log_model_call,
        summarization,
    ],
    system_prompt=system_prompt,
    context_schema=UserContext,
)


# --------------------------------------------------
# 6. User Context and Conversation Configuration
# --------------------------------------------------

user_context = UserContext(user_id="vamsi")

thread_number = 1

config = {
    "configurable": {
        "thread_id": f"vamsi-session-{thread_number}"
    }
}


# --------------------------------------------------
# 7. CLI Streaming
# --------------------------------------------------

while True:

    try:
        user_input = input("You: ").strip()

    except (KeyboardInterrupt, EOFError):
        print("\nNova session ended.")
        break

    if user_input.lower() in {"exit", "quit"}:
        break

    if user_input.lower() == "/new":

        thread_number += 1

        config = {
            "configurable": {
                "thread_id": f"vamsi-session-{thread_number}"
            }
        }

        print(f"\nStarted new conversation: {thread_number}\n")
        continue

    if not user_input:
        continue

    print("\nNova: ", end="", flush=True)

    try:

        for mode, chunk in agent.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            },
            config=config,
            context=user_context,
            stream_mode=["messages", "updates"],
        ):

            # ------------------------------------------
            # A. MESSAGE STREAMING
            # ------------------------------------------

            if mode == "messages":

                message_chunk, metadata = chunk

                node = metadata.get("langgraph_node")

                # Tool execution result
                if node == "tools":

                    tool_name = getattr(
                        message_chunk,
                        "name",
                        "unknown",
                    )

                    status = getattr(
                        message_chunk,
                        "status",
                        None,
                    )

                    if status == "error":

                        print(
                            f"\n[Tool failed: {tool_name}]",
                            flush=True,
                        )

                        print(
                            f"Error: {message_chunk.content}",
                            flush=True,
                        )

                    else:

                        print(
                            f"\n[Tool completed: {tool_name}]",
                            flush=True,
                        )

                # Assistant response tokens
                elif node == "model":

                    if isinstance(message_chunk.content, str):

                        print(
                            message_chunk.content,
                            end="",
                            flush=True,
                        )


            # ------------------------------------------
            # B. GRAPH UPDATES
            # ------------------------------------------

            elif mode == "updates":

                for node, update in chunk.items():

                    if node == "model":

                        for message in update.get("messages", []):

                            for tool_call in getattr(
                                message,
                                "tool_calls",
                                [],
                            ):

                                print(
                                    f"\n[Calling {tool_call['name']}...]",
                                    flush=True,
                                )

        print("\n")

    # ----------------------------------------------
    # C. EXCEPTIONS THAT ESCAPE THE AGENT
    # ----------------------------------------------

    except Exception as exc:

        print(
            f"\n[Nova encountered an error: {exc}]\n",
            flush=True,
        )
