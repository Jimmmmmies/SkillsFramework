---
name: web-search
description: |
  Comprehensive web searching and information gathering skill. Use when Claude needs to search the web,
  gather current information, find sources, or verify facts. This skill provides structured approaches
  for effective web research, source evaluation, and information synthesis. Trigger when users ask for
  current information, need to verify facts, require up-to-date data, or want to gather multiple sources
  on a topic.
---

# Web Search Skill

## Overview

This skill provides comprehensive guidance for conducting effective web searches and gathering reliable information. It covers search strategies, source evaluation, information synthesis, and best practices for web research.

## Core Principles

### 1. Search Strategy First
Always start with a clear search strategy before executing queries. Consider:
- What specific information is needed?
- What keywords will yield the best results?
- Which sources are most likely to have reliable information?
- What time frame is relevant (current vs historical)?

### 2. Source Evaluation
Not all sources are created equal. Evaluate sources based on:
- **Authority**: Who created the content? What are their credentials?
- **Accuracy**: Is the information supported by evidence?
- **Currency**: When was the information published/updated?
- **Purpose**: Why was the information created (inform, persuade, sell)?
- **Bias**: What perspectives might be missing or overrepresented?

### 3. Information Synthesis
Combine information from multiple sources to build a comprehensive understanding:
- Look for consensus among reliable sources
- Note conflicting information and investigate why
- Consider different perspectives and contexts
- Distinguish between facts, opinions, and interpretations

## Search Techniques

### Basic Search Operators

**Google/DuckDuckGo Operators:**
- `"exact phrase"` - Search for exact phrase
- `site:example.com` - Search within specific site
- `filetype:pdf` - Search for specific file types
- `-excludeword` - Exclude terms from results
- `intitle:keyword` - Search in page titles
- `inurl:keyword` - Search in URLs
- `related:example.com` - Find related sites
- `before:2023` / `after:2022` - Date range searches

**Advanced Techniques:**
- **Boolean operators**: `AND`, `OR`, `NOT` (or `+`, `|`, `-`)
- **Wildcards**: `*` for unknown words (e.g., "best * for beginners")
- **Range searches**: `2020..2023` for number ranges
- **Cache view**: `cache:example.com` to see cached version

### Search Strategy Patterns

**1. Broad to Narrow:**
- Start with general terms to understand the landscape
- Gradually add specific terms to narrow results
- Example: "artificial intelligence" → "AI in healthcare" → "AI diagnostic tools 2024"

**2. Question-Based Searching:**
- Frame searches as questions for more targeted results
- Example: "How does blockchain work?" vs "blockchain technology"

**3. Source-Specific Searching:**
- Identify likely sources first, then search within them
- Example: For academic research, search `site:arxiv.org` or `site:scholar.google.com`

**4. Time-Constrained Searching:**
- Use date operators for current information
- Example: "COVID variants after:2023-12-01"

## Source Types and Reliability

### High Reliability Sources
- **Academic**: Peer-reviewed journals, university publications
- **Government**: .gov domains, official statistics, reports
- **Established News**: Major newspapers with editorial standards
- **Professional Organizations**: Industry associations, professional bodies
- **Primary Sources**: Original research, official documents, direct observations

### Medium Reliability Sources
- **Reputable Blogs**: Industry experts with transparent credentials
- **Company Websites**: Official information from established companies
- **Industry Publications**: Trade magazines, industry reports
- **Educational Platforms**: Khan Academy, Coursera, edX

### Low Reliability Sources
- **Personal Blogs/Social Media**: Unless from verified experts
- **Unverified Forums**: Reddit, Quora (check for expert verification)
- **Clickbait Sites**: Sensational headlines, excessive ads
- **Uncited Claims**: Information without supporting evidence

## Information Verification

### Fact-Checking Process
1. **Cross-reference**: Check multiple reliable sources
2. **Check dates**: Ensure information is current and relevant
3. **Verify sources**: Trace claims back to original sources
4. **Check for updates**: Look for corrections or recent developments
5. **Consider context**: Understand the broader context of information

