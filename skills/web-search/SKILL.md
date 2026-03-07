---
name: web-search
description: "Perform web searches using DuckDuckGo to find information, answer questions, and gather data from the internet. Use when Claude needs to: (1) Search for current information or facts, (2) Find documentation or tutorials, (3) Research topics or gather data, (4) Look up news or recent developments, (5) Find websites or resources on specific subjects. This skill provides privacy-focused web searching without tracking."
---
# Web Search Skill

## Overview

This skill enables Claude to perform web searches using DuckDuckGo, a privacy-focused search engine. It provides both API-based search and HTML fallback methods to retrieve web results including titles, URLs, and snippets.

## Quick Start

To perform a basic web search:

```bash
# Using the simple search script (recommended)
python scripts/simple_search.py "your search query" --max-results 3

# Using the advanced search script (requires BeautifulSoup)
python scripts/duckduckgo_search.py "your search query" --max-results 5
```

## Search Methods

### 1. Simple Search (Recommended)
The `simple_search.py` script uses DuckDuckGo's Instant Answer API and includes a fallback HTML parser. It doesn't require additional dependencies beyond `requests`.

**Features:**
- Instant answers for factual queries
- Related topics and web results
- Automatic fallback to HTML search
- Consistent JSON output format

### 2. Advanced Search
The `duckduckgo_search.py` script uses BeautifulSoup for more robust HTML parsing. It requires `beautifulsoup4` and `requests`.

**Features:**
- More comprehensive web search results
- Better snippet extraction
- Region and safe search controls
- Detailed result parsing

## How to Use This Skill

### Basic Search Workflow

1. **Identify the search need**: Determine what information you need to find
2. **Formulate the query**: Create specific, clear search terms
3. **Execute the search**: Run the appropriate search script
4. **Analyze results**: Review titles, URLs, and snippets
5. **Extract information**: Gather relevant data from results
6. **Follow up if needed**: Perform additional searches for more information

### Common Search Patterns

#### Factual Information
```bash
python scripts/simple_search.py "population of Tokyo" --max-results 2
```

#### Technical Documentation
```bash
python scripts/simple_search.py "Python requests library POST example" --max-results 3
```

#### News and Current Events
```bash
python scripts/simple_search.py "latest AI developments 2024" --max-results 4
```

#### How-to Guides
```bash
python scripts/simple_search.py "how to set up Python virtual environment" --max-results 3
```

### Integration with Claude's Workflow

When Claude needs to search the web:

1. **Direct execution**: Use the `bash` tool to run search scripts
2. **Result processing**: Parse JSON output or text results
3. **Information synthesis**: Combine multiple search results
4. **Citation**: Include URLs when referencing information

## Script Details

### simple_search.py
- **Dependencies**: Only `requests` (already available)
- **Output**: JSON or formatted text
- **Best for**: Most search needs, quick results

### duckduckgo_search.py  
- **Dependencies**: `beautifulsoup4` and `requests`
- **Output**: JSON or formatted text
- **Best for**: Comprehensive web searches, detailed results

## Result Format

Search results are returned as a list of dictionaries:

```python
[
    {
        "title": "Result Title",
        "url": "https://example.com/path",
        "snippet": "Brief description or excerpt from the page",
        "type": "instant_answer|related_topic|html_fallback"
    }
]
```

## Best Practices

1. **Be Specific**: Use precise search terms for better results
2. **Use Appropriate max_results**: Start with 3-5 results, increase if needed
3. **Verify URLs**: Check domain credibility before using information
4. **Combine Sources**: Use multiple results to verify information
5. **Respect Privacy**: DuckDuckGo doesn't track searches - maintain this privacy focus

## Error Handling

- Network errors return empty results
- Invalid queries may return fewer results
- API rate limits are handled gracefully
- Timeouts are set to 10 seconds

## Examples of When to Use This Skill

### Scenario 1: Answering Current Questions
**User**: "What's the latest version of Python?"
**Claude Action**: Search for "Python latest version release date"

### Scenario 2: Finding Documentation
**User**: "How do I use the pandas groupby function?"
**Claude Action**: Search for "pandas groupby function examples tutorial"

### Scenario 3: Research Topics
**User**: "Tell me about renewable energy sources"
**Claude Action**: Search for "types of renewable energy sources pros and cons"

### Scenario 4: Technical Troubleshooting
**User**: "I'm getting a 'module not found' error in Python"
**Claude Action**: Search for the specific error message

## Resources

For detailed usage examples and API documentation, see:
- [Search Usage Guide](references/search_usage.md) - Comprehensive guide with examples

## Notes

- DuckDuckGo is privacy-focused and doesn't track searches
- Results may vary based on region (default: us-en)
- Some queries trigger instant answers (concise summaries)
- Always verify critical information from multiple sources