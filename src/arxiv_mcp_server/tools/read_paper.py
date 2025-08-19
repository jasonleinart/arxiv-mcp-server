"""Read functionality for the arXiv MCP server."""

import json
from pathlib import Path
from typing import Dict, Any, List
import mcp.types as types
from ..config import Settings

settings = Settings()

read_tool = types.Tool(
    name="read_paper",
    description="Read the full text content of a previously downloaded and converted research paper in clean markdown format. This tool retrieves the complete paper content including abstract, introduction, methodology, results, conclusions, and references. The content is formatted for easy reading and analysis, with preserved mathematical equations and structured sections. Use this tool when you need to access the full text of a paper for detailed study, quotation, analysis, or research. The paper must have been previously downloaded using the download_paper tool.",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv identifier of the paper to read (e.g., '2301.07041', '1706.03762'). This must be a paper that has been previously downloaded and converted to markdown format. Use list_papers to see available papers.",
                "pattern": "^(\\d{4}\\.\\d{4,5}(v\\d+)?|[a-z-]+(\\.[A-Z]{2})?/\\d{7}(v\\d+)?)$"
            }
        },
        "required": ["paper_id"],
        "additionalProperties": False
    },
)


def list_papers() -> list[str]:
    """List all stored paper IDs."""
    return [p.stem for p in Path(settings.STORAGE_PATH).glob("*.md")]


async def handle_read_paper(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle requests to read a paper's content."""
    try:
        paper_ids = list_papers()
        paper_id = arguments["paper_id"]
        # Check if paper exists
        if paper_id not in paper_ids:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "error",
                            "message": f"Paper {paper_id} not found in storage. You may need to download it first using download_paper.",
                        }
                    ),
                )
            ]

        # Get paper content
        content = Path(settings.STORAGE_PATH, f"{paper_id}.md").read_text(
            encoding="utf-8"
        )

        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "success",
                        "paper_id": paper_id,
                        "content": content,
                    }
                ),
            )
        ]

    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": f"Error reading paper: {str(e)}",
                    }
                ),
            )
        ]
