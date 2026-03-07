#!/usr/bin/env python3
"""
DuckDuckGo Web Search Script

This script performs web searches using DuckDuckGo's HTML search results.
It extracts search results including titles, URLs, and snippets.

Usage:
    python duckduckgo_search.py "search query" [--max-results 5] [--region us-en]

Example:
    python duckduckgo_search.py "Python programming tutorials" --max-results 3
"""

import argparse
import json
import sys
import urllib.parse
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


def search_duckduckgo(
    query: str, 
    max_results: int = 5, 
    region: str = "us-en",
    safe_search: bool = True
) -> List[Dict[str, str]]:
    """
    Perform a DuckDuckGo search and return results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        region: Region/language code (e.g., "us-en", "uk-en", "fr-fr")
        safe_search: Whether to enable safe search
        
    Returns:
        List of dictionaries with keys: 'title', 'url', 'snippet'
    """
    # Prepare search URL
    base_url = "https://html.duckduckgo.com/html/"
    params = {
        "q": query,
        "kl": region,
    }
    if safe_search:
        params["kp"] = "1"  # Moderate safe search
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}", file=sys.stderr)
        return []
    
    # Parse HTML response
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    # Find result containers
    result_elements = soup.find_all('div', class_='result')
    
    for result in result_elements[:max_results]:
        # Extract title and URL
        title_elem = result.find('a', class_='result__title')
        if not title_elem:
            continue
            
        title = title_elem.get_text(strip=True)
        url = title_elem.get('href', '')
        
        # Clean up URL (DuckDuckGo uses redirect URLs)
        if url.startswith('//duckduckgo.com/l/'):
            # Try to extract actual URL from redirect
            try:
                # Parse the redirect URL to get actual destination
                parsed = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in query_params:
                    actual_url = query_params['uddg'][0]
                    url = urllib.parse.unquote(actual_url)
            except:
                pass
        
        # Extract snippet
        snippet_elem = result.find('a', class_='result__snippet')
        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
        
        # If no snippet from result__snippet, try other classes
        if not snippet:
            snippet_elem = result.find('div', class_='result__snippet')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
        
        results.append({
            'title': title,
            'url': url,
            'snippet': snippet
        })
    
    return results


def search_duckduckgo_simple(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Simplified version of DuckDuckGo search for common use cases.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with keys: 'title', 'url', 'snippet'
    """
    return search_duckduckgo(query, max_results=max_results)


def main():
    parser = argparse.ArgumentParser(description="Search DuckDuckGo for web results")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of results (default: 5)")
    parser.add_argument("--region", default="us-en", help="Region/language code (default: us-en)")
    parser.add_argument("--no-safe-search", action="store_true", help="Disable safe search")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    results = search_duckduckgo(
        query=args.query,
        max_results=args.max_results,
        region=args.region,
        safe_search=not args.no_safe_search
    )
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("No results found.")
            return
        
        print(f"Search results for: {args.query}")
        print("=" * 60)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            if result['snippet']:
                print(f"   {result['snippet']}")
        print("=" * 60)
        print(f"Total results: {len(results)}")


if __name__ == "__main__":
    main()