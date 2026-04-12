# LLM-Based File Assistant (Resume Analyzer)

## 📌 Project Overview
This project is an AI-powered file assistant that can read, analyze, and process resume files using LLM (Large Language Models).

It supports natural language queries and performs operations like:
- Listing files
- Reading resumes
- Searching keywords
- Generating summaries
- Extracting structured data (JSON)

---

## 🚀 Features

### 1. File System Tools
- Read files (TXT, PDF, DOCX)
- List files in a directory
- Search keywords inside files
- Write output files

### 2. AI Integration
- Uses Groq LLM for tool calling
- Converts user queries into function calls

### 3. Resume Summary
- Generates AI-based summary
- Saves summary file

### 4. Structured Data Extraction
Extracts:
- Name
- Skills
- Experience

Output example:
```json
{
  "name": "Rahul Sharma",
  "skills": ["Python", "React"],
  "experience": "Worked on freelance projects"
}

```
---
## 👤 Author

**Suraj Tapase**  
Full Stack Developer | AI Enthusiast