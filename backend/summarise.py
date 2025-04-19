import ollama
import re
import concurrent.futures

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

Provide each of the following as a separate clear, short summary.

1. 🧠 **Abstract** (summarize if too long)
2. 🛠️ **Techniques Used** (mention specific algorithms, frameworks, methods)
3. 👤 **Authors** (format in IEEE style: e.g., A. Kumar, B. Singh, and C. Zhang)
4. 📅 **Year**
5. 🔗 **URL**
"""

def extract_section(text, section_name):
    # Extracts the section text following the section header
    pattern = rf"{section_name}\s*[:：\-]*\s*(.*?)\s*(?=\n[1-5🧠🛠️👤📅🔗]|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
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
        
        # Optimized API request (ensure you're not querying too often or too much data at once)
        response = ollama.chat(
            model="mistral:7b",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract message content
        content = response.get("message", {}).get("content", "")
        
        return {
            "title": paper.get("title", ""),
            "abstract": extract_section(content, "Abstract"),
            "techniques": extract_section(content, "Techniques Used"),
            "authors": extract_section(content, "Authors"),
            "year": extract_section(content, "Year"),
            "url": paper.get("url", "")
        }
    except Exception as e:
        print(f"[LLM ERROR] Failed to process: {paper.get('title')} - {str(e)}")
        return {
            "title": paper.get("title", ""),
            "error": str(e)
        }

def process_all_papers(papers_json):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Using ThreadPoolExecutor to process papers concurrently
        future_to_paper = {executor.submit(extract_paper_details, paper): paper for paper in papers_json}
        
        for future in concurrent.futures.as_completed(future_to_paper):
            paper = future_to_paper[future]
            try:
                extracted = future.result()
                results.append(extracted)
            except Exception as e:
                print(f"[PROCESSING ERROR] {paper.get('title')} - {str(e)}")
    return results
