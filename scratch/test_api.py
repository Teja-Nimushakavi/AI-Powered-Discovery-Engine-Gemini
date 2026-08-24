import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "http://127.0.0.1:8000/api/v1/query"
payload = {"query": "What are the common issues with the app?"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)
