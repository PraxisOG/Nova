from tools.decorators import tool
import os
import subprocess

@tool(name="web_search_summary", description="Performs a web search and returns summarized results.")
def web_search_summary(query: str) -> str:
    """
    Takes a search query, performs a web search using Google,
    extracts top links, and returns summarized content from those pages
    """
    # Install required libraries if not already installed
    subprocess.run(["pip", "install", "requests", "beautifulsoup4"], check=True)

    import requests
    from bs4 import BeautifulSoup

    try:
        # Perform Google search (basic method for demonstration purposes)
        url = f"https://www.google.com/search?q={query}&num=5"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        link_results = [a.get('href', '') for a in soup.select("div.g cite")]

        # Extract content from top 3 results with basic summarization logic
        summaries = []
        valid_links = [l for l in link_results if l.startswith(http)]

        for link in valid_links[:3]:
            try:
                article_response = requests.get(link, timeout=10)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                # Simple summarization by extracting first paragraph or key content block
                text_content = article_soup.find_all(['p', 'h1', 'h2'])
                summary_text = ' '.join(p.get_text().strip() for p in text_content[:3] if p.text.strip())

                if len(summary_text) > 50:
                    summaries.append(f"\n=== Summary from {link} ===\n{summary_text[:200]}...")
            except Exception as e:
                continue

        return f"Web Search Results for '{query}':\n{''.join(summaries)}" if summaries else "No valid results found."
    
    except Exception as e:
        return f"Error performing search: {str(e)}"