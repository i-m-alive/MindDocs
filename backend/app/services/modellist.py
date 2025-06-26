import requests
import os

api_key = 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

url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

print(response.json())