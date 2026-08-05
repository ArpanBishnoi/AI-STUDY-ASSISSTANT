import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)
def generate_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
        input=text,
    )
    return response.data[0].embedding

