"""
Feishu Token MCP Server

A Model Context Protocol server for managing and automatically refreshing 
Feishu app and user access tokens.
"""

__version__ = "1.0.0"

from .server import create_server

__all__ = ["create_server"]
