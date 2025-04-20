# Literature Survey Helper

An intelligent and interactive assistant for automating the literature review process using keyword-based search, Semantic Scholar API, and LLM-powered extraction. Ideal for researchers who want to streamline paper discovery, summarization, and reference management.

---

##  Problem Statement

Literature surveys are time-consuming. Researchers need a way to quickly extract meaningful information (e.g., abstract, techniques, authors) from a large set of papers.

**This tool solves that by:**
- Searching relevant papers using keywords from your research problem.
- Extracting structured information with the help of LLMs.
- Presenting data in a clean tabular UI.
- Enabling easy selection and reference management.

---

##  How It Works

### 1. **Keyword-based Search**
- Input your research problem or topic.
- Keywords are used to query the **Semantic Scholar API**.
- Retrieves paper metadata and raw content.

### 2. **LLM-Based Content Extraction**
- Each paper is passed to a **Large Language Model (LLM)** (e.g., `mistral:7b` via [OpenRouter.ai](https://openrouter.ai)).
- The LLM extracts the following:
  - 📄 Title
  - 👤 Authors
  - 📅 Year
  - 🧠 Abstract
  - 🛠️ Techniques Used
  - 🔗 URL

### 3. **Dynamic Literature Table**
- Results displayed in an editable, dynamic **tabular format**.
- Columns:
  - Authors
  - Title
  - Abstract
  - Techniques
  - Year
  - URL

### 4. **Select & Manage Papers**
- Each row = one paper.
- Users can **select or remove** papers as needed.
- Auto-generates **BibTeX references** for selected papers.
- Author names and citations formatted in **IEEE** or other academic styles.

---

## 🛠️ Technologies Used

| Layer        | Tech Stack                          |
|--------------|--------------------------------------|
| **Frontend** | React + Vite + JavaScript            |
| **Backend**  | Node.js / Python (optional APIs)     |
| **LLM API**  | OpenRouter (using `mistral:7b`)      |
| **Paper API**| Semantic Scholar API                 |
| **Styling**  | TailwindCSS / Custom CSS             |

---

##  Features

- 🔎 Keyword-based search for relevant papers.
- 🧠 LLM-powered metadata extraction.
- 📋 Interactive tabular interface.
- 🗑️ Option to remove unwanted papers.
- 🧾 Auto-generated BibTeX references.
- 🌐 Paper URLs included for quick access.
- ⚙️ Modular and extendable architecture.

---

##  Example Workflow

