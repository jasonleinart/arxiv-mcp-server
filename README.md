[![Twitter Follow](https://img.shields.io/twitter/follow/JoeBlazick?style=social)](https://twitter.com/JoeBlazick)
[![smithery badge](https://smithery.ai/badge/arxiv-mcp-server)](https://smithery.ai/server/arxiv-mcp-server)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/blazickjp/arxiv-mcp-server/actions/workflows/tests.yml/badge.svg)](https://github.com/blazickjp/arxiv-mcp-server/actions/workflows/tests.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI Downloads](https://img.shields.io/pypi/dm/arxiv-mcp-server.svg)](https://pypi.org/project/arxiv-mcp-server/)
[![PyPI Version](https://img.shields.io/pypi/v/arxiv-mcp-server.svg)](https://pypi.org/project/arxiv-mcp-server/)

# ArXiv MCP Server
## Enhanced Fork with Docker Registry Contribution & Volume Mounting Solutions

> 🔍 Enable AI assistants to search and access arXiv papers through a simple MCP interface.
> 
> 🐳 **NEW**: Includes Docker MCP Toolkit compatibility solutions and utility scripts

**This enhanced fork includes**:
- ✅ [Docker MCP Registry contribution](https://github.com/docker/mcp-registry/pull/66) - **MERGED** 🎉
- ✅ Full Docker Desktop MCP Toolkit integration
- ✅ Production-ready Docker deployment with volume mounting
- ✅ Comprehensive documentation and guides
- ✅ All original ArXiv MCP server functionality

---

## 🎯 Docker MCP Registry Contribution

**Status**: ✅ **MERGED** - [Pull Request #66](https://github.com/docker/mcp-registry/pull/66) 🎉

This fork was specifically enhanced to contribute the ArXiv MCP Server to Docker's official registry, making academic research tools accessible through Docker Desktop MCP Toolkit. The contribution includes:

- **Production Docker deployment** ready for widespread adoption
- **Volume mounting workarounds** solving fundamental Docker MCP Toolkit limitations  
- **Universal utility scripts** benefiting the entire MCP community
- **Professional documentation** and comprehensive user guides

**Impact**: ArXiv MCP Server is now available to researchers, academics, and AI developers worldwide through Docker's official registry!

---

The ArXiv MCP Server provides a bridge between AI assistants and arXiv's research repository through the Model Context Protocol (MCP). It allows AI models to search for papers and access their content in a programmatic way.

<div align="center">
  
🤝 **[Contribute](https://github.com/blazickjp/arxiv-mcp-server/blob/main/CONTRIBUTING.md)** • 
📝 **[Report Bug](https://github.com/blazickjp/arxiv-mcp-server/issues)** •
🐳 **[Docker Registry](https://github.com/docker/mcp-registry/pull/66)** ✅

<a href="https://www.pulsemcp.com/servers/blazickjp-arxiv-mcp-server"><img src="https://www.pulsemcp.com/badge/top-pick/blazickjp-arxiv-mcp-server" width="400" alt="Pulse MCP Badge"></a>
</div>

## ✨ Core Features

- 🔎 **Paper Search**: Query arXiv papers with filters for date ranges and categories
- 📄 **Paper Access**: Download and read paper content
- 📋 **Paper Listing**: View all downloaded papers
- 🗃️ **Local Storage**: Papers are saved locally for faster access
- 📝 **Prompts**: A Set of Research Prompts
- 🐳 **Docker Ready**: Official Docker MCP Registry integration with volume mounting

## 🚀 Quick Start

### Installing via Smithery

To install ArXiv Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/arxiv-mcp-server):

```bash
npx -y @smithery/cli install arxiv-mcp-server --client claude
```

### Installing Manually
Install using uv:

```bash
uv tool install arxiv-mcp-server
```

For development:

```bash
# Clone and set up development environment
git clone https://github.com/blazickjp/arxiv-mcp-server.git
cd arxiv-mcp-server

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install with test dependencies
uv pip install -e ".[test]"
```

### 🔌 MCP Integration

Add this configuration to your MCP client config file:

```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "uv",
            "args": [
                "tool",
                "run",
                "arxiv-mcp-server"
            ],
            "env": {
                "ARXIV_STORAGE_PATH": "/path/to/paper/storage"
            }
        }
    }
}
```

For Development:

```json
{
    "mcpServers": {
        "arxiv-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "path/to/cloned/arxiv-mcp-server",
                "run",
                "arxiv-mcp-server"
            ],
            "env": {
                "ARXIV_STORAGE_PATH": "/path/to/paper/storage"
            }
        }
    }
}
```

## 🐳 Docker Integration

**Great News!** The ArXiv MCP Server is now officially available in the Docker MCP Registry with full volume mounting support! 🎉

### Using with Docker Desktop MCP Toolkit

1. **Install from Docker Registry**: Available directly through Docker Desktop's MCP Toolkit
2. **Automatic Volume Mounting**: Downloaded papers are automatically accessible on your host machine
3. **No Configuration Required**: Works out of the box with proper volume mounting

### Additional Features

The server includes comprehensive research analysis prompts and full paper content access, making it perfect for academic research workflows.

### 🏆 Technical Achievement: Contributing to Docker MCP Ecosystem

**The Journey**: During the Docker MCP Registry contribution process, we enhanced the ArXiv MCP Server with production-ready Docker deployment capabilities and comprehensive tooling.

**Our Contributions**: 
- **Production Docker Configuration**: Proper volume mounting and environment variable handling
- **Comprehensive Documentation**: Guides helping the entire MCP community
- **Ecosystem Impact**: Solutions work with any LLM supporting MCP protocol

**Community Impact**: The ArXiv MCP Server is now available to thousands of researchers, academics, and developers worldwide through Docker's official registry, enabling seamless academic research workflows.

**Real-World Success**: Successfully tested with papers including:
- FR3E Framework (ByteDance): Entropy-based exploration for LLM reasoning
- Cognitive Networks: DQN optimization for energy harvesting systems

## 💡 Available Tools

The server provides four main tools:

### 1. Paper Search
Search for papers with optional filters:

```python
result = await call_tool("search_papers", {
    "query": "transformer architecture",
    "max_results": 10,
    "date_from": "2023-01-01",
    "categories": ["cs.AI", "cs.LG"]
})
```

### 2. Paper Download
Download a paper by its arXiv ID:

```python
result = await call_tool("download_paper", {
    "paper_id": "2401.12345"
})
```

### 3. List Papers
View all downloaded papers:

```python
result = await call_tool("list_papers", {})
```

### 4. Read Paper
Access the content of a downloaded paper:

```python
result = await call_tool("read_paper", {
    "paper_id": "2401.12345"
})
```

## 📝 Research Prompts

The server offers specialized prompts to help analyze academic papers:

### Paper Analysis Prompt
A comprehensive workflow for analyzing academic papers that only requires a paper ID:

```python
result = await call_prompt("deep-paper-analysis", {
    "paper_id": "2401.12345"
})
```

This prompt includes:
- Detailed instructions for using available tools (list_papers, download_paper, read_paper, search_papers)
- A systematic workflow for paper analysis
- Comprehensive analysis structure covering:
  - Executive summary
  - Research context
  - Methodology analysis
  - Results evaluation
  - Practical and theoretical implications
  - Future research directions
  - Broader impacts

## ⚙️ Configuration

Configure through environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `ARXIV_STORAGE_PATH` | Paper storage location | ~/.arxiv-mcp-server/papers |

## 🧪 Testing

Run the test suite:

```bash
python -m pytest
```

## 📄 License

Released under the MIT License. See the LICENSE file for details.

---

<div align="center">

Made with ❤️ by the Pearl Labs Team

<a href="https://glama.ai/mcp/servers/04dtxi5i5n"><img width="380" height="200" src="https://glama.ai/mcp/servers/04dtxi5i5n/badge" alt="ArXiv Server MCP server" /></a>
</div>
