#!/usr/bin/env python3
import sys, json, re, requests
from bs4 import BeautifulSoup

SEARXNG_URL  = "http://localhost:8888"
OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
TIMEOUT      = 10

def search(query, n=3):
    try:
        resp = requests.get(f"{SEARXNG_URL}/search",
            params={"q": query, "format": "json", "categories": "general"},
            timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {"error": str(e), "results": []}

    results = [{"title": r.get("title",""), "url": r.get("url",""), "snippet": r.get("content","")}
               for r in data.get("results", [])[:n]]
    if not results:
        return {"error": "no results", "results": []}

    context = "\n\n".join(f"Source: {r['title']}\n{r['snippet']}" for r in results)
    return {"results": results, "summary": llm_summarize(query, context)}

def fetch(url):
    try:
        resp = requests.get(url, timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0"})
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script","style","nav","footer","header","aside"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True))[:4000]
    return {"text": text, "summary": llm_summarize("Summarize this page", text)}

def llm_summarize(query, context):
    prompt = f'You are Jarvis. The user asked: "{query}"\n\n{context}\n\nSummarize in 2-3 spoken sentences. No markdown.'
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "keep_alive": 300},
            timeout=30)
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"Search done but summarization failed: {e}"

def handle(line):
    try:
        req = json.loads(line.strip())
    except Exception as e:
        return {"ok": False, "error": str(e)}
    cmd = req.get("cmd")
    if cmd == "search":
        return {"ok": True, "data": search(req["query"], req.get("n", 3))}
    elif cmd == "fetch":
        return {"ok": True, "data": fetch(req["url"])}
    return {"ok": False, "error": f"unknown cmd: {cmd}"}

def main():
    print(json.dumps({"ok": True, "data": "search ready"}), flush=True)
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle(line)), flush=True)

if __name__ == "__main__":
    main()
