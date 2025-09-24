#!/usr/bin/env python3
"""
Direct test script to verify the FeishuTokenManager functionality.
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

def test_token_manager():
    """Test the FeishuTokenManager directly."""
    print("Testing FeishuTokenManager directly...")
    
    # Get credentials from environment
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    print(f"App ID: {app_id}")
    print(f"App Secret: {app_secret}")
    
    if not app_id or not app_secret:
        print("Error: FEISHU_APP_ID and FEISHU_APP_SECRET must be set in .env file")
        return False
    
    # Create token manager
    manager = FeishuTokenManager(app_id, app_secret)
    
    try:
        # Test getting app token
        print("Getting app token...")
        token = manager.get_app_token()
        print(f"App token: {token}")
        
        # Test token info
        print("Getting token info...")
        # Access private attributes for testing
        print(f"Expires at: {manager.expires_at}")
        print("Test completed successfully!")
        return True
    except Exception as e:
        print(f"Error testing token manager: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running direct test...")
    success = test_token_manager()
    if success:
        print("Test passed!")
    else:
        print("Test failed!")
        sys.exit(1)