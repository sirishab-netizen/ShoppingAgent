"""
Main chat loop — reuses the agent and environment created in agent_setup.py.
"""
import anthropic
import os
import threading

AGENT_ID       = "ag_01JWjUBKoYhEJJsRELj6sDhy"
ENVIRONMENT_ID = "env_016HGLSDVUwcYY3kLgLK44gu"

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
BETAS = ["managed-agents-2026-04-01"]


def create_session(resources=None):
    return client.beta.sessions.create(
        agent=AGENT_ID,
        environment_id=ENVIRONMENT_ID,
        title="Shopping Session",
        resources=resources or [],
        betas=BETAS,
    )


def send_message(session_id: str, text: str):
    client.beta.sessions.events.send(
        session_id=session_id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
        betas=BETAS,
    )


def stream_response(session_id: str):
    """Stream events until the agent goes idle."""
    with client.beta.sessions.events.stream(session_id=session_id, betas=BETAS) as stream:
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if hasattr(block, "text"):
                        print(f"\nAgent: {block.text}", flush=True)
            elif event.type == "session.error":
                print(f"\n[Error] {event}", flush=True)
            elif event.type == "session.status_idle":
                break


def chat(session_id: str, user_input: str):
    """Open stream in background, then send message."""
    done = threading.Event()

    def _stream():
        stream_response(session_id)
        done.set()

    t = threading.Thread(target=_stream, daemon=True)
    t.start()
    send_message(session_id, user_input)
    done.wait()


if __name__ == "__main__":
    session = create_session()
    print(f"Session started: {session.id}")
    print("Shopping Agent ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            client.beta.sessions.archive(session.id, betas=BETAS)
            print("Session archived. Goodbye!")
            break
        if user_input:
            chat(session.id, user_input)
