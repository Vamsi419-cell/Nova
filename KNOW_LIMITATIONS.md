# Nova v1.0 — Known Limitations

Nova v1.0 is a learning-focused AI agent and is not yet production-ready. The following are known limitations of the current implementation.

## 1. Web Search Is Currently a Stub

The web-search tool does not perform a real internet search yet. It currently uses predefined responses for testing tool-calling and multi-step agent behavior.

As a result, Nova cannot reliably retrieve current information from the web.

## 2. Tool Selection Depends on the LLM

The agent relies on the language model to decide when and which tool to call.

If the model incorrectly decides not to use a tool, or selects an inappropriate tool, Nova may produce an incorrect answer even though the tool itself works correctly.

## 3. Raw Nova Does Not Persist Conversation Memory

The raw implementation creates a new message history for every call to `run_agent()`.

Therefore, previous turns are not automatically available to the raw agent across separate interactions.

The LangChain implementation addresses this within a session using `InMemorySaver`, but that memory is temporary and is lost when the process exits.

## 4. Conversation Context Can Grow

The LangChain implementation stores conversation messages in the agent state.

As a conversation becomes longer, the amount of context sent to the model can increase, leading to higher token usage and potentially less room for new responses.

There is currently no summarization or long-term memory strategy.

## 5. Limited Evaluation

Nova currently has only basic unit testing for the calculator tool.

There is no systematic evaluation dataset for measuring tool-selection accuracy, task completion, response quality, or failure recovery.

A future version should introduce an evaluation set covering single-tool tasks, multi-step tasks, incorrect inputs, tool failures, and ambiguous requests.
