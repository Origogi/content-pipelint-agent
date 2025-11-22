import os

from firecrawl import FirecrawlApp
from firecrawl.v2.types import ScrapeOptions, Document
from crewai.tools import tool
import re

@tool
def web_search_tool(query: str):
    """
    Web Search Tool.

    Args:
        query (str): The search query.

    Returns:
        A list of search results with the website content in cleaned markdown format.
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    response = app.search(
        query=query,
        limit=5,
        scrape_options=ScrapeOptions(
            formats=["markdown"],
        )
    )

    cleaned_chunks = []

    for result in response.web:
        if isinstance(result, Document):
            markdown = result.markdown
            cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
            cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)
            cleaned_result = {
                "title": result.metadata.title,
                "url": result.metadata.url,
                "markdown": cleaned,
            }
            cleaned_chunks.append(cleaned_result)

    print(cleaned_chunks)
    return cleaned_chunks
