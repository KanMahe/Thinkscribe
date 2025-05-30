import requests
import re
import concurrent.futures
import time
import os
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("openrouter_api_key")
MODEL_ID = "mistralai/mistral-7b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Rate limit configuration: 20 requests per 60 seconds
CALLS_PER_MINUTE = 20
ONE_MINUTE = 60

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=ONE_MINUTE)
def query_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return query_openrouter(prompt)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def build_prompt(title, authors, year, abstract, url):
    return f"""
You are an expert AI assistant trained to analyze academic papers.

Please extract the following details **accurately** from the provided research paper.

---
📄 Title: {title}

👤 Authors: {', '.join(authors)}

📅 Year: {year}

🧠 Abstract: {abstract}

🔗 URL: {url}
---

Provide each of the following as a separate clear, short summary. Please follow this **numbered format exactly**, with each section starting on a new line:

1. 🧠 **Abstract** (summarize if too long)
2. 🛠️ **Techniques Used** (mention specific algorithms, frameworks, methods)
3. 👤 **Authors** (format in IEEE style: e.g., A. Kumar, B. Singh, and C. Zhang)
4. 📅 **Year**
5. 🔗 **URL**
"""

def extract_section(text, section_name):
    pattern = rf"(?mi)^.*?{section_name}\s*(?:\*\*|:|-)?\s*(.*?)\s*(?=^(\d[\.\)]|[🧠🛠️👤📅🔗])|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else "Not available"

def extract_paper_details(paper):
    try:
        prompt = build_prompt(
            title=paper.get("title", ""),
            authors=paper.get("authors", []),
            year=paper.get("year", "Unknown"),
            abstract=paper.get("abstract", ""),
            url=paper.get("url", "")
        )

        content = query_openrouter(prompt)
        techniques = extract_section(content, "Techniques Used")
        techniques_list = [tech.strip() for tech in techniques.split(',') if tech.strip()]

        return {
            "title": paper.get("title", ""),
            "abstract": extract_section(content, "Abstract"),
            "techniques": techniques_list,
            "authors": parse_authors(extract_section(content, "Authors")),
            "year": extract_section(content, "Year"),
            "url": paper.get("url", "")
        }
    except Exception as e:
        print(f"[LLM ERROR] Failed to process: {paper.get('title')} - {str(e)}")
        return {
            "title": paper.get("title", ""),
            "error": str(e)
        }
def parse_authors(authors_str):
    """
    Converts a formatted authors string like:
    "A. Kumar, B. Singh, and C. Zhang"
    into a list: ["A. Kumar", "B. Singh", "C. Zhang"]
    """
    if not authors_str:
        return []

    # Replace " and " with comma for consistent splitting
    authors_str = authors_str.replace(" and ", ", ")
    # Split and clean up whitespace
    return [author.strip() for author in authors_str.split(",") if author.strip()]

def process_all_papers(papers_json):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_paper = {executor.submit(extract_paper_details, paper): paper for paper in papers_json}
        for future in concurrent.futures.as_completed(future_to_paper):
            paper = future_to_paper[future]
            try:
                extracted = future.result()
                results.append(extracted)
            except Exception as e:
                print(f"[PROCESSING ERROR] {paper.get('title')} - {str(e)}")
    return results