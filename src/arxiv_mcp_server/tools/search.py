"""Search functionality for the arXiv MCP server."""

import arxiv
import json
from typing import Dict, Any, List
from datetime import datetime, timezone
from dateutil import parser
import mcp.types as types
from ..config import Settings

settings = Settings()

search_tool = types.Tool(
    name="search_papers",
    description="Search for academic research papers on arXiv.org using advanced filtering capabilities. This tool allows you to find papers by keywords, authors, categories, and date ranges. Use this when you need to discover relevant research papers on a specific topic, find papers by a particular author, or explore recent publications in a field. The search automatically enhances plain text queries for better relevance and supports arXiv's field-specific search syntax.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search terms for finding papers. Can be plain text (e.g., 'transformer architecture'), quoted phrases (e.g., '\"attention mechanism\"'), or arXiv field syntax (e.g., 'ti:transformer' for title search). The tool automatically optimizes simple queries for better results."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of papers to return (default: 10, maximum: 100). Use smaller numbers for quick overviews, larger numbers for comprehensive searches.",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            },
            "date_from": {
                "type": "string",
                "description": "Start date for paper publication filtering in ISO format (e.g., '2023-01-01' or '2023-06-15T10:30:00Z'). Only papers published on or after this date will be included."
            },
            "date_to": {
                "type": "string",
                "description": "End date for paper publication filtering in ISO format (e.g., '2024-12-31' or '2024-06-15T10:30:00Z'). Only papers published on or before this date will be included."
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter papers by arXiv subject categories (e.g., ['cs.AI', 'cs.LG'] for AI and Machine Learning, ['math.CO', 'cs.DM'] for combinatorics and discrete math). Common categories include: cs.AI (Artificial Intelligence), cs.LG (Machine Learning), cs.CL (Computation and Language), cs.CV (Computer Vision), physics.* (Physics), math.* (Mathematics), stat.* (Statistics)."
            },
        },
        "required": ["query"],
    },
)


def _is_within_date_range(
    date: datetime, start: datetime | None, end: datetime | None
) -> bool:
    """Check if a date falls within the specified range."""
    if start and not start.tzinfo:
        start = start.replace(tzinfo=timezone.utc)
    if end and not end.tzinfo:
        end = end.replace(tzinfo=timezone.utc)

    if start and date < start:
        return False
    if end and date > end:
        return False
    return True


def _process_paper(paper: arxiv.Result) -> Dict[str, Any]:
    """Process paper information with resource URI."""
    return {
        "id": paper.get_short_id(),
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "abstract": paper.summary,
        "categories": paper.categories,
        "published": paper.published.isoformat(),
        "url": paper.pdf_url,
        "resource_uri": f"arxiv://{paper.get_short_id()}",
    }


async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle paper search requests.

    Automatically adds field specifiers to plain queries for better relevance.
    This fixes issue #33 where queries sorted by date returned irrelevant results.
    """
    try:
        client = arxiv.Client()
        max_results = min(int(arguments.get("max_results", 10)), settings.MAX_RESULTS)

        # Build search query with category filtering
        query = arguments["query"]

        # Add field specifier if not already present
        # This ensures the query actually searches the content
        if not any(field in query for field in ["all:", "ti:", "abs:", "au:", "cat:"]):
            # Convert plain query to use all: field for better results
            # Handle quoted phrases
            if '"' in query:
                # Keep quoted phrases intact
                query = f"all:{query}"
            else:
                # For unquoted multi-word queries, use AND operator
                terms = query.split()
                if len(terms) > 1:
                    query = " AND ".join(f"all:{term}" for term in terms)
                else:
                    query = f"all:{query}"

        if categories := arguments.get("categories"):
            category_filter = " OR ".join(f"cat:{cat}" for cat in categories)
            query = f"({query}) AND ({category_filter})"

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        # Process results with date filtering
        results = []
        try:
            date_from = (
                parser.parse(arguments["date_from"]).replace(tzinfo=timezone.utc)
                if "date_from" in arguments
                else None
            )
            date_to = (
                parser.parse(arguments["date_to"]).replace(tzinfo=timezone.utc)
                if "date_to" in arguments
                else None
            )
        except (ValueError, TypeError) as e:
            return [
                types.TextContent(
                    type="text", text=f"Error: Invalid date format - {str(e)}"
                )
            ]

        for paper in client.results(search):
            if _is_within_date_range(paper.published, date_from, date_to):
                results.append(_process_paper(paper))

            if len(results) >= max_results:
                break

        response_data = {"total_results": len(results), "papers": results}

        return [
            types.TextContent(type="text", text=json.dumps(response_data, indent=2))
        ]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
