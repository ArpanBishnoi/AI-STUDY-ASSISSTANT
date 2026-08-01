import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)


def generate_response(prompt: str):
    response = client.chat.completions.create(
        model="poolside/laguna-xs-2.1:free",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content