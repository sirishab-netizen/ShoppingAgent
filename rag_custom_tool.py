"""
Option B — RAG via custom tool + vector DB (e.g. Supabase pgvector).
The agent calls search_catalog; your app handles the event and returns results.
Best for large catalogs (10k+ products) needing semantic search.
"""
import anthropic
import os
import threading

AGENT_ID       = "ag_01JWjUBKoYhEJJsRELj6sDhy"
ENVIRONMENT_ID = "env_016HGLSDVUwcYY3kLgLK44gu"

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
BETAS = ["managed-agents-2026-04-01"]

# ── Agent with custom search_catalog tool ─────────────────────────────────────
# Run once to create a RAG-enabled variant of the agent.
def create_rag_agent():
    agent = client.beta.agents.create(
        name="Shopping Agent (RAG)",
        model="claude-sonnet-4-6",
        system=(
            "You are a helpful shopping assistant. A product catalog is searchable via the "
            "search_catalog tool — always call it before using web_search. "
            "Combine catalog results with live web prices to give complete recommendations."
        ),
        tools=[
            {"type": "agent_toolset_20260401"},
            {
                "type": "custom",
                "name": "search_catalog",
                "description": (
                    "Semantic search over the internal product catalog. "
                    "Returns the top matching products for a query."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query, e.g. 'noise-cancelling headphones under $200'",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default 5)",
                        },
                    },
                    "required": ["query"],
                },
            },
        ],
        betas=BETAS,
    )
    print(f"RAG agent created: {agent.id}")
    return agent.id


# ── Stub: replace with your real vector DB call ───────────────────────────────
def vector_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Replace this with a real vector search, e.g.:
        embeddings = openai.embeddings.create(input=query, model="text-embedding-3-small")
        results = supabase.rpc("match_products", {"query_embedding": embeddings, "match_count": top_k})
    """
    return [
        {"name": "Sony WH-1000XM5", "price": "$279", "rating": 4.8, "category": "headphones"},
        {"name": "Anker Q45",        "price": "$56",  "rating": 4.5, "category": "headphones"},
    ]


# ── Event loop with custom tool handling ─────────────────────────────────────
def stream_with_tool_handling(session_id: str):
    with client.beta.sessions.events.stream(session_id=session_id, betas=BETAS) as stream:
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if hasattr(block, "text"):
                        print(f"\nAgent: {block.text}", flush=True)

            elif event.type == "agent.custom_tool_use" and event.name == "search_catalog":
                print(f"[catalog search] query='{event.input['query']}'", flush=True)
                results = vector_search(
                    event.input["query"],
                    event.input.get("top_k", 5),
                )
                client.beta.sessions.events.send(
                    session_id=session_id,
                    events=[{
                        "type": "user.custom_tool_result",
                        "custom_tool_use_id": event.id,
                        "content": [{"type": "text", "text": str(results)}],
                        "is_error": False,
                    }],
                    betas=BETAS,
                )

            elif event.type == "session.error":
                print(f"\n[Error] {event}", flush=True)
            elif event.type == "session.status_idle":
                break


if __name__ == "__main__":
    from shopping_agent import send_message

    # Swap in your RAG agent ID here after running create_rag_agent() once
    RAG_AGENT_ID = AGENT_ID

    session = client.beta.sessions.create(
        agent=RAG_AGENT_ID,
        environment_id=ENVIRONMENT_ID,
        title="Shopping Session (RAG - Vector DB)",
        betas=BETAS,
    )
    print(f"Session started: {session.id}")
    print("Shopping Agent (vector search mode) ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            client.beta.sessions.archive(session.id, betas=BETAS)
            print("Session archived. Goodbye!")
            break
        if user_input:
            done = threading.Event()
            t = threading.Thread(
                target=lambda: (stream_with_tool_handling(session.id), done.set()),
                daemon=True,
            )
            t.start()
            send_message(session.id, user_input)
            done.wait()
