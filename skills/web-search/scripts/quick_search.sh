#!/bin/bash
# Quick Search Helper Script
# Provides command-line utilities for common web search tasks

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    echo -e "${BLUE}Quick Search Helper Script${NC}"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  google [query]        - Open Google search in browser"
    echo "  scholar [query]       - Open Google Scholar search"
    echo "  github [query]        - Search GitHub"
    echo "  stack [query]         - Search Stack Overflow"
    echo "  wiki [query]          - Search Wikipedia"
    echo "  news [query]          - Search Google News"
    echo "  youtube [query]       - Search YouTube"
    echo "  help                  - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 google \"machine learning tutorial\""
    echo "  $0 scholar \"quantum computing 2024\""
    echo "  $0 github \"python flask example\""
    echo ""
    echo "Note: This script opens search results in your default web browser."
}

# Function to URL encode a string
urlencode() {
    local string="${1}"
    local length="${#string}"
    local encoded=""
    local i char

    for (( i = 0; i < length; i++ )); do
        char="${string:$i:1}"
        case "$char" in
            [a-zA-Z0-9.~_-]) encoded+="$char" ;;
            *) encoded+=$(printf '%%%02X' "'$char") ;;
        esac
    done
    echo "$encoded"
}

# Function to open Google search
google_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://www.google.com/search?q=${encoded_query}"
    
    echo -e "${GREEN}Searching Google for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Function to open Google Scholar search
scholar_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://scholar.google.com/scholar?q=${encoded_query}"
    
    echo -e "${GREEN}Searching Google Scholar for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Function to search GitHub
github_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://github.com/search?q=${encoded_query}"
    
    echo -e "${GREEN}Searching GitHub for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Function to search Stack Overflow
stack_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://stackoverflow.com/search?q=${encoded_query}"
    
    echo -e "${GREEN}Searching Stack Overflow for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Function to search Wikipedia
wiki_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://en.wikipedia.org/w/index.php?search=${encoded_query}"
    
    echo -e "${GREEN}Searching Wikipedia for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Function to search Google News
news_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://news.google.com/search?q=${encoded_query}"
    
    echo -e "${GREEN}Searching Google News for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Function to search YouTube
youtube_search() {
    local query="$*"
    local encoded_query=$(urlencode "$query")
    local url="https://www.youtube.com/results?search_query=${encoded_query}"
    
    echo -e "${GREEN}Searching YouTube for:${NC} $query"
    echo -e "${BLUE}URL:${NC} $url"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url"
    elif command -v open &> /dev/null; then
        open "$url"
    elif command -v start &> /dev/null; then
        start "$url"
    else
        echo -e "${YELLOW}Could not detect browser opener. Please open the URL manually.${NC}"
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

COMMAND="$1"
shift
QUERY="$*"

case "$COMMAND" in
    "google")
        google_search "$QUERY"
        ;;
    "scholar")
        scholar_search "$QUERY"
        ;;
    "github")
        github_search "$QUERY"
        ;;
    "stack")
        stack_search "$QUERY"
        ;;
    "wiki")
        wiki_search "$QUERY"
        ;;
    "news")
        news_search "$QUERY"
        ;;
    "youtube")
        youtube_search "$QUERY"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac