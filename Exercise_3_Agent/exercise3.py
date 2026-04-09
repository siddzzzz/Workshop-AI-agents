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
def read_file(filename):
    print(f"[TOOL] Reading file: {filename}")
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filename}: {e}"

def write_file(arguments):
    # We expect arguments in the format "filename|content"
    if "|" not in arguments:
        return "Error: arguments must be in the format 'filename|content'"
    filename, content = arguments.split("|", 1)
    print(f"[TOOL] Writing to file: {filename}")
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file {filename}: {e}"

# TODO: Add your own completely new tool here! 
# For example, you could make a `list_directory` tool, a `search_web` tool,
# or anything you can think of! 
# Step 1: Define the python function for your tool here:

# def my_custom_tool(arguments):
#    ...
#    return ...


# ---------------------------------------------------------
# 2. SYSTEM PROMPT
# ---------------------------------------------------------
# TODO: Step 2: Add your new tool to the SYSTEM_PROMPT documentation below!
SYSTEM_PROMPT = """You are an autonomous AI agent. You will be given a task, and you must use tools to complete it.
You MUST only reply with exactly ONE XML tool call at a time. The system will give you the result.
When you are done with the main task, you MUST use the 'finish' tool to provide the final answer.

Output exactly this XML format:
<tool_call>
<name>tool_name</name>
<arguments>tool_arguments</arguments>
</tool_call>

Tools available:
1. name: read_file
   description: Reads the content of a file.
   arguments: The name of the file to read (e.g. "data.txt").

2. name: write_file
   description: Writes text to a file. 
   arguments: The filename and content separated by a pipe character "|" (e.g. "output.txt|Hello World!").

3. name: finish
   description: Ends the task and provides the final answer to the user.
   arguments: A detailed summary of all the tasks you completed, what you found, and your final answer.
"""

def parse_tool_call(response_text):
    match = re.search(r"<tool_call>.*?<name>(.*?)</name>.*?<arguments>(.*?)</arguments>.*?</tool_call>", response_text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def execute_tool(tool_name, tool_args):
    if tool_name == "read_file":
        return read_file(tool_args)
    elif tool_name == "write_file":
        return write_file(tool_args)
    
    # TODO: Step 3: Add your new tool to the execute_tool routing here!
    # elif tool_name == "my_custom_tool":
    #    return my_custom_tool(tool_args)
    
    else:
        return f"Error: Tool '{tool_name}' not recognized."

# ---------------------------------------------------------
# 3. THE MAIN AGENT LOOP
# ---------------------------------------------------------
def run_agent(task_description, chat_history):
    print(f"\n[AGENT STARTED] Goal: {task_description}\n")
    
    # We maintain a conversation history from previous tasks
    chat_history.append({"role": "user", "parts": [{"text": task_description}]})

    max_steps = 10
    
    for step in range(max_steps):
        print(f"\n--- STEP {step+1} ---")
        
        # 1. Ask the AI for the next action
        response = client.models.generate_content(
            model=gemini_model,
            contents=chat_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0 
            )
        )
        
        ai_message = response.text.strip()
        print(f"\n[AI THOUGHT & ACTION]")
        print(ai_message)
        
        # Add AI's response to history
        chat_history.append({"role": "model", "parts": [{"text": ai_message}]})
        
        # 2. Parse the tool call
        tool_name, tool_args = parse_tool_call(ai_message)
        
        if not tool_name:
            error_msg = "Error: You didn't output a valid XML <tool_call>. Please format your output correctly."
            print(f"\n[SYSTEM WARNING] {error_msg}")
            chat_history.append({"role": "user", "parts": [{"text": error_msg}]})
            continue
            
        # 3. Check for finish condition
        if tool_name == "finish":
            print("\n[AGENT FINISHED] Task Complete!")
            print(f"Final Output: {tool_args}")
            break
            
        # 4. Execute the tool
        tool_result = execute_tool(tool_name, tool_args)
        print(f"\n[TOOL RESULT]\n{tool_result}")
        
        # 5. Provide tool result back to the AI
        result_message = f"Tool result for {tool_name}:\n{tool_result}"
        chat_history.append({"role": "user", "parts": [{"text": result_message}]})
        
    else:
        print("\n[AGENT ABORTED] Max steps reached without finishing.")

if __name__ == "__main__":
    # Let's create a starting file so the agent has something to do
    with open("instructions.txt", "w") as f:
        f.write("Create a file called 'greeting.txt'. Inside it, write 'Hello from the Autonomous Agent!'")
        
    print("\n========================================")
    print(" EXERCISE 3: AUTONOMOUS AGENT")
    print("========================================")
    print("You can give the agent a task, and it will use tools in a loop to figure it out.")
    print("Because it has chat history, you can follow up with 'What did you just do?'")
    print("Try asking it to read 'instructions.txt'!")
    print("Type 'exit' to quit.\n")
    
    agent_chat_history = []
    
    while True:
        task = input("Agent Task: ")
        if task.lower() == 'exit':
            break
            
        run_agent(task, agent_chat_history)
        print("\n" + "="*40 + "\n")
