# Nova v2.0 — Known Limitations

Nova v2.0 is an evolving AI agent designed to explore agent orchestration, tool execution, memory management, middleware, and document processing. Although several capabilities have been implemented, the system is not yet production-ready.

The following limitations are currently known.

## 1. Web Search Reliability

The web-search tool has been integrated into the agent, but its implementation and reliability still need to be evaluated.

Nova relies on the language model to formulate search queries and interpret returned results. Search quality, source reliability, and handling of outdated information have not yet been systematically evaluated.

## 2. Tool Selection Depends on the LLM

The agent relies on the language model to decide when and which tool to call.

If the model incorrectly decides not to use a tool, selects an inappropriate tool, or generates invalid tool arguments, Nova may produce an incorrect answer even when the underlying tool works correctly.

## 3. Conversation Persistence Is Limited

The LangChain implementation uses LangGraph's `InMemorySaver` to maintain conversation state across interactions within a session.

However, checkpoint data exists only in process memory and is lost when Nova terminates or restarts.

Long-term user memories are stored separately in a local SQLite database and persist across application restarts.

The raw implementation does not automatically preserve conversation history across separate calls to `run_agent()`.

## 4. Conversation Context Can Grow

The LangChain implementation stores conversation messages in agent state.

Summarization middleware has been introduced to manage growing conversation histories by summarizing older messages and retaining recent context.

However, summarization can potentially discard details that become relevant later. Its effectiveness and impact on long-running conversations require further evaluation.

## 5. Limited Long-Term Memory Retrieval

Nova supports persistent user-specific memories through SQLite.

Memory retrieval currently uses simple lexical keyword matching rather than semantic similarity.

Consequently, queries with different wording but similar meaning may fail to retrieve relevant memories.

The current database also supports only one memory per user per category, meaning that saving another memory under the same category overwrites the previous entry.

## 6. Incomplete Safety and Approval Workflow

Human-in-the-loop middleware has been configured for sensitive tool execution, particularly email sending.

However, the CLI still needs a complete approval, rejection, editing, and interruption-resumption workflow.

PII middleware has not yet been integrated into the agent.

## 7. Structured Output Is Not Yet Integrated

The agent currently supports structured schemas for individual tools, but a general structured response mechanism has not yet been integrated into the agent.

A future implementation should support validated structured responses using Pydantic schemas where appropriate.

## 8. Limited Evaluation and Testing

Nova currently has basic unit testing for the calculator tool.

There is no systematic evaluation dataset for measuring:

- Tool-selection accuracy.
- Multi-step task completion.
- Memory retrieval accuracy.
- Response quality.
- Middleware behavior.
- Failure recovery and interruption handling.
- Streaming correctness.

A future version should introduce an evaluation suite covering these scenarios.

## 9. Document Ingestion Is Not Yet Implemented

Nova does not currently have a dedicated document ingestion pipeline.

It cannot reliably process domain-specific formats such as structured notebooks, PDFs containing complex tables, or HTML documents with nested structures.

Custom document loaders and structure-aware text splitters are planned for the next development phase.

## 10. Model Reliability and Fallback

Retry and fallback model configurations have been defined, but the agent currently uses the primary model directly.

Therefore, automatic recovery from model failures through the configured fallback model is not yet active.

## 11. Limited Deployment and Scalability

Nova currently operates primarily as a local CLI application.

Its in-memory checkpointing, local SQLite storage, and single-process execution model are intended for development and experimentation rather than concurrent production workloads.

Future improvements should introduce persistent checkpoint storage, better service boundaries, and appropriate concurrency and authentication mechanisms.
