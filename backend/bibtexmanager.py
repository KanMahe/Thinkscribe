def generate_bibtex_entry(data):
    return f"""
@article{{{data.get("id", "paper1")}}},
  title={{ {data["title"]} }},
  author={{ {' and '.join(data['authors'])} }},
  journal={{ {data.get('journal', 'Unknown Journal')} }},
  year={{ {data['year']} }},
  url={{ {data.get('url', '')} }}
}}""".strip()
