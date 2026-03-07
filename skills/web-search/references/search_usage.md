# DuckDuckGo Web Search Usage Guide

## Overview

This skill provides web searching capabilities using DuckDuckGo. It includes both API-based search and HTML fallback methods.

## Available Search Methods

### 1. API Search (`search_duckduckgo_api`)
- Uses DuckDuckGo's Instant Answer API
- Returns structured JSON data
- Includes instant answers and related topics
- Fast and reliable for most queries

### 2. HTML Fallback Search (`search_duckduckgo_html_fallback`)
- Uses DuckDuckGo's HTML interface
- Works when API doesn't return good results
- More comprehensive web search results
- Slightly slower but more thorough

### 3. Main Search Function (`search_web`)
- Primary function for general use
- Automatically chooses the best method
- Returns consistent result format

## Result Format

All search functions return a list of dictionaries with the following structure:

```python
[
    {
        "title": "Result Title",
        "url": "https://example.com",
        "snippet": "Brief description or excerpt",
        "type": "instant_answer|related_topic|html_fallback"
    },
    # ... more results
]
```

## Usage Examples

### Python Code Examples

```python
from simple_search import search_web

# Basic search
results = search_web("Python programming tutorials", max_results=3)

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet'][:100]}...")
    print()
```

### Command Line Usage

```bash
# Basic search with 3 results
python simple_search.py "machine learning algorithms"

# Search with 5 results
python simple_search.py "Python web frameworks" --max-results 5

# Output as JSON for programmatic use
python simple_search.py "data science" --json

# Using the advanced search script (requires BeautifulSoup)
python duckduckgo_search.py "artificial intelligence" --max-results 3 --region us-en
```

## Common Search Patterns

### 1. Factual Queries
```bash
python simple_search.py "capital of France"
# Returns instant answer: Paris
```

### 2. Technical Information
```bash
python simple_search.py "Python requests library documentation"
# Returns official docs and tutorials
```

### 3. News and Current Events
```bash
python simple_search.py "latest technology news 2024"
# Returns recent articles and news sources
```

### 4. How-to Guides
```bash
python simple_search.py "how to install Python on Windows"
# Returns step-by-step guides
```

## Best Practices

1. **Be Specific**: Use specific search terms for better results
2. **Use Quotes**: For exact phrase matching (handled automatically)
3. **Limit Results**: Use `max_results` parameter to control output size
4. **Check URLs**: Always verify URLs before visiting
5. **Combine Sources**: Use multiple results for comprehensive information

## Error Handling

The search functions include error handling for:
- Network connectivity issues
- API rate limiting
- Invalid responses
- Timeout scenarios

If search fails, the function returns an empty list.

## Integration with Claude

When using this skill with Claude, you can:

1. **Direct Script Execution**: Run search scripts via bash tool
2. **Python Integration**: Import and use search functions in Python code
3. **Result Processing**: Parse and analyze search results for specific information
4. **Multi-query Search**: Combine multiple searches for comprehensive research

## Example Claude Workflow

```
User: Search for information about renewable energy sources

Claude can:
1. Run: python simple_search.py "renewable energy sources types" --max-results 5
2. Analyze results to extract key information
3. Summarize findings
4. Follow up with more specific searches if needed
```

## Notes

- DuckDuckGo respects user privacy and doesn't track searches
- Results may vary based on region and language settings
- Some queries may trigger instant answers (concise summaries)
- The API has rate limits; use responsibly