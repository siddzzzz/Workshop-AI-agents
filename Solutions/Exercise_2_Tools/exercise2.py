import os
import re
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

load_dotenv(find_dotenv())

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found. Please check your .env file!")
client = genai.Client(api_key=api_key)
gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")

# ---------------------------------------------------------
# 1. DEFINE OUR TOOLS
# ---------------------------------------------------------
def calculator(expression):
    """A tool that evaluates basic math expressions."""
    print(f"\n[TOOL EXECUTION] Calculating: {expression}")
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating: {e}"

def read_file(filename):
    print(f"\n[TOOL EXECUTION] Reading file: {filename}")
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# ---------------------------------------------------------
# 2. CREATE SYSTEM PROMPT WITH XML INSTRUCTIONS
# ---------------------------------------------------------
SYSTEM_PROMPT = """You are an AI assistant that can use tools. 
When the user asks you to do something that requires a tool, output exactly this XML format and NOTHING else:

<tool_call>
<name>tool_name</name>
<arguments>tool_arguments</arguments>
</tool_call>

Tools available:
1. name: calculator
   description: Evaluates math expressions.
   arguments: A valid math string (e.g. "3 * 4").
   
2. name: read_file
   description: Reads the content of a file.
   arguments: The name of the file to read (e.g. "secret.txt").
"""

def parse_and_execute_tool(response_text):
    """A simple parser that looks for <tool_call> tags and executes the python function."""
    match = re.search(r"<tool_call>.*?<name>(.*?)</name>.*?<arguments>(.*?)</arguments>.*?</tool_call>", response_text, re.DOTALL)
    
    if match:
        tool_name = match.group(1).strip()
        tool_args = match.group(2).strip()
        
        print(f"[PARSER] Found tool request: {tool_name} with args '{tool_args}'!")
        
        if tool_name == "calculator":
            return calculator(tool_args)
        elif tool_name == "read_file":
            return read_file(tool_args)
        else:
            return f"Error: Tool '{tool_name}' not recognized."
    else:
        return None # No tool requested

# ---------------------------------------------------------
# 3. INTERACT WITH THE AI
# ---------------------------------------------------------
if __name__ == "__main__":
    # Let's create a test file for our read_file tool
    with open("secret.txt", "w") as f:
        f.write("The secret password is: AgenticAI_2026")

    print("\n========================================")
    print(" EXERCISE 2: TOOL USAGE")
    print("========================================")
    print("You can ask me to calculate things!")
    print("You can also ask me to read a file, e.g. 'secret.txt'.")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_prompt = input("You: ")
        if user_prompt.lower() == 'exit':
            break

        response = client.models.generate_content(
            model=gemini_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0  # Use low temperature for more predictable tool calls
            )
        )
        
        print("AI Raw Response:")
        print(response.text)
        
        # Check if AI used a tool
        tool_result = parse_and_execute_tool(response.text)
        if tool_result:
            print(f"[TOOL RESULT] {tool_result}\n")
        else:
            print("[INFO] No tool executed by the AI.\n")
