# ArXiv MCP Server Utility Scripts

This directory contains utility scripts that solve common issues when using the ArXiv MCP server with Docker.

## 🐳 Docker Volume Mounting Issue

**Problem:** The Docker MCP Toolkit doesn't implement volume mounting yet, so files downloaded inside containers aren't accessible on your host machine.

**Solution:** These scripts work around this limitation by downloading PDFs directly to your local filesystem using the URLs returned by the MCP server.

## 📁 Scripts

### `download_pdf.py`

Downloads ArXiv PDFs to your local filesystem using URLs returned from MCP download responses.

**Features:**
- Downloads PDFs from ArXiv URLs
- Saves markdown content from MCP responses
- Configurable output directories
- Handles both direct URLs and full MCP response JSON

**Basic Usage:**
```bash
# Download from direct ArXiv URL
python download_pdf.py https://arxiv.org/pdf/2507.06000v1.pdf

# Download to custom directory
python download_pdf.py https://arxiv.org/pdf/2507.06000v1.pdf --output-dir ~/MyPapers

# Parse full MCP response (with content)
python download_pdf.py --mcp-response '{"pdf_uri": "https://arxiv.org/pdf/2507.06000v1.pdf", "content": "# Paper content..."}'
```

### `config.py`

Configuration file for customizing download behavior.

**Configuration Options:**
- `papers_directory`: Default download location
- `auto_download_pdf`: Whether to auto-download PDFs
- `save_markdown`: Whether to save markdown content
- `download_timeout`: Request timeout in seconds
- `chunk_size`: Download chunk size in bytes

## ⚙️ Configuration

### Priority Order:
1. **Command line** `--output-dir` (highest priority)
2. **Environment variable** `ARXIV_PAPERS_PATH`
3. **Config file** `config.py` settings
4. **Default** `~/Downloads/Papers` (fallback)

### Environment Variables:
```bash
# Set custom papers directory
export ARXIV_PAPERS_PATH="/path/to/your/papers"
```

### Config File:
Edit `config.py` to change defaults:
```python
CONFIG = {
    'papers_directory': '/your/custom/path',
    'auto_download_pdf': True,
    'save_markdown': True,
    'download_timeout': 30,
    'chunk_size': 8192,
}
```

## 🔧 Installation

1. **Install dependencies:**
   ```bash
   pip install requests
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x download_pdf.py config.py
   ```

## 📖 Usage Examples

### With Docker MCP Toolkit

1. **Download paper via MCP:**
   ```bash
   # This returns content + PDF URL but files aren't accessible
   mcp download-paper 2507.06000v1
   ```

2. **Extract PDF URL and download locally:**
   ```bash
   # Use the pdf_uri from the MCP response
   python scripts/download_pdf.py https://arxiv.org/pdf/2507.06000v1.pdf
   ```

3. **Or parse the full MCP response:**
   ```bash
   # Copy the entire JSON response from MCP
   python scripts/download_pdf.py --mcp-response '{"status":"success","pdf_uri":"https://arxiv.org/pdf/2507.06000v1.pdf","content":"..."}'
   ```

### Workflow Integration

```bash
# Set your preferred papers directory
export ARXIV_PAPERS_PATH="$HOME/Research/Papers"

# Download paper
python scripts/download_pdf.py https://arxiv.org/pdf/2507.06000v1.pdf

# Results in:
# ~/Research/Papers/2507.06000v1.pdf  (4.2 MB)
# ~/Research/Papers/2507.06000v1.md   (15.6 KB) [if content included]
```

## 🐛 Troubleshooting

### Common Issues:

**Files not appearing in directory:**
- Check the output directory path
- Verify write permissions
- Ensure directory exists or can be created

**Download failures:**
- Check internet connection
- Verify ArXiv URL is correct and accessible
- Check timeout settings in config

**Import errors:**
- Ensure `requests` is installed: `pip install requests`
- Run from the scripts directory or adjust import paths

### Debug Information:
```bash
# Show current configuration
python config.py

# Test with verbose output
python download_pdf.py --help
```

## 🔄 Future Improvements

When Docker MCP Toolkit adds volume mounting support, these scripts will still be useful for:
- Custom download locations
- Batch operations
- Integration with other tools
- Offline PDF management

## 🤝 Contributing

These scripts solve a fundamental limitation in the Docker MCP ecosystem. Improvements welcome:
- Better error handling
- Batch download support
- Integration with other MCP servers
- GUI versions 