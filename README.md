# Nova v1.0

Nova is a CLI-based AI research assistant built to explore how tool-calling agents work. It can perform calculations, answer weather queries, and use a web-search tool to retrieve information and complete multi-step tasks.

## Features

* Tool calling with Groq's `openai/gpt-oss-20b`
* Calculator tool for arithmetic operations
* Weather tool
* Web-search tool
* Pydantic validation for tool inputs and outputs
* Error handling and iteration limits
* Interactive CLI
* LangChain implementation using `create_agent`
* Conversation memory using LangGraph's `InMemorySaver`
* Long-term user memories persisted locally in SQLite (`nova_memory.sqlite3`)
* Basic tool tests with pytest

## Architecture

Nova was implemented in two ways during development:

### Raw implementation

The raw implementation manually handles the agent loop:

```text
User
 ↓
LLM
 ↓
Tool call
 ↓
Validate arguments
 ↓
Execute tool
 ↓
Validate result
 ↓
Send result back to LLM
 ↓
Final answer
```

The main components are:

* `src/nova/agent.py` — model, tool definitions, and agent configuration
* `src/nova/loop.py` — hand-written agent execution loop
* `src/nova/schemas/tools.py` — Pydantic schemas
* `src/nova/tools/` — tool implementations

### LangChain implementation

`langchain_test.py` provides a separate implementation using LangChain:

```text
User
 ↓
LangChain Agent
 ↓
Tools
 ↓
Agent state / memory
 ↓
Final answer
```

It uses `@tool`, `create_agent`, and `InMemorySaver`.
User facts saved through the memory tools are stored in `nova_memory.sqlite3`
in the project root, so they remain available after restarting the CLI. Set
`NOVA_MEMORY_DB` to choose a different database path.

## Setup

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Running Nova

### Raw implementation

```bash
PYTHONPATH=src python main.py
```

### LangChain implementation

```bash
PYTHONPATH=src python langchain_test.py
```

Type `exit` or `quit` to stop the CLI.

## Testing

Run the tests with:

```bash
PYTHONPATH=src pytest
```

## What I Learned

This project was built incrementally to understand agent systems from the ground up.

Key concepts learned:

* LLM tool calling and tool schemas
* Agent execution loops
* Pydantic input and output validation
* Tool error handling
* Iteration limits
* Conversation state and memory
* LangChain's `@tool` abstraction
* LangChain agents and `create_agent`
* The difference between a hand-written agent loop and a framework-managed runtime
* Why persistent agent state and workflow orchestration become important as agents become more complex
* Basic testing and repository organization

The raw implementation was built first so that the underlying agent loop was understood before introducing framework abstractions.
