import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

load_dotenv(find_dotenv())
# We initialize the Gemini client. It requires the API key explicitly sometimes.
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found. Please check your .env file!")
client = genai.Client(api_key=api_key)
gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")

def send_message(contents):
    """Sends a message or a list of messages (history) to Gemini and returns the text response."""
    response = client.models.generate_content(
        model=gemini_model,
        contents=contents
    )
    return response.text

print("========================================")
print(" EXERCISE 1: THE PROBLEM (NO CONTEXT)")
print("========================================")
print("Try telling the AI your name, and then ask it what your name is on the next prompt!")
print("Type 'exit' to move to the next part.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    
    # Sending just the new question (no context)
    response = send_message(user_input)
    print(f"Gemini: {response}\n")

print("\nNotice how Gemini forgot things from earlier in the conversation!")

print("========================================")
print(" EXERCISE 1: THE SOLUTION (ADD CONTEXT)")
print("========================================")
print("Type 'exit' to quit.\n")

# We will store the history in this list.
chat_history = []

while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break

    # TODO: Append the user's input to the `chat_history` list BEFORE sending it to the API.
    # Format for a message dictionary:
    # {"role": "user", "parts": [{"text": user_input}]}
    
    # --- YOUR CODE HERE ---
    
    
    # ----------------------

    if len(chat_history) > 0:
        response = send_message(chat_history)
        print(f"Gemini: {response}\n")
        
        # TODO: Append the AI's response to `chat_history` so it remembers its own answers!
        # Use `"role": "model"` and pass the `response` variable string.
        # --- YOUR CODE HERE ---
        
        
        # ----------------------
    else:
        print("Please complete the TODOs to see context in action!")
        break
