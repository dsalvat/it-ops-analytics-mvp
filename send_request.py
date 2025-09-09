import requests
import json

url = "http://localhost:8000/api/v1/llm/generate?platform=Gemini&model=gemini-1.5-flash-latest&language=English&week=36&year=2025"

with open("C:/Users/User/Projects/it-ops-analytics-mvp/data.json", "r") as f:
    data = json.load(f)

headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.json())
