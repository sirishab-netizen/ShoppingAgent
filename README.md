# 🛍️ Claude Shopping Agent

An AI-powered shopping assistant built with Anthropic's Managed Agents API.

## What it does
- Searches the web for real-time product prices and reviews
- Compares products against a local product catalog (RAG)
- Maintains conversation history across a session

## Architecture decisions
| Decision | Options considered | Choice & why |
|---|---|---|
| Product data retrieval | File upload vs vector DB | File upload — catalog <10k products, no infra overhead |
| Web search | Always-on vs on-demand | Always-on via agent_toolset — ensures fresh pricing |

## Tech stack
- [Anthropic Python SDK](https://github.com/anthropic/anthropic-sdk-python)
- Claude Sonnet 4.6 (claude-sonnet-4-6)
- Managed Agents API (sessions, environments, vaults)

## Setup
\`\`\`bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key
python agent_setup.py   # run once
python shopping_agent.py
\`\`\`

## Key learnings
- Agentic workflow design (tool selection, permission policies)
- RAG architecture tradeoffs for product catalog search
- Streaming event handling with session lifecycle management
