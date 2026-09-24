def websearch(query: str):
    """Perform a web search and return the results."""
    query = query.lower()

    if "ertyuio" in query and "population" in query:
        return "The population of ertyuio is 1000."

    return f"Searched the web for: {query}"