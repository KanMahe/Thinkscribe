from flask import Flask, request, jsonify
from summarise import process_all_papers
from pdf_parser import extract_text_from_pdf
from keywordextractor import extract_keywords
from bibtexmanager import generate_bibtex_entry
from papersearch import search_semantic_scholar
import os
import json
from datetime import datetime


app = Flask(__name__)

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
    year_start = int(request.args.get("year_start", 2020))  # Default to 2020
    year_end = int(request.args.get("year_end", 2025))  # Default to 2025

    # Extract keywords from the problem statement (query)
    keywords = extract_keywords(query)
    print(f"Extracted Keywords: {keywords}")

    # Refine the query
    refined_query = query + " " + " ".join(keywords)
    print(f"Refined Query: {refined_query}")

    # Fetch papers from Semantic Scholar
    papers = search_semantic_scholar(refined_query, limit=limit, year_start=year_start, year_end=year_end)

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


# @app.route("/fetch_and_store", methods=["GET"])
# def fetch_and_store():
#     query = request.args.get("query")
#     if not query:
#         return jsonify({"error": "Query parameter is required"}), 400
    
#     limit = int(request.args.get("limit", 100))  # Default to 100 if not provided
#     year_start = int(request.args.get("year_start", 2020))  # Default to 2020
#     year_end = int(request.args.get("year_end", 2025))  # Default to 2025

#     # Extract keywords from the problem statement (query)
#     keywords = extract_keywords(query)
#     print(f"Extracted Keywords: {keywords}")  # Log the extracted keywords for debugging

#     # Create a refined query with the problem statement and extracted keywords
#     refined_query = query + " " + " ".join(keywords)
#     print(f"Refined Query: {refined_query}")  # Log the refined query for debugging

#     # Use the refined query to fetch papers
#     papers = search_semantic_scholar(refined_query, limit=limit, year_start=year_start, year_end=year_end)

#     if not papers:
#         return jsonify({"message": "No papers found or API error"}), 404

#     # Generate a unique filename with timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"data/{query.replace(' ', '_')}_{timestamp}.json"

#     # Ensure the 'data' folder exists
#     os.makedirs("data", exist_ok=True)

#     # Save the fetched papers to a JSON file
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(papers, f, indent=4)

#     # Return a success message with the filename
#     return jsonify({"message": f"{len(papers)} papers stored", "file": filename})


# @app.route("/search_papers", methods=["GET"]) PLAIN SEARCHING CANT STORE
# def search_papers():
#     query = request.args.get("query")
#     if not query:
#         return jsonify({"error": "Query parameter is required"}), 400

#     papers = search_semantic_scholar(query)
#     return jsonify({"papers": papers})

# @app.route("/process_papers", methods=["POST"])
# def process_papers():
#     """
#     This route processes the papers extracted in the previous step using an LLM model (Mistral-7B).
#     The papers are extracted from the JSON file.
#     """
#     # Get the path to the JSON file containing the papers (uploaded or generated)
#     file_path = request.json.get("file_path")
#     if not file_path or not os.path.exists(file_path):
#         return jsonify({"error": "Valid file path is required."}), 400

#     with open(file_path, "r", encoding="utf-8") as f:
#         papers = json.load(f)

#     # Use LLM to process each paper and extract relevant details
#     processed_papers = []
#     for paper in papers:
#         # Call the summarization function that uses Mistral-7B to extract various details
#         details = summarize_paper(paper)  # Pass the entire paper (not just abstract)

#         # Add the processed details to the paper object
#         processed_paper = {**paper, **details}
#         processed_papers.append(processed_paper)

#     return jsonify({"processed_papers": processed_papers})



if __name__ == "__main__":
    app.run(debug=True)
