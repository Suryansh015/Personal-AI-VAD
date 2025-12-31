import requests
import os

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

def generate_gemini(prompt: str):
    headers = {
        "x-goog-api-key": GEMINI_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    resp = requests.post(GEMINI_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()
