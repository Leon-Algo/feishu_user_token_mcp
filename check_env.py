#!/usr/bin/env python3
"""
Check environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
app_id = os.getenv("FEISHU_APP_ID")
app_secret = os.getenv("FEISHU_APP_SECRET")

print(f"App ID: {app_id}")
print(f"App Secret: {app_secret}")

if app_id and app_secret:
    print("Environment variables loaded successfully!")
else:
    print("Failed to load environment variables!")