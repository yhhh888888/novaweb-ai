from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import requests
import os
from datetime import datetime

# =========================================
# APP CONFIG
# =========================================

app = FastAPI()

LLM_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_NAME = "llama-3.3-70b-versatile"

API_KEY = os.getenv("GROQ_API_KEY")

GENERATED_FOLDER = "generated_sites"

# =========================================
# FOLDERS
# =========================================

os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# =========================================
# TEMPLATES
# =========================================

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# =========================================
# HOME
# =========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# =========================================
# GENERATE WEBSITE
# =========================================

@app.post("/generate", response_class=HTMLResponse)
async def generate_website(
    request: Request,
    prompt: str = Form(...)
):

    full_prompt = f"""
Create a beautiful modern responsive landing page.

Website idea:
{prompt}

Requirements:
- Return ONLY raw HTML
- Include inline CSS
- Responsive design
- Modern UI
- No markdown
- No explanations
"""

    try:

        response = requests.post(

            LLM_URL,

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            },

            timeout=120

        )

        # =========================================
        # CHECK RESPONSE
        # =========================================

        resp_json = response.json()

        # DEBUG PRINT
        print(resp_json)

        # =========================================
        # SAFE EXTRACTION
        # =========================================

        generated_html = ""

        if (
            "choices" in resp_json
            and len(resp_json["choices"]) > 0
        ):

            generated_html = (
                resp_json["choices"][0]
                ["message"]["content"]
            )

        else:

            generated_html = f"""
            <html>
            <body style="background:#111;color:white;font-family:Arial;padding:40px;">
                <h1>Generation Error</h1>
                <pre>{resp_json}</pre>
            </body>
            </html>
            """

        # =========================================
        # SAVE GENERATED FILE
        # =========================================

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"{GENERATED_FOLDER}/site_{timestamp}.html"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(generated_html)

        return HTMLResponse(
            content=generated_html
        )

    except Exception as e:

        return HTMLResponse(
            content=f"""
            <html>
            <body style="background:#111;color:white;font-family:Arial;padding:40px;">
                <h1>Server Error</h1>
                <pre>{str(e)}</pre>
            </body>
            </html>
            """
        )

# =========================================
# HEALTH CHECK
# =========================================

@app.get("/health")
async def health():

    return {
        "status": "running"
    }