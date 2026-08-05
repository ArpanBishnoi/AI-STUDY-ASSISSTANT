import os
import requests
# Free HuggingFace Inference API — same model (all-MiniLM-L6-v2) that was
# previously loaded locally, but served remotely so no RAM is consumed on Render.
HF_API_URL = (
    "https://api-inference.huggingface.co/pipeline/feature-extraction/"
    "sentence-transformers/all-MiniLM-L6-v2"
)
def generate_embedding(text: str) -> list:
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise RuntimeError(
            "HF_API_KEY environment variable is not set. "
            "Create a free token at https://huggingface.co/settings/tokens "
            "and add it as HF_API_KEY."
        )
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": text, "options": {"wait_for_model": True}}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    # The API returns token-level embeddings: shape [seq_len, 384].
    # Mean-pool across tokens to produce a single 384-dim sentence embedding.
    token_embeddings = response.json()
    num_tokens = len(token_embeddings)
    dim = len(token_embeddings[0])
    embedding = [
        sum(token_embeddings[t][i] for t in range(num_tokens)) / num_tokens
        for i in range(dim)
    ]
    return embedding

