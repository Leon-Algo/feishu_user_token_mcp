#!/usr/bin/env python3
"""
Simple test script to verify the Feishu token manager functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import the server module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Import our token manager
from hello_server.server import FeishuTokenManager

def test_app_token():
    """Test the app token functionality."""
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("Error: FEISHU_APP_ID and FEISHU_APP_SECRET must be set in .env file")
        return False
    
    print("Testing app token retrieval...")
    manager = FeishuTokenManager(app_id, app_secret)
    
    try:
        token = manager.get_app_token()
        print(f"App token retrieved successfully: {token[:20]}...")
        print(f"Token expires at: {manager.expires_at}")
        return True
    except Exception as e:
        print(f"Error retrieving app token: {e}")
        return False

if __name__ == "__main__":
    print("Running simple test...")
    success = test_app_token()
    if success:
        print("Test passed!")
    else:
        print("Test failed!")
        sys.exit(1)