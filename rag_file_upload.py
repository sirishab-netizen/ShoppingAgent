"""
Option A — RAG via file upload.
Uploads a product catalog CSV and mounts it into the session container.
Best for catalogs under ~10k rows.
"""
import anthropic
import os

AGENT_ID       = "ag_01JWjUBKoYhEJJsRELj6sDhy"
ENVIRONMENT_ID = "env_016HGLSDVUwcYY3kLgLK44gu"
CATALOG_PATH   = "sample_catalog.csv"

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
BETAS = ["managed-agents-2026-04-01", "files-api-2025-04-14"]


def upload_catalog(path: str) -> str:
    """Upload catalog and return file_id. Run once; reuse the ID across sessions."""
    with open(path, "rb") as f:
        file = client.beta.files.upload(
            {"file": (os.path.basename(path), f, "text/csv")},
            betas=BETAS,
        )
    print(f"Catalog uploaded: {file.id}")
    return file.id


def create_session_with_catalog(file_id: str):
    return client.beta.sessions.create(
        agent=AGENT_ID,
        environment_id=ENVIRONMENT_ID,
        title="Shopping Session (RAG - File Upload)",
        resources=[{
            "type": "file",
            "file_id": file_id,
            "mount_path": "/workspace/catalog.csv",
        }],
        betas=BETAS,
    )


if __name__ == "__main__":
    import threading
    from shopping_agent import send_message, stream_response

    file_id = upload_catalog(CATALOG_PATH)
    session = create_session_with_catalog(file_id)
    print(f"Session started: {session.id}")
    print("Shopping Agent (catalog mode) ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            client.beta.sessions.archive(session.id, betas=["managed-agents-2026-04-01"])
            print("Session archived. Goodbye!")
            break
        if user_input:
            done = threading.Event()
            t = threading.Thread(target=lambda: (stream_response(session.id), done.set()), daemon=True)
            t.start()
            send_message(session.id, user_input)
            done.wait()
