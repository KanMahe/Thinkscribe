from flask import Flask, request, jsonify
from pdf_parser import extract_text_from_pdf
from keywordextractor import extract_keywords
from bibtexmanager import generate_bibtex_entry
from summarise import process_all_papers,query_openrouter
import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from flask_cors import CORS
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["lit_survey_db"]
papers_collection = db["papers"]

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Lit Survey Helper API Running!"

@app.route('/get-papers', methods=['GET'])
def get_papers():
    try:
        papers = list(papers_collection.find({}, {"_id": 0}))
        return jsonify(papers), 200
    except Exception as e:
        print(f"[get-papers] error: {e}")
        return jsonify([]), 200

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    os.makedirs("../papers", exist_ok=True)
    file_path = os.path.join("../papers", file.filename)
    file.save(file_path)

    text = extract_text_from_pdf(file_path)
    paper_obj = {
        "title": file.filename,
        "authors": [],
        "year": datetime.now().year,
        "abstract": text[:2000],
        "techniques": [],
        "url": ""
    }
    return jsonify({"processed": [paper_obj]})

@app.route("/bibtex", methods=["POST"])
def create_bibtex():
    data = request.get_json()
    bibtex = generate_bibtex_entry(data)
    return jsonify({"bibtex": bibtex})

@app.route('/add-papers', methods=['POST'])
def add_papers():
    new_papers = request.json or []
    inserted_papers = []

    try:
        for paper in new_papers:
            existing = papers_collection.find_one({"title": paper["title"]})
            if not existing:
                papers_collection.insert_one(paper)
                inserted_papers.append(paper["title"])

        return jsonify({
            "message": f"{len(inserted_papers)} paper(s) added successfully.",
            "inserted_titles": inserted_papers
        }), 200

    except Exception as e:
        print(f"[add-papers] error: {e}")
        return jsonify({"message": str(e)}), 500


@app.route("/fetch_and_store", methods=["GET"])
def fetch_and_store():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    limit = int(request.args.get("limit", 100))
    keywords = extract_keywords(query)
    refined_query = query + " " + " ".join(keywords)
    print(f"Refined Query: {refined_query}")

    # Fetch from arXiv API
    base_url = "http://export.arxiv.org/api/query"
    all_papers = []
    batch_size = 100
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    try:
        for start in range(0, limit, batch_size):
            max_results = min(batch_size, limit - start)
            params = {
                "search_query": f"all:{refined_query}",
                "start": start,
                "max_results": max_results
            }

            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()

            root = ET.fromstring(resp.text)
            entries = root.findall("atom:entry", ns)
            if not entries:
                break

            for entry in entries:
                title = entry.find("atom:title", ns).text.strip()
                abstract = entry.find("atom:summary", ns).text.strip()
                pub = entry.find("atom:published", ns).text
                year = datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ").year
                authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
                url = entry.find("atom:id", ns).text

                # LLM Summarization
                try:
                    summary = query_openrouter(f"Summarize this abstract in 3-4 lines:\n\n{abstract}")

                except Exception as e:
                    summary = "LLM summarization failed."
                    print(f"[Summarization Error] {e}")

                all_papers.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "abstract": abstract,
                    "summary": summary,
                    "techniques": [],
                    "url": url
                })

            if len(all_papers) >= limit:
                break

        papers = all_papers[:limit]
        if not papers:
            return jsonify({"message": "No papers found or API error"}), 404

        
#  Now use LLM to summarize and extract details
        processed_data = process_all_papers(papers)

# You can optionally store the processed version as well in another collection
# processed_collection.insert_many(processed_data)

        return jsonify({
            "message": f"{len(papers)} papers fetched and processed successfully.",
            "processed": processed_data
        }), 200

    except Exception as e:
        print(f"[fetch_and_store] error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
