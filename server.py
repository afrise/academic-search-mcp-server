import logging
import sys
import os
from datetime import datetime
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import unicodedata
import json
import sys

# Set UTF-8 as default encoding for Python
sys.stdout.recodeinfo = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize FastMCP server
mcp = FastMCP("scientific_literature")

# Constants
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "scientific-literature-app/1.0"


async def make_api_request(url: str, headers: dict = None, params: dict = None) -> dict[str, Any] | None:
    """Make a request to the API with proper error handling."""
    if headers is None:
        headers = { "User-Agent": USER_AGENT }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

def format_paper_data(data: dict, source: str) -> str:
    """Format paper data from different sources into a consistent string format."""
    if not data:
        return "No paper data available"
        
    try:
        if source == "semantic_scholar":
            title = unicodedata.normalize('NFKD', str(data.get('title', 'No title available')))
            authors = ', '.join([author.get('name', 'Unknown Author') for author in data.get('authors', [])])
            year = data.get('year') or 'Year unknown'
            external_ids = data.get('externalIds', {}) or {}
            doi = external_ids.get('DOI', 'No DOI available')
            venue = data.get('venue') or 'Venue unknown'
            abstract = data.get('abstract') or 'No abstract available'
            tldr = (data.get('tldr') or {}).get('text', '')
            is_open = "Yes" if data.get('isOpenAccess') else "No"
            pdf_data = data.get('openAccessPdf', {}) or {}
            pdf_url = pdf_data.get('url', 'Not available')

        elif source == "crossref":
            title = (data.get('title') or ['No title available'])[0]
            authors = ', '.join([
                f"{author.get('given', '')} {author.get('family', '')}".strip() or 'Unknown Author'
                for author in data.get('author', [])
            ])
            year = (data.get('published-print', {}).get('date-parts', [['']])[0][0]) or 'Year unknown'
            doi = data.get('DOI') or 'No DOI available'
            
        result = [
            f"Title: {title}",
            f"Authors: {authors}",
            f"Year: {year}",
            f"DOI: {doi}"
        ]
        
        if source == "semantic_scholar":
            result.extend([
                f"Venue: {venue}",
                f"Open Access: {is_open}",
                f"PDF URL: {pdf_url}",
                f"Abstract: {abstract}"
            ])
            if tldr:
                result.append(f"TL;DR: {tldr}")
                
        return "\n".join(result) + "\t\t\n"
        
    except Exception as e:
        return f"Error formatting paper data: {str(e)}"

@mcp.tool()
async def search_papers(query: str, limit: int = 10) -> str:
    """Search for papers across multiple sources.

    args: 
        query: the search query
        limit: the maximum number of results to return (default 10)
    """

    if query == "":
        return "Please provide a search query."
    
    # Truncate long queries
    MAX_QUERY_LENGTH = 300
    if len(query) > MAX_QUERY_LENGTH:
        original_length = len(query)
        query = query[:MAX_QUERY_LENGTH] + "..."
    
    try:
        # Search Semantic Scholar
        semantic_url = f"{SEMANTIC_SCHOLAR_API}/paper/search?query={query}&limit={limit}"
        semantic_data = await make_api_request(semantic_url)

        # Search Crossref
        crossref_url = f"{CROSSREF_API}?query={query}&rows={limit}"
        crossref_data = await make_api_request(crossref_url)

        results = []
        
        if semantic_data and 'papers' in semantic_data:
            results.append("=== Semantic Scholar Results ===")
            for paper in semantic_data['papers']:
                results.append(format_paper_data(paper, "semantic_scholar"))

        if crossref_data and 'items' in crossref_data.get('message', {}):
            results.append("\n=== Crossref Results ===")
            for paper in crossref_data['message']['items']:
                results.append(format_paper_data(paper, "crossref"))

        if not results:
            return "No results found or error occurred while fetching papers."

        return "\n".join(results)
    except:
        return "Error searching papers."

@mcp.tool()
async def fetch_paper_details(paper_id: str, source: str = "semantic_scholar") -> str:
    """Get detailed information about a specific paper.

    Args:
        paper_id: Paper identifier (DOI for Crossref, paper ID for Semantic Scholar)
        source: Source database ("semantic_scholar" or "crossref")
    """
    if source == "semantic_scholar":
        url = f"{SEMANTIC_SCHOLAR_API}/paper/{paper_id}"
    elif source == "crossref":
        url = f"{CROSSREF_API}/{paper_id}"
    else:
        return "Unsupported source. Please use 'semantic_scholar' or 'crossref'."

    data = await make_api_request(url)
    
    if not data:
        return f"Unable to fetch paper details from {source}."

    if source == "crossref":
        data = data.get('message', {})

    return format_paper_data(data, source)


@mcp.tool()
async def search_by_topic(topic: str, year_start: int = None, year_end: int = None, limit: int = 10) -> str:
    """Search for papers by topic with optional date range. 
    
    Note: Query length is limited to 300 characters. Longer queries will be automatically truncated.
    
    Args:
        topic (str): Search query (max 300 chars)
        year_start (int, optional): Start year for date range
        year_end (int, optional): End year for date range  
        limit (int, optional): Maximum number of results to return (default 10)
        
    Returns:
        str: Formatted search results or error message
    """
    
    try:
        # Truncate long queries to prevent API errors
        MAX_QUERY_LENGTH = 300
        if len(topic) > MAX_QUERY_LENGTH:
            original_length = len(topic)
            topic = topic[:MAX_QUERY_LENGTH] + "..."
        
        # Try Semantic Scholar API first
        semantic_url = f"{SEMANTIC_SCHOLAR_API}/paper/search"
        params = {
            "query": topic.encode('utf-8').decode('utf-8'),
            "limit": limit,
            "fields": "title,authors,year,paperId,externalIds,abstract,venue,isOpenAccess,openAccessPdf,tldr"
        }
        if year_start and year_end:
            params["year"] = f"{year_start}-{year_end}"
            
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        data = await make_api_request(semantic_url, headers=headers, params=params)
        
        if data and 'data' in data:
            results = ["=== Search Results ==="]
            for paper in data['data']:
                results.append(format_paper_data(paper, "semantic_scholar"))
            return "\n".join(results)
            
        # Fallback to Crossref if Semantic Scholar fails
        return await search_papers(topic, limit)
        
    except Exception as e:
        return f"Error searching papers!"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
