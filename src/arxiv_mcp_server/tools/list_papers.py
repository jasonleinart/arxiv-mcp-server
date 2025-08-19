"""List functionality for the arXiv MCP server."""

import json
from pathlib import Path
import arxiv
from typing import Dict, Any, List, Optional
import mcp.types as types
from ..config import Settings

settings = Settings()

list_tool = types.Tool(
    name="list_papers",
    description="List all previously downloaded and converted papers that are available in local storage for immediate reading and analysis. This tool shows you what papers you already have access to without needing to download them again. Each paper in the list includes metadata like title, authors, abstract, and direct links. Use this tool to see your paper library, check if a specific paper is already downloaded, or browse previously acquired research papers before downloading new ones.",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    },
)


def list_papers() -> list[str]:
    """List all stored paper IDs."""
    return [p.stem for p in Path(settings.STORAGE_PATH).glob("*.md")]


async def handle_list_papers(
    arguments: Optional[Dict[str, Any]] = None,
) -> List[types.TextContent]:
    """Handle requests to list all stored papers."""
    try:
        papers = list_papers()

        client = arxiv.Client()

        results = client.results(arxiv.Search(id_list=papers))

        response_data = {
            "total_papers": len(papers),
            "papers": [
                {
                    "title": result.title,
                    "summary": result.summary,
                    "authors": [author.name for author in result.authors],
                    "links": [link.href for link in result.links],
                    "pdf_url": result.pdf_url,
                }
                for result in results
            ],
        }

        return [
            types.TextContent(type="text", text=json.dumps(response_data, indent=2))
        ]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
