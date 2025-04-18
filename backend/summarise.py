from transformers import pipeline

# Load summarizer (you can load this once and reuse)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text, max_length=130, min_length=30):
    # Truncate input to first 1024 tokens (model limit)
    text = text[:1024]
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
