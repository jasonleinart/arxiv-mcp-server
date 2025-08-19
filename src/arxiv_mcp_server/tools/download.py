"""Download functionality for the arXiv MCP server."""

import arxiv
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import mcp.types as types
from ..config import Settings
import pymupdf4llm
import logging

logger = logging.getLogger("arxiv-mcp-server")
settings = Settings()

# Global dictionary to track conversion status
conversion_statuses: Dict[str, Any] = {}


@dataclass
class ConversionStatus:
    """Track the status of a PDF to Markdown conversion."""

    paper_id: str
    status: str  # 'downloading', 'converting', 'success', 'error'
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


download_tool = types.Tool(
    name="download_paper",
    description="Download and convert an arXiv paper to readable markdown format for analysis and reading. This tool fetches the PDF from arXiv, converts it to markdown using advanced text extraction, and stores it locally for immediate access. Use this tool when you need to read, analyze, or work with the full text content of a specific paper. The conversion process extracts text, preserves formatting, and handles mathematical equations. Returns the full paper content directly upon successful completion.",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv identifier of the paper to download (e.g., '2301.07041', '1706.03762', 'cs.AI/0301001'). This can be found in search results or arXiv URLs. The paper must exist on arXiv.",
                "pattern": "^(\\d{4}\\.\\d{4,5}(v\\d+)?|[a-z-]+(\\.[A-Z]{2})?/\\d{7}(v\\d+)?)$"
            },
            "check_status": {
                "type": "boolean",
                "description": "Set to true to only check the status of an ongoing or completed conversion without starting a new download. Use this to monitor long-running conversions or verify if a paper is already available.",
                "default": False
            },
        },
        "required": ["paper_id"],
    },
)


def get_paper_path(paper_id: str, suffix: str = ".md") -> Path:
    """Get the absolute file path for a paper with given suffix."""
    storage_path = Path(settings.STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path / f"{paper_id}{suffix}"


def convert_pdf_to_markdown(paper_id: str, pdf_path: Path) -> None:
    """Convert PDF to Markdown in a separate thread."""
    try:
        logger.info(f"Starting conversion for {paper_id}")
        markdown = pymupdf4llm.to_markdown(pdf_path, show_progress=False)
        md_path = get_paper_path(paper_id, ".md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        status = conversion_statuses.get(paper_id)
        if status:
            status.status = "success"
            status.completed_at = datetime.now()

        # Clean up PDF after successful conversion
        logger.info(f"Conversion completed for {paper_id}")

    except Exception as e:
        logger.error(f"Conversion failed for {paper_id}: {str(e)}")
        status = conversion_statuses.get(paper_id)
        if status:
            status.status = "error"
            status.completed_at = datetime.now()
            status.error = str(e)


async def handle_download(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle paper download and conversion requests."""
    try:
        paper_id = arguments["paper_id"]
        check_status = arguments.get("check_status", False)

        # If only checking status
        if check_status:
            status = conversion_statuses.get(paper_id)
            if not status:
                if get_paper_path(paper_id, ".md").exists():
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "success",
                                    "message": "Paper is ready",
                                    "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                                    "pdf_uri": f"https://arxiv.org/pdf/{paper_id}.pdf",
                                }
                            ),
                        )
                    ]
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "unknown",
                                "message": "No download or conversion in progress",
                            }
                        ),
                    )
                ]

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": status.status,
                            "started_at": status.started_at.isoformat(),
                            "completed_at": (
                                status.completed_at.isoformat()
                                if status.completed_at
                                else None
                            ),
                            "error": status.error,
                            "message": f"Paper conversion {status.status}",
                        }
                    ),
                )
            ]

        # Check if paper is already converted
        if get_paper_path(paper_id, ".md").exists():
            # Read the existing content to return it directly
            md_path = get_paper_path(paper_id, ".md")
            content = md_path.read_text(encoding="utf-8")
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "success",
                            "message": "Paper already available",
                            "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                            "pdf_uri": f"https://arxiv.org/pdf/{paper_id}.pdf",
                            "content": content,
                        }
                    ),
                )
            ]

        # Check if already in progress
        if paper_id in conversion_statuses:
            status = conversion_statuses[paper_id]
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": status.status,
                            "message": f"Paper conversion {status.status}",
                            "started_at": status.started_at.isoformat(),
                        }
                    ),
                )
            ]

        # Start new download and conversion
        pdf_path = get_paper_path(paper_id, ".pdf")
        client = arxiv.Client()

        # Initialize status
        conversion_statuses[paper_id] = ConversionStatus(
            paper_id=paper_id, status="downloading", started_at=datetime.now()
        )

        # Download PDF
        paper = next(client.results(arxiv.Search(id_list=[paper_id])))
        paper.download_pdf(dirpath=pdf_path.parent, filename=pdf_path.name)

        # Update status and start conversion
        status = conversion_statuses[paper_id]
        status.status = "converting"

        # Start conversion in background task and return immediately
        asyncio.create_task(asyncio.to_thread(convert_pdf_to_markdown, paper_id, pdf_path))
        
        # Return status indicating conversion has started
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "converting",
                        "message": "Paper download completed, conversion started in background. Use check_status=true to monitor progress.",
                        "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                        "pdf_uri": f"https://arxiv.org/pdf/{paper_id}.pdf",
                        "started_at": status.started_at.isoformat(),
                    }
                ),
            )
        ]

    except StopIteration:
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": f"Paper {paper_id} not found on arXiv",
                    }
                ),
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"Error: {str(e)}"}),
            )
        ]
