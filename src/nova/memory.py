import re
import os
import sqlite3
from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
from langchain.tools import tool,ToolRuntime
from pydantic import BaseModel

@dataclass
class UserContext:
    user_id:str


MEMORY_DB_PATH = Path(
    os.getenv(
        "NOVA_MEMORY_DB",
        str(Path(__file__).resolve().parents[2] / "nova_memory.sqlite3"),
    )
)


def _connect_memory_db():
    MEMORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(MEMORY_DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            PRIMARY KEY (user_id, category)
        )
        """
    )
    return connection


def _save_memory(category: str, content: str, runtime: ToolRuntime[UserContext]) -> str:
    category = category.strip().lower().replace(" ", "_")
    content = content.strip()

    if not category or not content:
        return "Category and content cannot be empty."

    if len(category) > 80 or len(content) > 1000:
        return "Memory is too long."

    with closing(_connect_memory_db()) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO memories (user_id, category, content)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, category)
                DO UPDATE SET content = excluded.content
                """,
                (runtime.context.user_id, category, content),
            )

    return f"Successfully saved memory under category '{category}'."


@tool("save_memory")
def save_memory(
    category: str,
    content: str,
    runtime: ToolRuntime[UserContext],
) -> str:
    """
    Save an important user fact or preference.

    Use a descriptive category such as:
    name, education, preferences, or projects.

    Saving the same category again updates its existing value.
    """

    return _save_memory(category, content, runtime)


class _SaveMem0Args(BaseModel):
    content: str
    category: str = "name"


@tool("save_mem0", args_schema=_SaveMem0Args)
def save_mem0(
    category: str,
    content: str,
    runtime: ToolRuntime[UserContext],
) -> str:
    """Compatibility alias for saving the user's name; category defaults to name."""

    return _save_memory(category, content, runtime)


def _search_memory(query: str, runtime: ToolRuntime[UserContext]) -> str:
    with closing(_connect_memory_db()) as connection:
        rows = connection.execute(
            "SELECT category, content FROM memories WHERE user_id = ?",
            (runtime.context.user_id,),
        ).fetchall()

    memories = [
        {"category": category, "content": content}
        for category, content in rows
    ]

    if not memories:
        return "No saved memories found."

    # Simple lexical relevance ranking.
    # This is not semantic/vector search.
    query_words = set(re.findall(r"\w+", query.lower()))

    def relevance(memory):
        content = memory["content"].lower()
        category = memory["category"].lower()

        words = set(re.findall(r"\w+", content + " " + category))
        return len(query_words & words)
      

    memories = sorted(
        memories,
        key=relevance,
        reverse=True,
    )

    results = []

    for memory in memories[:10]:
        results.append(
            f"Category: {memory['category']}\n"
            f"Information: {memory['content']}"
        )

    return "\n\n".join(results)


@tool("search_memory")
def search_memory(
    query: str,
    runtime: ToolRuntime[UserContext],
) -> str:
    """Search the user's previously saved long-term memories."""

    return _search_memory(query, runtime)


@tool("search_mem0")
def search_mem0(
    query: str,
    runtime: ToolRuntime[UserContext],
) -> str:
    """Compatibility alias for searching the user's saved memories."""

    return _search_memory(query, runtime)






