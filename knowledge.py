import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Fix per far leggere anche i link nei documenti Word (se docx è installato)
def load_docx(path: str) -> str:
    doc = DocxDocument(path)
    paragraphs = []
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        parts = [p.text]
        for rel in p.part.rels.values():
            if "hyperlink" in rel.reltype:
                parts.append(f"({rel.target_ref})")
        paragraphs.append(" ".join(parts))
    return "\n".join(paragraphs)


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return load_docx(path)
    elif ext in (".txt", ".md"):
        return load_txt(path)
    raise ValueError(f"Formato non supportato: {ext}")


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 60) -> list[str]:
    # Semplice chunking basato su parole, con overlap per mantenere contesto tra i chunk
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 30]


class KnowledgeBase:
    def __init__(self, data_dir: str = "data"):
        self.chunks: list[str] = []
        self.sources: list[str] = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )
        self._fitted = False
        self._load(data_dir)

    def _load(self, data_dir: str):
        files = [
            ("tax_knowledge_1_txt.docx", "regimi_detrazioni"),
            ("tax_knowledge_2_txt.docx", "fatturazione"),
            ("tone_of_voice.txt", "tone_of_voice"),
        ]
        for filename, source in files:
            path = os.path.join(data_dir, filename)
            if not os.path.exists(path):
                print(f"[WARNING] File non trovato: {path}")
                continue
            text = load_document(path)
            chunks = chunk_text(text)
            self.chunks.extend(chunks)
            self.sources.extend([source] * len(chunks))

        if self.chunks:
            self.vectorizer.fit(self.chunks)
            self._fitted = True

    def retrieve(self, query: str, top_k: int = 4) -> str:
        # Restituisce i chunk più rilevanti per la query, come stringa unica
        if not self._fitted or not self.chunks:
            return ""

        query_vec = self.vectorizer.transform([query])
        corpus_vec = self.vectorizer.transform(self.chunks)
        scores = cosine_similarity(query_vec, corpus_vec)[0]

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        seen_sources = set()
        for idx in top_indices:
            if scores[idx] < 0.01:
                continue
            chunk = self.chunks[idx]
            source = self.sources[idx]
            label = f"[{source}]" if source not in seen_sources else ""
            seen_sources.add(source)
            results.append(f"{label}\n{chunk}".strip())

        return "\n\n---\n\n".join(results)
