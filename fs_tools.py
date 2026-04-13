import os
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document

# ✅ ALWAYS FIX PATH HERE
def normalize_path(filepath):
    return os.path.join("resumes", os.path.basename(filepath))


# ---------------- READ FILE ---------------- #

def read_file(filepath: str) -> dict:
    try:
        filepath = normalize_path(filepath)

        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}

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
            return {"success": False, "error": "Unsupported file type"}

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


# ---------------- LIST FILES ---------------- #

def list_files(directory: str, extension: str = None, **kwargs) -> list:
    try:
        directory = "resumes"  # force fix

        if not os.path.exists(directory):
            return [{"error": "resumes folder not found"}]

        files_data = []

        for file in os.listdir(directory):
            if extension and extension.strip():
                if not file.lower().endswith(extension.lower()):
                    continue

            path = os.path.join(directory, file)

            if os.path.isfile(path):
                files_data.append({
                    "name": file,
                    "size": os.path.getsize(path),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(path)
                    ).isoformat()
                })

        return files_data

    except Exception as e:
        return [{"error": str(e)}]


# ---------------- WRITE FILE ---------------- #

def write_file(filepath: str, content: str) -> dict:
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------- SEARCH ---------------- #

def search_in_file(filepath: str, keyword: str) -> dict:
    try:
        data = read_file(filepath)

        if not data.get("success"):
            return data

        content = data["content"]
        keyword_lower = keyword.lower()

        matches = []
        for i, line in enumerate(content.split("\n")):
            if keyword_lower in line.lower():
                matches.append({
                    "line_number": i + 1,
                    "text": line.strip()
                })

        return {"success": True, "matches": matches}

    except Exception as e:
        return {"success": False, "error": str(e)}