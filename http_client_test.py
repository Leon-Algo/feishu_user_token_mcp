#!/usr/bin/env python3
"""
HTTP client test for the MCP server.
"""

import requests
import json

# Server URL
url = "http://127.0.0.1:8081/mcp"

# Initialize request
init_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

# Send initialize request
print("Sending initialize request...")
try:
    response = requests.post(url, json=init_payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")