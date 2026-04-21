"""
Run this ONCE to create your agent and environment.
Save the printed IDs — paste them into shopping_agent.py and the RAG files.
"""
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
BETAS = ["managed-agents-2026-04-01"]

agent = client.beta.agents.create(
    name="Shopping Agent",
    model="claude-sonnet-4-6",
    description="An AI-powered shopping assistant that searches the web and a local product catalog.",
    system=(
        "You are a helpful shopping assistant. Help users find products, compare prices across "
        "retailers, track deals and discounts, build and manage shopping lists, and make informed "
        "purchase decisions. When researching products, use web search to find current prices, "
        "reviews, and availability. Summarize key specs, pros/cons, and price differences clearly. "
        "Always flag the best value options and note any significant deals or coupons. "
        "If a product catalog is available at /workspace/catalog.csv, always search it first "
        "before using web_search. Use the read tool to load it, then filter by the user's criteria."
    ),
    tools=[{"type": "agent_toolset_20260401"}],
    betas=BETAS,
)

environment = client.beta.environments.create(
    name="shopping-agent-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
    betas=BETAS,
)

print("=== Save these IDs ===")
print(f"AGENT_ID       = \"{agent.id}\"")
print(f"ENVIRONMENT_ID = \"{environment.id}\"")
