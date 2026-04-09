import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

def send_message(contents):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents
    )
    return response.text

contents = [
    {"role": "user", "parts": [{"text": "Hi, my name is John and my favorite color is Blue."}]},
    {"role": "model", "parts": [{"text": "Hello John! Good to know."}]},
    {"role": "user", "parts": [{"text": "What is my favorite color?"}]}
]

print(send_message(contents))
