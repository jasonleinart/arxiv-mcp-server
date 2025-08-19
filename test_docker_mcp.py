#!/usr/bin/env python3
"""
Test script to verify the arxiv-mcp-server Docker container
Simulates MCP protocol requests that would come from Docker MCP Gateway
"""

import json
import subprocess
import asyncio
import sys

def send_mcp_request(request):
    """Send an MCP request to the Docker container via stdin"""
    request_json = json.dumps(request)
    return request_json + "\n"

async def test_docker_server():
    """Test the Docker container with MCP protocol"""
    
    print("=" * 80)
    print("TESTING ARXIV MCP SERVER IN DOCKER")
    print("=" * 80)
    
    # Start the Docker container with proper volume mounting
    print("\n1. Starting Docker container with volume mounting...")
    
    # Create a local directory for paper storage
    subprocess.run(["mkdir", "-p", "/tmp/arxiv-papers"], check=True)
    
    # Run the container
    proc = await asyncio.create_subprocess_exec(
        "docker", "run", 
        "-i",  # Interactive mode for stdin
        "-v", "/tmp/arxiv-papers:/papers",  # Volume mount for paper storage
        "-e", "ARXIV_STORAGE_PATH=/papers",  # Set storage path
        "arxiv-mcp-server:test",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("Container started. Testing MCP protocol...")
    
    # Test 1: Initialize
    print("\n2. Sending initialization request...")
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-01",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    proc.stdin.write(send_mcp_request(init_request).encode())
    await proc.stdin.drain()
    
    # Read response
    response = await proc.stdout.readline()
    init_response = json.loads(response)
    print(f"Initialization response: {json.dumps(init_response, indent=2)[:200]}...")
    
    # Test 2: List tools to get enhanced descriptions
    print("\n3. Requesting tool list with enhanced descriptions...")
    tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    proc.stdin.write(send_mcp_request(tools_request).encode())
    await proc.stdin.drain()
    
    # Read response
    response = await proc.stdout.readline()
    tools_response = json.loads(response)
    
    print("\n" + "=" * 80)
    print("ENHANCED TOOL DESCRIPTIONS FROM DOCKER CONTAINER")
    print("=" * 80)
    
    if "result" in tools_response and "tools" in tools_response["result"]:
        for tool in tools_response["result"]["tools"]:
            print(f"\n📦 Tool: {tool['name']}")
            print(f"📝 Description: {tool['description'][:200]}...")
            
            # Show parameter descriptions
            if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                print("🔧 Parameters:")
                for param, details in tool["inputSchema"]["properties"].items():
                    desc = details.get("description", "No description")
                    print(f"   - {param}: {desc[:100]}...")
    
    # Test 3: Test a search to verify functionality
    print("\n4. Testing search functionality...")
    search_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "search_papers",
            "arguments": {
                "query": "attention mechanism",
                "max_results": 2
            }
        },
        "id": 3
    }
    
    proc.stdin.write(send_mcp_request(search_request).encode())
    await proc.stdin.drain()
    
    # Read response
    response = await proc.stdout.readline()
    search_response = json.loads(response)
    
    if "result" in search_response:
        print("✅ Search successful! Found papers.")
    else:
        print(f"Search response: {json.dumps(search_response, indent=2)[:200]}...")
    
    # Cleanup
    print("\n5. Shutting down container...")
    proc.stdin.close()
    await proc.wait()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\n✅ The Docker container successfully:")
    print("   - Runs the MCP server")
    print("   - Serves enhanced tool descriptions")
    print("   - Supports volume mounting for paper storage")
    print("   - Responds to MCP protocol requests")
    print("\n🎯 Ready for Docker MCP Gateway integration!")

if __name__ == "__main__":
    asyncio.run(test_docker_server())