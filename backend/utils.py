def read_faq():
    with open("backend/docs/airline_faq.txt", "r", encoding="utf-8") as f:
        return f.read()

from duckduckgo_search import DDGS

def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return "\n\n".join([r['title'] + ":\n" + r['body'] + "\n" + r['href'] for r in results])
