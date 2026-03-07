#!/usr/bin/env python3
"""
Simple DuckDuckGo Web Search Script

This script performs web searches using DuckDuckGo's Instant Answer API.
It's simpler and doesn't require BeautifulSoup.

Usage:
    python simple_search.py "search query" [--max-results 5]

Example:
    python simple_search.py "Python programming" --max-results 3
"""

import argparse
import json
import sys
from typing import Dict, List, Optional

import requests


def search_duckduckgo_api(
    query: str, 
    max_results: int = 5
) -> List[Dict[str, str]]:
    """
    Perform a DuckDuckGo search using the Instant Answer API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with keys: 'title', 'url', 'snippet'
    """
    base_url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return []
    
    results = []
    
    # Check for instant answer
    if data.get("AbstractText"):
        results.append({
            'title': data.get("Heading", "Instant Answer"),
            'url': data.get("AbstractURL", ""),
            'snippet': data.get("AbstractText", ""),
            'type': 'instant_answer'
        })
    
    # Check for related topics
    for topic in data.get("RelatedTopics", [])[:max_results]:
        if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
            results.append({
                'title': topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", ""),
                'url': topic.get("FirstURL", ""),
                'snippet': topic.get("Text", ""),
                'type': 'related_topic'
            })
        elif isinstance(topic, dict) and "Topics" in topic:
            # Nested topics
            for subtopic in topic.get("Topics", [])[:max_results]:
                if "Text" in subtopic and "FirstURL" in subtopic:
                    results.append({
                        'title': subtopic.get("Text", "").split(" - ")[0] if " - " in subtopic.get("Text", "") else subtopic.get("Text", ""),
                        'url': subtopic.get("FirstURL", ""),
                        'snippet': subtopic.get("Text", ""),
                        'type': 'related_topic'
                    })
    
    # If no results from API, try a fallback HTML search
    if not results:
        return search_duckduckgo_html_fallback(query, max_results)
    
    return results[:max_results]


def search_duckduckgo_html_fallback(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Fallback method using HTML search when API doesn't return good results.
    This is a simpler version that doesn't require BeautifulSoup.
    """
    base_url = "https://duckduckgo.com/html/"
    params = {
        "q": query,
        "kl": "us-en",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        print(f"Error in fallback search: {e}", file=sys.stderr)
        return []
    
    # Simple text parsing (less reliable but works without BeautifulSoup)
    results = []
    
    # Look for result patterns in HTML
    lines = html_content.split('\n')
    for i, line in enumerate(lines):
        if 'class="result__title"' in line and i + 2 < len(lines):
            # Try to extract title and URL
            title_line = line
            url_line = lines[i + 1] if i + 1 < len(lines) else ""
            snippet_line = lines[i + 2] if i + 2 < len(lines) else ""
            
            # Extract title (simplified)
            title_start = title_line.find('>')
            title_end = title_line.find('</a>')
            if title_start > 0 and title_end > title_start:
                title = title_line[title_start + 1:title_end].strip()
                
                # Extract URL (simplified)
                href_start = title_line.find('href="')
                if href_start > 0:
                    href_end = title_line.find('"', href_start + 6)
                    if href_end > 0:
                        url = title_line[href_start + 6:href_end]
                        
                        # Extract snippet (simplified)
                        snippet = ""
                        if 'class="result__snippet"' in snippet_line:
                            snippet_start = snippet_line.find('>')
                            snippet_end = snippet_line.find('</a>')
                            if snippet_start > 0 and snippet_end > snippet_start:
                                snippet = snippet_line[snippet_start + 1:snippet_end].strip()
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'type': 'html_fallback'
                        })
    
    return results[:max_results]


def search_web(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Main search function for general use.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with keys: 'title', 'url', 'snippet', 'type'
    """
    return search_duckduckgo_api(query, max_results=max_results)


def main():
    parser = argparse.ArgumentParser(description="Search DuckDuckGo for web results")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=3, help="Maximum number of results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    results = search_web(query=args.query, max_results=args.max_results)
    
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
                # Truncate long snippets
                snippet = result['snippet']
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                print(f"   {snippet}")
        print("=" * 60)
        print(f"Total results: {len(results)}")


if __name__ == "__main__":
    main()