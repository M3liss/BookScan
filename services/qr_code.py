import requests
import base64
import json


OLLAMA_URL = "http://localhost:11434/api/generate"


def detect_books(image_path):

    with open(image_path, "rb") as f:
        image = base64.b64encode(
            f.read()
        ).decode()


    prompt = """
Identify all visible books in this image.

Return ONLY JSON:

[
 {
   "title": "",
   "author": ""
 }
]
"""


    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "moondream",
            "prompt": prompt,
            "images": [image],
            "stream": False
        }
    )


    output = response.json()["response"]

    return parse_json(output)



def parse_json(text):

    start = text.find("[")
    end = text.rfind("]")

    if start >= 0 and end >= 0:
        return json.loads(
            text[start:end+1]
        )

    return []


books = detect_books(
    "static/photo_2026-07-25_14-48-22.jpg"
)

print(books)