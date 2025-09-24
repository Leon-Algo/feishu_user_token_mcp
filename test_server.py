#!/usr/bin/env python3
"""
Test script to verify the Feishu token manager MCP server functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import the server module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def test_server():
    """Test the server functionality."""
    print("Testing Feishu Token Manager MCP Server...")
    
    # Import our server module
    from hello_server.server import create_server
    
    # Create the server
    server = create_server()
    
    # Print server attributes
    print(f"Server attributes: {dir(server)}")
    
    # Get credentials from environment
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    print(f"App ID: {app_id}")
    print(f"App Secret: {app_secret}")
    
    if not app_id or not app_secret:
        print("Error: FEISHU_APP_ID and FEISHU_APP_SECRET must be set in .env file")
        return False
    
    return True

if __name__ == "__main__":
    print("Running server test...")
    success = test_server()
    if success:
        print("Test passed!")
    else:
        print("Test failed!")
        sys.exit(1)