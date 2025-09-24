"""
Feishu Access Token Manager for MCP

This server provides tools to manage and automatically refresh Feishu app and user access tokens.
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
FEISHU_USER_TOKEN_REFRESH_URL = "https://open.feishu.cn/open-apis/authen/v1/refresh_access_token"


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
                self.app_access_token = data.get("app_access_token")
                # Set expiration time with a 5-minute buffer
                self.expires_at = time.time() + data.get("expire", 0) - 300
                return True, None
            else:
                return False, data.get("msg", "Unknown error")
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def get_app_token(self):
        """
        Returns the current app access token. If the token is expired or about to expire,
        it refreshes it first.
        """
        if not self.app_access_token or time.time() >= self.expires_at:
            success, error_msg = self.refresh_app_token()
            if not success:
                raise Exception(f"Failed to refresh app token: {error_msg}")

        return self.app_access_token

    def refresh_user_token(self, refresh_token: str):
        """
        Refreshes the user access token using the refresh token.
        """
        # First get a valid app token
        app_token = self.get_app_token()
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {app_token}"
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.app_id,
            "client_secret": self.app_secret
        }
        
        try:
            response = requests.post(FEISHU_USER_TOKEN_REFRESH_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                token_data = data.get("data", {})
                return {
                    "access_token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in"),
                    "token_type": token_data.get("token_type"),
                    "scope": token_data.get("scope")
                }, None
            else:
                return None, f"API error: {data.get('msg', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return None, str(e)


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
    server.description = "A server to manage and refresh Feishu app and user access tokens."
    server.version = "1.0.0"

    # Add a tool to get Feishu app token
    @server.tool()
    def get_feishu_app_token(ctx: Context) -> dict:
        """
        Provides a valid Feishu app access token. 
        If the existing token is expired or invalid, it will be refreshed automatically.
        The necessary app_id and app_secret are retrieved from the session configuration.
        Returns the app_access_token and expiration information.
        """
        session_config = ctx.session_config
        
        # Get the token manager instance for the current session
        manager = get_token_manager(
            app_id=session_config.app_id,
            app_secret=session_config.app_secret
        )
        
        try:
            app_token = manager.get_app_token()
            return {
                "app_access_token": app_token,
                "expires_at": manager.expires_at
            }
        except Exception as e:
            raise Exception(f"Failed to get app token: {str(e)}")

    # Add a tool to refresh Feishu user token
    @server.tool()
    def refresh_feishu_user_token(refresh_token: str, ctx: Context) -> dict:
        """
        Refreshes a Feishu user access token using the provided refresh token.
        The app_id and app_secret are retrieved from the session configuration.
        Returns the new access token, refresh token, and expiration information.
        """
        session_config = ctx.session_config
        
        # Get the token manager instance for the current session
        manager = get_token_manager(
            app_id=session_config.app_id,
            app_secret=session_config.app_secret
        )
        
        token_info, error = manager.refresh_user_token(refresh_token)
        
        if error:
            raise Exception(f"Failed to refresh user token: {error}")
            
        if not token_info:
            raise Exception("Failed to retrieve token information.")

        return token_info

    return server