"""Regression tests for stored paper listings."""

import json
from unittest.mock import patch

import pytest
from arxiv_mcp_server.tools import handle_list_papers


@pytest.mark.asyncio
async def test_empty_library_does_not_contact_arxiv():
    """An empty library returns immediately without an API client."""
    with patch(
        "arxiv_mcp_server.tools.list_papers.list_papers", return_value=[]
    ), patch("arxiv.Client") as client:
        result = await handle_list_papers({})
    assert json.loads(result[0].text) == {"total_papers": 0, "papers": []}
    client.assert_not_called()


@pytest.mark.asyncio
async def test_nonempty_library_keeps_metadata(mock_client, mock_paper):
    """Stored IDs still use the existing metadata lookup."""
    with patch(
        "arxiv_mcp_server.tools.list_papers.list_papers",
        return_value=["2103.12345"],
    ), patch("arxiv.Client", return_value=mock_client):
        result = await handle_list_papers({})
    content = json.loads(result[0].text)
    assert content["total_papers"] == 1
    assert content["papers"][0]["title"] == mock_paper.title
    assert content["papers"][0]["pdf_url"] == mock_paper.pdf_url
    mock_client.results.assert_called_once()
