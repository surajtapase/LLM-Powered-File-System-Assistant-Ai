import os
import json
import re
from groq import Groq
import fs_tools
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- INTENT DETECTION ---------------- #

def detect_intent(user_input: str):
    text = user_input.lower()

    if "list" in text:
        return "list_files", {"directory": "resumes"}

    if "read" in text:
        file = re.findall(r'[\w\-]+\.txt', text)
        if file:
            return "read_file", {"filepath": file[0]}

    if "summary" in text or "summarize" in text:
        file = re.findall(r'[\w\-]+\.txt', text)
        if file:
            return "create_summary", {"filepath": file[0]}

    if "extract" in text or "structured" in text:
        file = re.findall(r'[\w\-]+\.txt', text)
        if file:
            return "extract_data", {"filepath": file[0]}

    return None, None

# ---------------- FUNCTION ROUTER ---------------- #

def call_function(name, args):
    try:
        if name == "list_files":
            return fs_tools.list_files(**args)

        elif name == "read_file":
            return fs_tools.read_file(**args)

        elif name == "search_in_file":
            return fs_tools.search_in_file(**args)

        elif name == "create_summary":
            return create_summary(**args)

        elif name == "extract_data":
            return extract_data(**args)

        return {"error": "Unknown function"}

    except Exception as e:
        return {"error": str(e)}

# ---------------- CUSTOM FUNCTIONS ---------------- #

def create_summary(filepath):
    data = fs_tools.read_file(filepath)

    if not data.get("success"):
        return data

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Summarize this resume briefly."},
            {"role": "user", "content": data["content"]}
        ],
        temperature=0
    )

    summary = response.choices[0].message.content

    save_path = os.path.join("outputs", os.path.basename(filepath).replace(".txt", "_summary.txt"))
    fs_tools.write_file(save_path, summary)

    return {"success": True, "file": save_path, "summary": summary}


def extract_data(filepath):
    data = fs_tools.read_file(filepath)

    if not data.get("success"):
        return data

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Return ONLY JSON with name, skills, experience."},
            {"role": "user", "content": data["content"]}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw)
    except:
        return {"error": "Invalid JSON", "raw": raw}

    save_path = os.path.join("outputs", os.path.basename(filepath).replace(".txt", "_data.json"))
    fs_tools.write_file(save_path, json.dumps(parsed, indent=2))

    return {"success": True, "file": save_path, "data": parsed}

# ---------------- CHAT ---------------- #

def chat():
    while True:
        user_input = input("\nAsk: ")

        # ✅ RULE BASED (NO LLM)
        intent, args = detect_intent(user_input)

        if intent:
            result = call_function(intent, args)
            print("\nTOOL RESULT:", result)
            continue

        # ✅ ONLY fallback to LLM
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_input}],
            temperature=0
        )

        print("\nAI:", response.choices[0].message.content)


if __name__ == "__main__":
    chat()