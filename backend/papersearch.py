import requests
def search_semantic_scholar(query, limit=100, year_start=2020, year_end=2025):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    all_papers = []
    offset = 0

    while len(all_papers) < limit:
        batch_size = min(100, limit - len(all_papers))
        params = {
            "query": query,
            "limit": batch_size,
            "offset": offset,
            "fields": "title,authors,year,abstract,url",
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        new_papers = data.get("data", [])
        if not new_papers:
            break

        for item in new_papers:
            paper = {
                "title": item.get("title", "N/A"),
                "authors": [author.get("name") for author in item.get("authors", [])],
                "year": item.get("year", "N/A"),
                "abstract": item.get("abstract", "No abstract available."),
                "url": item.get("url", "N/A")
            }
            all_papers.append(paper)

        offset += batch_size

    return all_papers


