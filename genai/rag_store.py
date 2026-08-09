# -*- coding: utf-8 -*-
"""RAG vector store: embeds crypto news via Gemini and retrieves relevant
articles for a given query using a local Chroma collection (no paid vector DB)."""

import os
import tempfile
import chromadb
from google import genai

EMBED_MODEL = "models/gemini-embedding-001"
COLLECTION_NAME = "crypto_news"
PERSIST_DIR = os.environ.get("CHROMA_DATA_DIR", os.path.join(tempfile.gettempdir(), "trading_bot_btc_chroma"))
os.makedirs(PERSIST_DIR, exist_ok=True)


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY no configurada en el entorno (.env)")
    return genai.Client(api_key=api_key)


def _embed_texts(client, texts):
    embeddings = []
    for text in texts:
        resp = client.models.embed_content(model=EMBED_MODEL, contents=text)
        embeddings.append(resp.embeddings[0].values)
    return embeddings


def build_index(articles):
    """Embed and store a list of articles (from news_fetcher) into Chroma.

    Each article dict needs: title, summary, link, source.
    Returns the number of articles indexed.
    """
    client = _get_client()
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    texts = [f"{a['title']}. {a['summary']}" for a in articles]
    embeddings = _embed_texts(client, texts)

    ids = [str(i) for i in range(len(articles))]
    metadatas = [{"title": a["title"], "link": a["link"], "source": a["source"]} for a in articles]

    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(articles)


def query_relevant_news(query, top_k=5):
    """Return the top_k most relevant news articles for a given query."""
    client = _get_client()
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    if collection.count() == 0:
        return []

    query_embedding = _embed_texts(client, [query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, collection.count()))

    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({"text": doc, "title": meta["title"], "link": meta["link"], "source": meta["source"]})
    return hits


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from news_fetcher import fetch_latest_news

    print("Fetching news...")
    articles = fetch_latest_news(max_per_feed=5)
    print(f"Indexing {len(articles)} articles...")
    n = build_index(articles)
    print(f"Indexed {n} articles")

    print("\nQuerying: 'bitcoin price movement'")
    results = query_relevant_news("bitcoin price movement", top_k=3)
    for r in results:
        print(f"- [{r['source']}] {r['title']}")
