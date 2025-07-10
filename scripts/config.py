#!/usr/bin/env python3
"""
ArXiv Download Configuration
Simple configuration file for ArXiv paper downloads
"""

import os
from pathlib import Path

# Default configuration
CONFIG = {
    # Download directory for papers (use user's home directory)
    'papers_directory': str(Path.home() / "Downloads" / "Papers"),
    
    # Whether to download PDFs automatically after MCP download
    'auto_download_pdf': True,
    
    # Whether to save markdown content
    'save_markdown': True,
    
    # Request timeout in seconds
    'download_timeout': 30,
    
    # Chunk size for downloading (in bytes)
    'chunk_size': 8192,
}

def get_papers_directory():
    """
    Get the configured papers directory, with priority:
    1. Environment variable ARXIV_PAPERS_PATH
    2. Config file setting
    3. Default ~/Downloads/Papers
    """
    env_path = os.getenv('ARXIV_PAPERS_PATH')
    if env_path:
        return env_path
    
    return CONFIG['papers_directory']

def get_config(key, default=None):
    """Get a configuration value"""
    return CONFIG.get(key, default)

def set_config(key, value):
    """Set a configuration value"""
    CONFIG[key] = value

def show_config():
    """Display current configuration"""
    print("ArXiv Download Configuration")
    print("=" * 35)
    print(f"Papers Directory: {get_papers_directory()}")
    print(f"Auto Download PDF: {CONFIG['auto_download_pdf']}")
    print(f"Save Markdown: {CONFIG['save_markdown']}")
    print(f"Download Timeout: {CONFIG['download_timeout']}s")
    print(f"Chunk Size: {CONFIG['chunk_size']} bytes")
    
    env_path = os.getenv('ARXIV_PAPERS_PATH')
    if env_path:
        print(f"\n📝 Note: Using environment variable ARXIV_PAPERS_PATH")

if __name__ == "__main__":
    show_config() 