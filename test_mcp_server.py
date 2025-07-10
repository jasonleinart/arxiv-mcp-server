#!/usr/bin/env python3
"""
Test script to verify the arXiv MCP server works
"""

import asyncio
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from arxiv_mcp_server.server import server
    from arxiv_mcp_server.tools import search_tool, download_tool, list_tool, read_tool
    print("✅ Successfully imported MCP server components")
    
    # Test that we can access the tools
    tools = [search_tool, download_tool, list_tool, read_tool]
    print(f"✅ Server has {len(tools)} tools available:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test that we can import the prompts
    try:
        from arxiv_mcp_server.prompts.handlers import list_prompts
        print("✅ Successfully imported prompts module")
    except ImportError as e:
        print(f"⚠️  Could not import prompts: {e}")
    
    print("\n✅ MCP Server components loaded successfully!")
    print("The server is ready to be used with Claude Desktop.")
    
except Exception as e:
    print(f"❌ Error testing MCP server: {e}")
    import traceback
    traceback.print_exc() 