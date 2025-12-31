import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_llm(system_prompt: str, user_prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.4,
        "max_tokens": 400,
        "stream": False
    }

    response = requests.post(GROQ_URL, json=payload, headers=headers)

    # Helpful debug if it fails again
    if response.status_code != 200:
        print("Groq error:", response.text)

    response.raise_for_status()
    return response.json()
