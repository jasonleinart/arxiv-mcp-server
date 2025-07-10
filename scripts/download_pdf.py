#!/usr/bin/env python3
"""
ArXiv PDF Downloader for Docker MCP Toolkit

This script solves the volume mounting limitation in Docker MCP Toolkit by:
1. Taking the PDF URL returned from arxiv_mcp_server downloads
2. Downloading the PDF to your local filesystem
3. Optionally saving the markdown content as well

Works around the issue where Docker MCP Toolkit doesn't implement volume mounting,
so files downloaded inside containers aren't accessible on the host.
"""

import requests
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Try to import local config, fall back to defaults
try:
    from config import get_papers_directory, get_config
except ImportError:
    def get_papers_directory():
        return os.getenv('ARXIV_PAPERS_PATH', str(Path.home() / "Downloads" / "Papers"))
    def get_config(key, default=None):
        defaults = {'download_timeout': 30, 'chunk_size': 8192}
        return defaults.get(key, default)

def download_arxiv_paper(pdf_url, content=None, paper_id=None, output_dir=None):
    """
    Download PDF from ArXiv URL and optionally save markdown content
    
    Args:
        pdf_url (str): Direct ArXiv PDF URL 
        content (str, optional): Markdown content to save
        paper_id (str, optional): Paper ID for filename
        output_dir (str, optional): Custom output directory
    """
    
    # Use custom directory or get from configuration
    if output_dir:
        papers_dir = Path(output_dir)
    else:
        papers_dir = Path(get_papers_directory())
    
    papers_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract paper ID from URL if not provided
    if not paper_id:
        # Extract from URL like https://arxiv.org/pdf/2507.06000v1.pdf
        parsed_url = urlparse(pdf_url)
        filename = Path(parsed_url.path).name
        paper_id = filename.replace('.pdf', '')
    
    print(f"📄 Downloading paper: {paper_id}")
    print(f"📁 Output directory: {papers_dir}")
    print(f"🔗 PDF URL: {pdf_url}")
    
    # Download PDF
    try:
        print("⬇️  Downloading PDF...")
        timeout = get_config('download_timeout', 30)
        chunk_size = get_config('chunk_size', 8192)
        
        response = requests.get(pdf_url, stream=True, timeout=timeout)
        response.raise_for_status()
        
        pdf_path = papers_dir / f"{paper_id}.pdf"
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        
        pdf_size = pdf_path.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"✅ PDF saved: {pdf_path} ({pdf_size:.1f} MB)")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download PDF: {e}")
        return False
    
    # Save markdown content if provided
    if content:
        try:
            md_path = papers_dir / f"{paper_id}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            md_size = md_path.stat().st_size / 1024  # Size in KB
            print(f"✅ Markdown saved: {md_path} ({md_size:.1f} KB)")
            
        except Exception as e:
            print(f"⚠️  Failed to save markdown: {e}")
    
    print(f"🎉 Paper {paper_id} successfully downloaded!")
    return True

def parse_mcp_response(mcp_response_text):
    """
    Parse MCP download response to extract PDF URL and content
    
    Args:
        mcp_response_text (str): JSON response from MCP download
        
    Returns:
        tuple: (pdf_url, content, paper_id)
    """
    try:
        data = json.loads(mcp_response_text)
        pdf_url = data.get('pdf_uri')
        content = data.get('content')
        
        # Try to extract paper ID from response or URL
        paper_id = None
        if 'paper_id' in data:
            paper_id = data['paper_id']
        elif pdf_url:
            # Extract from URL
            parsed_url = urlparse(pdf_url)
            filename = Path(parsed_url.path).name
            paper_id = filename.replace('.pdf', '')
            
        return pdf_url, content, paper_id
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse MCP response: {e}")
        return None, None, None

def main():
    """Main function - can be called with command line arguments"""
    
    if len(sys.argv) < 2:
        print("ArXiv PDF Downloader for Docker MCP Toolkit")
        print("=" * 50)
        print("Solves the volume mounting limitation where downloaded files")
        print("in Docker containers aren't accessible on the host.")
        print()
        print("Usage:")
        print("  python download_pdf.py <pdf_url> [paper_id] [--output-dir <path>]")
        print("  python download_pdf.py --mcp-response '<json_response>' [--output-dir <path>]")
        print()
        print("Examples:")
        print("  python download_pdf.py https://arxiv.org/pdf/2507.06000v1.pdf")
        print("  python download_pdf.py https://arxiv.org/pdf/2507.06000v1.pdf --output-dir ~/MyPapers")
        print('  python download_pdf.py --mcp-response \'{"pdf_uri": "https://arxiv.org/pdf/2507.06000v1.pdf"}\'')
        print()
        print("Configuration:")
        print("  ARXIV_PAPERS_PATH - Environment variable to set default download directory")
        print("  config.py         - Local configuration file (optional)")
        print()
        print("Current default path:", get_papers_directory())
        return
    
    # Parse command line arguments
    output_dir = None
    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
            # Remove --output-dir and its value from argv for simpler parsing
            sys.argv.pop(idx)  # Remove --output-dir
            sys.argv.pop(idx)  # Remove the path value
    
    if sys.argv[1] == '--mcp-response':
        # Parse full MCP response
        if len(sys.argv) < 3:
            print("❌ MCP response JSON required")
            return
            
        mcp_response = sys.argv[2]
        pdf_url, content, paper_id = parse_mcp_response(mcp_response)
        
        if not pdf_url:
            print("❌ No PDF URL found in MCP response")
            return
            
        download_arxiv_paper(pdf_url, content, paper_id, output_dir)
        
    else:
        # Direct PDF URL
        pdf_url = sys.argv[1]
        paper_id = sys.argv[2] if len(sys.argv) > 2 else None
        
        download_arxiv_paper(pdf_url, paper_id=paper_id, output_dir=output_dir)

if __name__ == "__main__":
    main() 