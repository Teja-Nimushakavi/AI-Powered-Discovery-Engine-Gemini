import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key available: {bool(api_key)}")

client = genai.Client(api_key=api_key)
print("Available models:")
try:
    models = client.models.list()
    for m in models:
        print(m.name)
except Exception as e:
    print("Error:", e)
