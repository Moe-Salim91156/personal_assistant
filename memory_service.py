#!/usr/bin/env python3
import sys, json
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

JARVIS_DIR = Path.home() / ".jarvis"
JARVIS_DIR.mkdir(exist_ok=True)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(
    path=str(JARVIS_DIR / "chromadb"),
    settings=Settings(anonymized_telemetry=False),
)
interactions = client.get_or_create_collection("interactions", metadata={"hnsw:space": "cosine"})
profile      = client.get_or_create_collection("profile",      metadata={"hnsw:space": "cosine"})

def embed(text):
    return embedder.encode(text, normalize_embeddings=True).tolist()

def store(text, kind="interaction"):
    doc_id = f"{kind}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    interactions.add(ids=[doc_id], embeddings=[embed(text)], documents=[text],
                     metadatas=[{"kind": kind, "at": datetime.utcnow().isoformat()}])
    return {"id": doc_id}

def recall(query, n=5, kind=None):
    where = {"kind": kind} if kind else None
    count = interactions.count()
    if count == 0:
        return []
    results = interactions.query(
        query_embeddings=[embed(query)],
        n_results=min(n, count),
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {"text": doc, "kind": meta.get("kind"), "at": meta.get("at"),
         "relevance": round(1 - dist, 3)}
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]

def store_profile(key, value):
    text = f"{key}: {value}"
    doc_id = f"profile_{key}"
    try:
        profile.delete(ids=[doc_id])
    except Exception:
        pass
    profile.add(ids=[doc_id], embeddings=[embed(text)], documents=[text],
                metadatas=[{"key": key, "value": value, "at": datetime.utcnow().isoformat()}])
    return {"key": key, "value": value}

def get_profile(key=None):
    if key:
        try:
            r = profile.get(ids=[f"profile_{key}"], include=["documents", "metadatas"])
            if r["documents"]:
                return [{"key": key, "value": r["metadatas"][0]["value"]}]
        except Exception:
            pass
        return []
    r = profile.get(include=["documents", "metadatas"])
    return [{"key": m["key"], "value": m["value"]} for m in r["metadatas"]]

def handle(line):
    try:
        req = json.loads(line.strip())
    except Exception as e:
        return {"ok": False, "error": str(e)}
    cmd = req.get("cmd")
    if cmd == "store":
        return {"ok": True, "data": store(req["text"], req.get("kind", "interaction"))}
    elif cmd == "recall":
        return {"ok": True, "data": recall(req["query"], req.get("n", 5), req.get("kind"))}
    elif cmd == "store_profile":
        return {"ok": True, "data": store_profile(req["key"], req["value"])}
    elif cmd == "get_profile":
        return {"ok": True, "data": get_profile(req.get("key"))}
    return {"ok": False, "error": f"unknown cmd: {cmd}"}

def main():
    print(json.dumps({"ok": True, "data": "memory ready"}), flush=True)
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle(line)), flush=True)

if __name__ == "__main__":
    main()
