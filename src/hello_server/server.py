"""
Feishu Access Token Manager for MCP

This server provides a tool to manage and automatically refresh Feishu app access tokens.
"""

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
import time
import requests
import os
from dotenv import load_dotenv

from smithery.decorators import smithery

# 加载环境变量
load_dotenv()

# Configuration schema for Feishu credentials
class ConfigSchema(BaseModel):
    app_id: str = Field(default=os.getenv("FEISHU_APP_ID", ""), description="The App ID of your Feishu application.")
    app_secret: str = Field(default=os.getenv("FEISHU_APP_SECRET", ""), description="The App Secret of your Feishu application.")


# Feishu API endpoints
FEISHU_APP_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"


class FeishuTokenManager:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_access_token = None
        self.expires_at = 0

    def refresh_app_token(self):
        """
        Gets the app access token using app_id and app_secret.
        """
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(FEISHU_APP_TOKEN_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                token_data = data.get("app_access_token")
                self.app_access_token = token_data
                # Set expiration time with a 5-minute buffer
                self.expires_at = time.time() + data.get("expire", 0) - 300
                return True, None
            else:
                return False, data.get("msg", "Unknown error")
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def get_token_info(self):
        """
        Returns the current app access token information. If the token is expired or about to expire,
        it refreshes it first.
        """
        if time.time() >= self.expires_at:
            success, error_msg = self.refresh_app_token()
            if not success:
                return None, error_msg

        return {
            "app_access_token": self.app_access_token,
            "expires_at": self.expires_at
        }, None


# In-memory cache for token managers (one per app_id)
token_manager_cache = {}


def get_token_manager(app_id: str, app_secret: str) -> FeishuTokenManager:
    """
    Factory function to get or create a FeishuTokenManager instance.
    This ensures that for a given app_id, we reuse the same token manager.
    """
    if app_id not in token_manager_cache:
        token_manager_cache[app_id] = FeishuTokenManager(app_id, app_secret)
    
    # Always update with the latest app_secret if provided
    manager = token_manager_cache[app_id]
    manager.app_secret = app_secret
        
    return manager


@smithery.server(config_schema=ConfigSchema)
def create_server():
    """Create and configure the Feishu Token MCP server."""
    
    # Create your FastMCP server as usual
    server = FastMCP("Feishu Token Manager")
    server.description = "A server to manage and refresh Feishu app access tokens."
    server.version = "1.0.0"

    # Add a tool to get Feishu token
    @server.tool()
    def get_feishu_token(ctx: Context) -> dict:
        """
        Provides a valid Feishu app access token. 
        If the existing token is expired or invalid, it will be refreshed automatically.
        The necessary app_id and app_secret are retrieved from the session configuration.
        Returns a dictionary containing the app_access_token and expiration timestamp.
        """
        session_config = ctx.session_config
        
        # Get the token manager instance for the current session
        manager = get_token_manager(
            app_id=session_config.app_id,
            app_secret=session_config.app_secret
        )
        
        token_info, error = manager.get_token_info()
        
        if error:
            raise Exception(f"Failed to refresh token: {error}")
            
        if not token_info:
            raise Exception("Failed to retrieve token information.")

        return token_info

    return server