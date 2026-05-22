import requests
import gradio as gr

URL = "http://127.0.0.1:1234/api/v1/chat"

def generate(prompt):

    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(URL, json=payload)

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        elif "message" in data:
            return data["message"]

        elif "content" in data:
            return data["content"]

        else:
            return str(data)

    except Exception as e:
        return str(e)

demo = gr.Interface(
    fn=generate,

    inputs=gr.Textbox(
        lines=5,
        placeholder="Enter your prompt here..."
    ),

    outputs="text",

    title="AI Booster",

    description="Local AI Prompt Generator"
)

demo.launch()