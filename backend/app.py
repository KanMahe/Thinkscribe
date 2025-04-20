from flask import Flask, request, jsonify
from summarise import process_all_papers
from pdf_parser import extract_text_from_pdf
from keywordextractor import extract_keywords
from bibtexmanager import generate_bibtex_entry
from papersearch import search_semantic_scholar
import os
import json
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Lit Survey Helper API Running!"

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = os.path.join("../papers", file.filename)
    file.save(file_path)

    text = extract_text_from_pdf(file_path)
    summary = summarize_text(text)
    keywords = extract_keywords(text)

    return jsonify({
        "summary": summary,
        "keywords": keywords
    })

@app.route("/bibtex", methods=["POST"])
def create_bibtex():
    data = request.get_json()
    bibtex = generate_bibtex_entry(data)
    return jsonify({"bibtex": bibtex})

@app.route("/fetch_and_store", methods=["GET"])
def fetch_and_store():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    limit = int(request.args.get("limit", 100))  # Default to 100 if not provided

    # Extract keywords from the problem statement (query)
    keywords = extract_keywords(query)
    print(f"Extracted Keywords: {keywords}")

    # Refine the query
    refined_query = query + " " + " ".join(keywords)
    print(f"Refined Query: {refined_query}")

    # Fetch papers from Semantic Scholar
    papers = search_semantic_scholar(refined_query, limit=limit)

    if not papers:
        return jsonify({"message": "No papers found or API error"}), 404

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/{query.replace(' ', '_')}_{timestamp}.json"

    # Ensure directory exists
    os.makedirs("data", exist_ok=True)

    # Save raw papers
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=4)

    # ✅ Process the papers immediately
    try:
        processed_data = process_all_papers(papers)
    except Exception as e:
        return jsonify({"error": f"Failed during processing: {str(e)}"}), 500

    # ✅ Return processed output with raw file reference
    return jsonify({
        "message": f"{len(papers)} papers fetched, stored, and processed successfully.",
        "file": filename,
        "processed": processed_data
    })

if __name__ == "__main__":
    app.run(debug=True)
