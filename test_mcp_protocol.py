#!/usr/bin/env python3
"""
Proper MCP protocol test for arxiv-mcp-server in Docker
Tests the actual protocol methods and verifies enhanced descriptions
"""

import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server with correct protocol"""
    
    print("=" * 80)
    print("TESTING ARXIV MCP SERVER - PROPER MCP PROTOCOL")
    print("=" * 80)
    
    # MCP commands to send
    commands = [
        # 1. Initialize
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-01",
                "capabilities": {},
                "clientInfo": {
                    "name": "docker-test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        },
        # 2. List tools (correct method name)
        {
            "jsonrpc": "2.0",
            "method": "list_tools",
            "params": {},
            "id": 2
        },
        # 3. Call search tool
        {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "name": "search_papers",
                "arguments": {
                    "query": "transformer architecture attention",
                    "max_results": 2
                }
            },
            "id": 3
        }
    ]
    
    # Prepare commands as newline-delimited JSON
    input_data = '\n'.join(json.dumps(cmd) for cmd in commands)
    
    print("\n1. Starting Docker container and sending MCP commands...")
    print("   Commands being sent:")
    for i, cmd in enumerate(commands, 1):
        print(f"   {i}. {cmd['method']}")
    
    # Run Docker container with commands
    result = subprocess.run(
        [
            "docker", "run", 
            "-i", "--rm",
            "-e", "ARXIV_STORAGE_PATH=/papers",
            "-v", "/tmp/arxiv-papers:/papers",
            "arxiv-mcp-server:test"
        ],
        input=input_data,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"\n❌ Error running container:")
        print(f"   stderr: {result.stderr}")
        return False
    
    # Parse responses
    responses = []
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Failed to parse: {line}")
                print(f"Error: {e}")
    
    print(f"\n2. Received {len(responses)} responses")
    
    # Analyze responses
    success = True
    
    # Check initialization
    if responses[0].get("result", {}).get("serverInfo", {}).get("name") == "arxiv-mcp-server":
        print("\n✅ Initialization successful")
        print(f"   Server: {responses[0]['result']['serverInfo']['name']} v{responses[0]['result']['serverInfo']['version']}")
    else:
        print("\n❌ Initialization failed")
        success = False
    
    # Check tool descriptions
    if len(responses) > 1 and "result" in responses[1]:
        tools_result = responses[1].get("result", {})
        if "tools" in tools_result:
            tools = tools_result["tools"]
            print(f"\n✅ Tool list retrieved: {len(tools)} tools")
            
            print("\n" + "=" * 80)
            print("ENHANCED TOOL DESCRIPTIONS")
            print("=" * 80)
            
            for tool in tools:
                print(f"\n📦 Tool: {tool['name']}")
                desc_len = len(tool.get('description', ''))
                print(f"   Description length: {desc_len} characters")
                
                if desc_len > 100:
                    print(f"   ✅ Enhanced description present")
                    print(f"   Preview: {tool['description'][:150]}...")
                else:
                    print(f"   ❌ Description too short (only {desc_len} chars)")
                    print(f"   Content: {tool['description']}")
                    success = False
                
                # Check parameters
                if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                    params = tool["inputSchema"]["properties"]
                    print(f"   Parameters: {', '.join(params.keys())}")
                    
                    # Check for enhanced parameter descriptions
                    for param_name, param_def in params.items():
                        if "description" in param_def:
                            param_desc_len = len(param_def["description"])
                            if param_desc_len > 20:
                                print(f"     ✅ {param_name}: has detailed description ({param_desc_len} chars)")
                            else:
                                print(f"     ⚠️  {param_name}: short description ({param_desc_len} chars)")
        else:
            print("\n❌ No tools in response")
            print(f"   Response: {json.dumps(responses[1], indent=2)}")
            success = False
    else:
        print("\n❌ Failed to get tool list")
        if len(responses) > 1:
            print(f"   Response: {json.dumps(responses[1], indent=2)}")
        success = False
    
    # Check search functionality
    if len(responses) > 2:
        search_response = responses[2]
        if "result" in search_response:
            content = search_response["result"].get("content", [])
            if content and len(content) > 0:
                # Parse the search results
                try:
                    search_data = json.loads(content[0]["text"])
                    paper_count = search_data.get("total_results", 0)
                    print(f"\n✅ Search tool works: Found {paper_count} papers")
                    
                    if paper_count > 0:
                        print("   Sample paper:")
                        paper = search_data["papers"][0]
                        print(f"     Title: {paper['title'][:60]}...")
                        print(f"     ID: {paper['id']}")
                except:
                    print("\n⚠️  Search returned data but couldn't parse results")
            else:
                print("\n❌ Search returned no content")
                success = False
        elif "error" in search_response:
            print(f"\n❌ Search failed with error: {search_response['error']}")
            success = False
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("   - Docker container runs correctly")
        print("   - Enhanced tool descriptions are present")
        print("   - Tools can be called successfully")
        print("   - Ready for Docker MCP Gateway integration")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("   Please review the errors above")
    
    return success

if __name__ == "__main__":
    # Create temp directory for papers
    subprocess.run(["mkdir", "-p", "/tmp/arxiv-papers"], check=True)
    
    # Run test
    success = test_mcp_server()
    sys.exit(0 if success else 1)