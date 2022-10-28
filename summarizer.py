#Transformer HuggingFace
from transformers import pipeline

summarizer = pipeline("summarization")


def summarize_text(article):
    num_iters = int(len(article) / 1000)
    summarized_text = []
    for i in range(0, num_iters + 1):
        start = 0
        start = i * 1000
        end = (i + 1) * 1000
        out = summarizer(article[start:end])
        out = out[0]
        out = out['summary_text']
        summarized_text.append(out)

    return " ".join(summarized_text)

