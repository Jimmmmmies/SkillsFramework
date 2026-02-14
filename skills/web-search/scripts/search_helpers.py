#!/usr/bin/env python3
"""
Web Search Helper Functions

This script provides utility functions for web searching and information gathering.
These functions can be used to automate common search tasks and information processing.

Note: This script requires internet access and appropriate Python packages.
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import urllib.parse


class SearchHelper:
    """Helper class for web search operations"""
    
    @staticmethod
    def construct_google_query(
        keywords: List[str],
        exact_phrases: Optional[List[str]] = None,
        exclude_words: Optional[List[str]] = None,
        site_restrictions: Optional[List[str]] = None,
        file_types: Optional[List[str]] = None,
        date_range: Optional[Tuple[str, str]] = None
    ) -> str:
        """
        Construct a Google search query with proper operators.
        
        Args:
            keywords: List of main search keywords
            exact_phrases: List of exact phrases to search (in quotes)
            exclude_words: List of words to exclude (prefixed with -)
            site_restrictions: List of sites to restrict to (site:example.com)
            file_types: List of file types to search (filetype:pdf)
            date_range: Tuple of (start_date, end_date) in YYYY-MM-DD format
            
        Returns:
            Formatted search query string
        """
        query_parts = []
        
        # Add keywords
        query_parts.extend(keywords)
        
        # Add exact phrases in quotes
        if exact_phrases:
            query_parts.extend([f'"{phrase}"' for phrase in exact_phrases])
        
        # Add site restrictions
        if site_restrictions:
            query_parts.extend([f'site:{site}' for site in site_restrictions])
        
        # Add file type restrictions
        if file_types:
            query_parts.extend([f'filetype:{ft}' for ft in file_types])
        
        # Add date range if provided
        if date_range:
            start_date, end_date = date_range
            query_parts.append(f'after:{start_date}')
            query_parts.append(f'before:{end_date}')
        
        # Add exclude words (prefixed with -)
        if exclude_words:
            query_parts.extend([f'-{word}' for word in exclude_words])
        
        return ' '.join(query_parts)
    
    @staticmethod
    def construct_academic_query(
        topic: str,
        years: Optional[Tuple[int, int]] = None,
        authors: Optional[List[str]] = None,
        publication_types: Optional[List[str]] = None
    ) -> str:
        """
        Construct a query for academic search engines.
        
        Args:
            topic: Main research topic
            years: Tuple of (start_year, end_year)
            authors: List of author names
            publication_types: List of publication types (article, review, etc.)
            
        Returns:
            Formatted academic search query
        """
        query_parts = [topic]
        
        # Add year range
        if years:
            start_year, end_year = years
            query_parts.append(f'{start_year}..{end_year}')
        
        # Add authors
        if authors:
            for author in authors:
                query_parts.append(f'author:"{author}"')
        
        # Add publication types
        if publication_types:
            type_query = ' OR '.join(publication_types)
            query_parts.append(f'({type_query})')
        
        return ' '.join(query_parts)
    
    @staticmethod
    def parse_search_results_summary(results_text: str) -> Dict:
        """
        Parse a text summary of search results into structured data.
        
        Args:
            results_text: Text containing search results summary
            
        Returns:
            Dictionary with parsed information
        """
        # This is a simplified parser - in practice, you'd use more sophisticated
        # parsing or API calls to search engines
        
        parsed = {
            'total_results': 0,
            'sources': [],
            'key_topics': [],
            'date_range': None
        }
        
        # Extract potential numbers (simplified)
        number_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+results'
        match = re.search(number_pattern, results_text, re.IGNORECASE)
        if match:
            try:
                parsed['total_results'] = int(match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # Extract potential sources (simplified)
        source_keywords = ['wikipedia', 'news', 'journal', 'study', 'report', 'article']
        for keyword in source_keywords:
            if keyword in results_text.lower():
                parsed['sources'].append(keyword)
        
        # Extract dates (simplified)
        date_pattern = r'(\d{4})'
        dates = re.findall(date_pattern, results_text)
        if len(dates) >= 2:
            parsed['date_range'] = (min(dates), max(dates))
        
        return parsed
    
    @staticmethod
    def generate_search_strategy(
        topic: str,
        search_type: str = "general",
        depth: str = "comprehensive"
    ) -> Dict:
        """
        Generate a search strategy for a given topic.
        
        Args:
            topic: The topic to research
            search_type: Type of search ("general", "academic", "technical", "news")
            depth: Search depth ("quick", "standard", "comprehensive")
            
        Returns:
            Dictionary with search strategy
        """
        strategies = {
            "general": {
                "quick": [
                    f'"{topic}" overview',
                    f'"{topic}" basics',
                    f'what is {topic}'
                ],
                "standard": [
                    f'"{topic}" explained',
                    f'"{topic}" guide',
                    f'understanding {topic}',
                    f'{topic} applications'
                ],
                "comprehensive": [
                    f'"{topic}" comprehensive guide',
                    f'"{topic}" deep dive',
                    f'{topic} fundamentals advanced',
                    f'{topic} history development',
                    f'{topic} future trends'
                ]
            },
            "academic": {
                "quick": [
                    f'"{topic}" review',
                    f'"{topic}" survey',
                    f'{topic} research overview'
                ],
                "standard": [
                    f'"{topic}" literature review',
                    f'{topic} state of the art',
                    f'{topic} recent developments',
                    f'{topic} challenges opportunities'
                ],
                "comprehensive": [
                    f'"{topic}" systematic review',
                    f'{topic} meta-analysis',
                    f'{topic} research gaps',
                    f'{topic} future research directions',
                    f'{topic} seminal papers'
                ]
            },
            "technical": {
                "quick": [
                    f'{topic} tutorial',
                    f'{topic} getting started',
                    f'{topic} examples'
                ],
                "standard": [
                    f'{topic} documentation',
                    f'{topic} best practices',
                    f'{topic} implementation',
                    f'{topic} troubleshooting'
                ],
                "comprehensive": [
                    f'{topic} advanced techniques',
                    f'{topic} performance optimization',
                    f'{topic} architecture design',
                    f'{topic} security considerations'
                ]
            },
            "news": {
                "quick": [
                    f'{topic} latest news',
                    f'{topic} recent developments',
                    f'{topic} 2024'
                ],
                "standard": [
                    f'{topic} current events',
                    f'{topic} breaking news',
                    f'{topic} updates',
                    f'{topic} analysis'
                ],
                "comprehensive": [
                    f'{topic} in-depth reporting',
                    f'{topic} investigative',
                    f'{topic} timeline',
                    f'{topic} background context'
                ]
            }
        }
        
        if search_type not in strategies:
            search_type = "general"
        if depth not in strategies[search_type]:
            depth = "standard"
        
        return {
            "topic": topic,
            "search_type": search_type,
            "depth": depth,
            "queries": strategies[search_type][depth],
            "suggested_sources": SearchHelper._get_suggested_sources(search_type)
        }
    
    @staticmethod
    def _get_suggested_sources(search_type: str) -> List[str]:
        """Get suggested sources based on search type."""
        sources = {
            "general": [
                "Wikipedia for overview",
                "Educational websites (Khan Academy, etc.)",
                "Reputable news sources for current context"
            ],
            "academic": [
                "Google Scholar",
                "PubMed (for medical/biological)",
                "arXiv (for physics/math/CS)",
                "University repositories"
            ],
            "technical": [
                "Official documentation",
                "GitHub repositories",
                "Stack Overflow",
                "Technical blogs"
            ],
            "news": [
                "Reuters, AP, BBC for breaking news",
                "Specialized industry publications",
                "Local news sources for regional context"
            ]
        }
        return sources.get(search_type, sources["general"])
    
    @staticmethod
    def evaluate_source_url(url: str) -> Dict:
        """
        Evaluate a source URL for reliability indicators.
        
        Args:
            url: The URL to evaluate
            
        Returns:
            Dictionary with evaluation metrics
        """
        evaluation = {
            "url": url,
            "domain_trust": "unknown",
            "likely_content_type": "unknown",
            "red_flags": [],
            "green_flags": []
        }
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check domain extensions
            if domain.endswith('.gov'):
                evaluation["domain_trust"] = "high"
                evaluation["green_flags"].append("Government domain (.gov)")
            elif domain.endswith('.edu'):
                evaluation["domain_trust"] = "high"
                evaluation["green_flags"].append("Educational domain (.edu)")
            elif domain.endswith('.org'):
                evaluation["domain_trust"] = "medium"
                evaluation["green_flags"].append("Organization domain (.org)")
            elif domain.endswith('.com'):
                evaluation["domain_trust"] = "variable"
            
            # Check for common reliable domains
            reliable_domains = [
                'wikipedia.org',
                'nih.gov',
                'nasa.gov',
                'bbc.com',
                'reuters.com',
                'arxiv.org',
                'github.com'
            ]
            
            for reliable in reliable_domains:
                if reliable in domain:
                    evaluation["domain_trust"] = "high"
                    evaluation["green_flags"].append(f"Known reliable domain: {reliable}")
                    break
            
            # Check for potential issues
            suspicious_patterns = [
                'clickbait',
                'sensational',
                'fake',
                'hoax',
                'conspiracy'
            ]
            
            for pattern in suspicious_patterns:
                if pattern in domain or pattern in url.lower():
                    evaluation["red_flags"].append(f"Suspicious pattern: {pattern}")
            
            # Guess content type from URL path
            path = parsed.path.lower()
            if any(ext in path for ext in ['.pdf', '.doc', '.docx']):
                evaluation["likely_content_type"] = "document"
            elif any(keyword in path for keyword in ['/article/', '/news/', '/blog/']):
                evaluation["likely_content_type"] = "article"
            elif any(keyword in path for keyword in ['/research/', '/study/', '/paper/']):
                evaluation["likely_content_type"] = "research"
            elif any(keyword in path for keyword in ['/data/', '/dataset/', '/statistics/']):
                evaluation["likely_content_type"] = "data"
            
        except Exception as e:
            evaluation["red_flags"].append(f"URL parsing error: {str(e)}")
        
        return evaluation
    
    @staticmethod
    def format_search_results(
        results: List[Dict],
        include_evaluation: bool = True
    ) -> str:
        """
        Format search results into a readable summary.
        
        Args:
            results: List of result dictionaries with keys like 'title', 'url', 'snippet'
            include_evaluation: Whether to include source evaluation
            
        Returns:
            Formatted results summary
        """
        if not results:
            return "No results found."
        
        formatted = []
        formatted.append(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('title', 'No title')}")
            formatted.append(f"   URL: {result.get('url', 'No URL')}")
            
            if 'snippet' in result:
                snippet = result['snippet']
                if len(snippet) > 150:
                    snippet = snippet[:147] + "..."
                formatted.append(f"   Preview: {snippet}")
            
            if include_evaluation and 'url' in result:
                eval_result = SearchHelper.evaluate_source_url(result['url'])
                if eval_result['green_flags']:
                    formatted.append(f"   ✓ {', '.join(eval_result['green_flags'][:2])}")
                if eval_result['red_flags']:
                    formatted.append(f"   ⚠ {', '.join(eval_result['red_flags'][:2])}")
            
            formatted.append("")  # Empty line between results
        
        return '\n'.join(formatted)


def main():
    """Example usage of the SearchHelper class."""
    print("Web Search Helper Examples")
    print("=" * 50)
    
    # Example 1: Construct a Google query
    query = SearchHelper.construct_google_query(
        keywords=["machine learning", "healthcare"],
        exact_phrases=["predictive modeling"],
        site_restrictions=["nih.gov", "arxiv.org"],
        file_types=["pdf"],
        date_range=("2022-01-01", "2024-01-01")
    )
    print(f"Example Google query:\n{query}\n")
    
    # Example 2: Generate search strategy
    strategy = SearchHelper.generate_search_strategy(
        topic="quantum computing",
        search_type="academic",
        depth="comprehensive"
    )
    print("Example search strategy for 'quantum computing':")
    print(f"Type: {strategy['search_type']}, Depth: {strategy['depth']}")
    print("Suggested queries:")
    for q in strategy['queries']:
        print(f"  - {q}")
    print()
    
    # Example 3: Evaluate a URL
    test_urls = [
        "https://www.nih.gov/research-training/medical-research-initiatives",
        "https://arxiv.org/abs/2301.12345",
        "https://example-sensational-news.com/breaking-hoax"
    ]
    
    print("URL evaluations:")
    for url in test_urls:
        evaluation = SearchHelper.evaluate_source_url(url)
        print(f"\n{url}")
        print(f"  Trust level: {evaluation['domain_trust']}")
        if evaluation['green_flags']:
            print(f"  Green flags: {', '.join(evaluation['green_flags'])}")
        if evaluation['red_flags']:
            print(f"  Red flags: {', '.join(evaluation['red_flags'])}")


if __name__ == "__main__":
    main()