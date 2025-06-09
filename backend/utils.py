def read_faq(query: str):
    """Search the FAQ document for relevant information about the given query."""
    with open("backend/docs/airline_faq.txt", "r", encoding="utf-8") as f:
        faq_content = f.read()
    
    # Split the FAQ into sections
    sections = faq_content.split('\n\n')
    
    # Search for the most relevant section
    query = query.lower()
    relevant_sections = []
    
    for section in sections:
        if not section.strip():
            continue
            
        # Check if the section title matches the query
        if any(word.lower() in query for word in section.split(':')):
            relevant_sections.append(section)
    
    # If no relevant sections found, return the full FAQ
    if not relevant_sections:
        return faq_content
    
    # Return the most relevant sections
    return '\n\n'.join(relevant_sections)

from duckduckgo_search import DDGS

def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return "\n\n".join([r['title'] + ":\n" + r['body'] + "\n" + r['href'] for r in results])