### Red Flags
- Information only appears on one obscure site
- No publication date or author information
- Excessive emotional language or sensationalism
- Claims that contradict established knowledge without evidence
- Poor website design with excessive ads/popups

## Specialized Search Scenarios

### Academic Research
- Use Google Scholar, PubMed, arXiv, JSTOR
- Look for peer-reviewed articles
- Check citation counts and impact factors
- Review methodology sections carefully

### Technical Information
- Search documentation sites (`site:docs.example.com`)
- Use GitHub for code examples and issues
- Check Stack Overflow for specific problems
- Review official documentation and API references

### Current Events
- Use news aggregators with multiple sources
- Check timestamp of information
- Compare coverage across different outlets
- Look for official statements or press releases

### Statistical Data
- Government statistical agencies (.gov domains)
- International organizations (UN, World Bank, IMF)
- Academic research databases
- Industry reports from reputable firms

## Information Organization

### Note-Taking Structure
1. **Source Information**: URL, title, author, date, publication
2. **Key Points**: Main findings or claims
3. **Evidence**: Supporting data or quotes
4. **Context**: How this fits with other information
5. **Evaluation**: Reliability assessment and notes

### Synthesis Techniques
- Create comparison tables for different sources
- Identify consensus points and areas of disagreement
- Note gaps in information that need further research
- Organize information thematically or chronologically

## Common Pitfalls to Avoid

### 1. Confirmation Bias
- Actively seek information that challenges your assumptions
- Consider multiple perspectives on controversial topics
- Be aware of your own biases when evaluating sources

### 2. Recency Bias
- Don't assume newer information is always better
- Historical context is often important
- Some foundational information doesn't change frequently

### 3. Authority Bias
- Don't accept claims just because they come from "experts"
- Verify credentials and check for conflicts of interest
- Even reputable sources can make mistakes

### 4. Information Overload
- Set clear search boundaries and time limits
- Focus on the most relevant and reliable sources first
- Know when you have enough information to proceed

## Quick Reference Checklist

### Before Searching
- [ ] Define clear search objectives
- [ ] Identify key search terms and alternatives
- [ ] Determine appropriate source types
- [ ] Set time constraints if needed

### During Searching
- [ ] Use appropriate search operators
- [ ] Evaluate source reliability quickly
- [ ] Take organized notes
- [ ] Adjust strategy based on initial results

### After Searching
- [ ] Cross-reference information
- [ ] Verify key facts
- [ ] Synthesize findings
- [ ] Identify any remaining gaps

## Output Format

When providing search results or gathered information:

1. **Summary**: Brief overview of findings
2. **Sources**: List of sources with reliability indicators
3. **Key Information**: Main points from each source
4. **Synthesis**: Combined understanding from all sources
5. **Gaps/Uncertainties**: Areas needing further research
6. **Recommendations**: Suggested next steps or additional searches

---

## Example Workflows

### Example 1: Current Technology Research
**User Request**: "Find current information about quantum computing advancements in 2024"

**Search Strategy:**
1. Start with broad search: "quantum computing 2024"
2. Narrow to specific aspects: "quantum supremacy 2024", "quantum error correction recent"
3. Search academic sources: `site:arxiv.org quantum computing 2024`
4. Check industry news: "IBM quantum 2024", "Google quantum 2024"

**Source Evaluation:**
- Prioritize peer-reviewed papers and official company announcements
- Cross-reference claims across multiple sources
- Check dates to ensure information is current

### Example 2: Fact Verification
**User Request**: "Verify claims about climate change impacts"

**Verification Process:**
1. Find original source of claims
2. Search scientific databases for supporting/contradicting evidence
3. Check consensus among climate scientists
4. Review reports from IPCC and other authoritative bodies
5. Compare with historical data and trends

### Example 3: Market Research
**User Request**: "Gather information about electric vehicle market trends"

**Research Approach:**
1. Industry reports from consulting firms
2. Government energy department statistics
3. Company financial reports and announcements
4. Academic research on EV technology
5. News coverage of major developments

---

**Remember**: The goal of web searching is not just to find information, but to find *reliable* information that helps answer questions and solve problems effectively.