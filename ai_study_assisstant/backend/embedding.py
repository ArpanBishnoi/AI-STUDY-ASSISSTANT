import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
print(API_KEY := os.getenv("OPEN_ROUTER_API_KEY"))
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)
def generate_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

