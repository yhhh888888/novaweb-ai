from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from datetime import datetime

app = FastAPI()

LLM_URL = "http://172.29.176.1:1234/api/v1/chat"

MODEL_NAME = "google/gemma-3-4b"

EXPORT_FOLDER = "exports"

if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {
        "status": "AI Website Generator Running"
    }

@app.post("/generate")
def generate_site(data: PromptRequest):

    full_prompt = f"""
Create a visually stunning futuristic responsive website.

USER REQUEST:
{data.prompt}

RULES:
- Return ONLY raw HTML
- Include inline CSS
- Include inline JS if needed
- No markdown
- No explanations
"""

    payload = {
        "model": MODEL_NAME,
        "input": full_prompt
    }

    try:

        response = requests.post(
            LLM_URL,
            json=payload,
            timeout=120
        )

        result = response.json()

        generated_html = str(result)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"{EXPORT_FOLDER}/website_{timestamp}.html"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(generated_html)

        return {
            "success": True,
            "file": filename,
            "html": generated_html
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }