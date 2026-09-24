
"""
Entry point for the Spotify Memory MCP server.

CALL FLOW
=========

  MCP client / host
        |
        | MCP protocol (stdio or streamable-http)
        v
  spotify_mcp/server.py
        |
        v
  spotify_mcp/tools/*.py
  spotify_mcp/resources/*.py
        |
        v
  spotify_mcp/adapters/graph_adapter.py
        |
        v
  graph/services/*.py
        |
        v
  graph/repositories/*.py
        |
        v
  graph/neo4j_client.py --> Neo4j database

Run directly:
    python -m spotify_mcp
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

from .adapters.graph_adapter import get_graph_adapter
from .config import mcp_config
from .resources import user_resources
from .tools import (
    engagement_tools,
    memory_tools,
    playback_tools,
    reasoning_tools,
    recommendation_tools,
    track_tools,
    user_tools,
)


class StaticTokenVerifier(TokenVerifier):
    """
    Simple bearer-token verifier.

    The expected token is stored in the MCP_AUTH_TOKEN
    environment variable on Render.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        expected_token = os.getenv("MCP_AUTH_TOKEN")

        if not expected_token:
            return None

        if token != expected_token:
            return None

        return AccessToken(
            token=token,
            client_id="spotify-mcp-client",
            scopes=["mcp"],
            resource="https://spotify-memory-mcp.onrender.com/mcp",
        )


mcp = FastMCP(
    mcp_config.server_name,
    host=mcp_config.host,
    port=mcp_config.port,
    streamable_http_path=mcp_config.streamable_http_path,
    sse_path=mcp_config.sse_path,
    message_path=mcp_config.message_path,
    stateless_http=mcp_config.stateless_http,

    # Bearer-token authentication
    token_verifier=StaticTokenVerifier(),

    # Authentication configuration
    auth=AuthSettings(
        issuer_url="https://spotify-memory-mcp.onrender.com",
        resource_server_url="https://spotify-memory-mcp.onrender.com/mcp",
        required_scopes=["mcp"],
        validate_token_resource=True,
    ),
)

adapter = get_graph_adapter()


# Register every tool/resource module against
# the shared MCP server and graph adapter.
playback_tools.register(mcp, adapter)
engagement_tools.register(mcp, adapter)
user_tools.register(mcp, adapter)
track_tools.register(mcp, adapter)
memory_tools.register(mcp, adapter)
recommendation_tools.register(mcp, adapter)
reasoning_tools.register(mcp, adapter)
user_resources.register(mcp, adapter)


def main() -> None:
    """
    Run the MCP server.

    For Render:
        MCP_TRANSPORT=streamable-http

    The MCP endpoint is:
        /mcp
    """
    mcp.run(transport=mcp_config.transport)


if __name__ == "__main__":
    print("Starting FastMCP server...")
    main()

