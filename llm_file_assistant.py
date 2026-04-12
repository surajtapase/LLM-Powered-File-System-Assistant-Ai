import os
import json
import re
from groq import Groq
import fs_tools

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in the resumes folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "extension": {"type": "string"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read raw content of a file. Use this when user asks to read or display file content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search keyword in a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "keyword": {"type": "string"}
                },
                "required": ["filepath", "keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_summary",
            "description": "Create a summary of a resume file and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_data",
            "description": "Extract structured JSON data from resume. Use only when user asks for structured data or JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"]
            }
        }
    }
]


def call_function(name, args):
    if name == "list_files":
        return fs_tools.list_files(**args)

    elif name == "read_file":
        return fs_tools.read_file(**args)

    elif name == "search_in_file":
        return fs_tools.search_in_file(**args)

    elif name == "write_file":
        return fs_tools.write_file(**args)

    elif name == "create_summary":   # ✅ ADD THIS
        return create_summary(**args)

    elif name == "extract_data":
        return extract_data(**args)

    return {"error": "Unknown function"}

def create_summary(filepath):
    data = fs_tools.read_file(filepath)

    if not data.get("success"):
        return data

    content = data["content"]

    # Ask LLM to summarize
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
                You are a file assistant.
                
                Rules:
                - If user asks to READ file → use read_file
                - If user asks to SEARCH → use search_in_file
                - If user asks to LIST → use list_files
                - If user asks for SUMMARY → use create_summary
                - If user asks for STRUCTURED DATA or JSON → use extract_data
                
                Do not mix tools.
                """
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )

    summary = response.choices[0].message.content

    # Save file
    filename = os.path.basename(filepath).replace(".txt", "_summary.txt")
    save_path = os.path.join("outputs", filename)

    fs_tools.write_file(save_path, summary)

    return {
        "success": True,
        "summary_file": save_path,
        "summary": summary
    }

def extract_data(filepath):
    filepath = os.path.join("resumes", os.path.basename(filepath))

    data = fs_tools.read_file(filepath)

    if not data.get("success"):
        return data

    content = data["content"]

    # Ask LLM to return JSON ONLY
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Extract Name, Skills, and Experience from resume. Return ONLY valid JSON with keys: name, skills, experience."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )

    raw_output = response.choices[0].message.content

    # 🔥 Clean markdown ```json ``` if present
    clean_output = raw_output.strip()

    if clean_output.startswith("```"):
        clean_output = clean_output.replace("```json", "").replace("```", "").strip()

    try:
     structured_data = json.loads(clean_output)
    except Exception as e:
        return {"error": "Invalid JSON from model", "raw": raw_output}


    # Save JSON file
    filename = os.path.basename(filepath).replace(".txt", "_data.json")
    save_path = os.path.join("outputs", filename)

    fs_tools.write_file(save_path, json.dumps(structured_data, indent=2))

    return {
        "success": True,
        "file": save_path,
        "data": structured_data
    }

def chat():
    messages = [
        {
            "role": "system",
            "content": "Extract Name, Skills, Experience. Return JSON. Experience should be a single string summary."
        }
    ]

    while True:
        user_input = input("\nAsk: ")
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        # ✅ Case 1: Proper tool call
        if msg.tool_calls:
            tool_call = msg.tool_calls[0]   # 🔥 take only first call

            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            result = call_function(function_name, arguments)

            print("\nTOOL RESULT:", result)

        # ✅ Case 2: Groq text-based function call
        elif msg.content and "<function=" in msg.content:
            match = re.search(r'<function=(\w+)>(.*?)</function>', msg.content)

            if match:
                function_name = match.group(1)
                arguments = json.loads(match.group(2))

                result = call_function(function_name, arguments)

                print("\nTOOL RESULT:", result)

        # ✅ Case 3: Normal response
        else:
            print("\nAI:", msg.content)


if __name__ == "__main__":
    chat()