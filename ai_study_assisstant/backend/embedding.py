import os
import requests

JINA_API_URL = "https://api.jina.ai/v1/embeddings"


def generate_embedding(text: str) -> list:
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "JINA_API_KEY environment variable is not set. "
            "Get a free key at https://jina.ai/embeddings"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "jina-embeddings-v3",
        "dimensions": 384,
        "input": [text],
    }

    response = requests.post(JINA_API_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["data"][0]["embedding"]

