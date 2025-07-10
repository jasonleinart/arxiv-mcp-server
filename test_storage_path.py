#!/usr/bin/env python3
"""Test script to check storage path configuration."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, '/app/src')

from arxiv_mcp_server.config import Settings

# Print the command line arguments
print("Command line arguments:", sys.argv)

# Create settings instance and check storage path
settings = Settings()
print("Storage path:", settings.STORAGE_PATH)
print("Storage path exists:", settings.STORAGE_PATH.exists())

# Test if the path is correct
expected_path = Path("/app/papers")
print("Expected path:", expected_path)
print("Paths match:", settings.STORAGE_PATH == expected_path) 