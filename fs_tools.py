import os
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document


def fix_path(filepath):
    return os.path.join("resumes", os.path.basename(filepath))

def read_file(filepath: str) -> dict:
    try:
        ext = os.path.splitext(filepath)[1].lower()
        content = ""

        if ext == ".pdf":
            reader = PdfReader(filepath)
            for page in reader.pages:
                content += page.extract_text() or ""

        elif ext == ".docx":
            doc = Document(filepath)
            for para in doc.paragraphs:
                content += para.text + "\n"

        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

        else:
            return {"error": "Unsupported file type"}

        return {
            "success": True,
            "content": content,
            "metadata": {
                "filename": os.path.basename(filepath),
                "size": os.path.getsize(filepath)
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(directory: str, extension: str = None, **kwargs) -> list:
    try:
        # 🔥 Fix incorrect directory names from LLM
        directory = directory.lower().strip()

        if "resume" in directory:
            directory = "resumes"

        files_data = []

        for file in os.listdir(directory):
            if extension and extension.strip() and not file.endswith(extension):
                continue

            path = os.path.join(directory, file)

            if os.path.isfile(path):
                files_data.append({
                    "name": file,
                    "size": os.path.getsize(path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                })

        return files_data

    except Exception as e:
        return [{"error": str(e)}]


def write_file(filepath: str, content: str) -> dict:
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {"success": True, "message": "File written successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def search_in_file(filepath: str, keyword: str) -> dict:
    try:
        data = read_file(filepath)

        if not data.get("success"):
            return data

        content = data["content"]
        keyword_lower = keyword.lower()

        matches = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if keyword_lower in line.lower():
                matches.append({
                    "line_number": i + 1,
                    "text": line.strip()
                })

        return {
            "success": True,
            "matches": matches
        }

    except Exception as e:
        return {"success": False, "error": str(e)}