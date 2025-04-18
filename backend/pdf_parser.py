import pdfplumber

def extract_text_from_pdf(file_path):
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages[:5]:  # Extract first few pages
            page_text = page.extract_text()
            if page_text:  # Check if text was extracted
                full_text += page_text + "\n"
            else:
                full_text += "[No text found on this page]\n"
    return full_text
