"""
MCP server configuration — separate from graph/config.py (which holds
Neo4j connection settings). This only configures the MCP server itself.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class MCPConfig:
    server_name: str = os.getenv("MCP_SERVER_NAME", "spotify-memory")
    server_version: str = os.getenv("MCP_SERVER_VERSION", "0.1.0")
    # Keep stdio for local Claude Desktop subprocesses. Use streamable-http
    # (recommended) or sse when an external host connects by URL.
    transport: str = os.getenv("MCP_TRANSPORT", "stdio")
    host: str = os.getenv("MCP_HOST", "127.0.0.1")
   port: int = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    streamable_http_path: str = os.getenv("MCP_STREAMABLE_HTTP_PATH", "/mcp")
    sse_path: str = os.getenv("MCP_SSE_PATH", "/sse")
    message_path: str = os.getenv("MCP_MESSAGE_PATH", "/messages/")
    stateless_http: bool = os.getenv("MCP_STATELESS_HTTP", "true").lower() in {"1", "true", "yes"}

    def __post_init__(self) -> None:
        if self.transport not in {"stdio", "sse", "streamable-http"}:
            raise ValueError("MCP_TRANSPORT must be stdio, sse, or streamable-http")
        if not 1 <= self.port <= 65535:
            raise ValueError("MCP_PORT must be between 1 and 65535")


mcp_config = MCPConfig()
