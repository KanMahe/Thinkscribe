# backend/papersearch.py

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def search_arxiv(query: str, limit: int = 100):
    """
    Search arXiv for papers matching `query`, return up to `limit` results
    as a list of dicts with keys: title, authors, abstract, year, url.
    """
    base_url = "http://export.arxiv.org/api/query"
    all_papers = []

    batch_size = 100
    for start in range(0, limit, batch_size):
        max_results = min(batch_size, limit - start)
        params = {
            "search_query": f"all:{query}",
            "start": start,
            "max_results": max_results
        }
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
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

            all_papers.append({
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": abstract,
                "techniques": [],
                "url": url
            })

        if len(all_papers) >= limit:
            break

    return all_papers[:limit]
