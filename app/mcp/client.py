import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_sql_client() -> Client:
    """
    Create an MCP client connected to the SQL MCP server
    through the stdio transport.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp.servers.sql_server",
        ],
        cwd=str(PROJECT_ROOT),
        env={
            "PYTHONPATH": str(PROJECT_ROOT),
        },
    )

    return Client(server_params)


async def test_connection():
    """
    Connect to the SQL MCP server and list available tools.
    """

    async with create_sql_client() as client:

        print("Connected to SQL MCP Server")

        print("\nServer info:")
        print(client.server_info)

        print("\nAvailable tools:")

        tools = await client.list_tools()

        for tool in tools:
            print(f"- {tool.name}")


def create_research_client() -> Client:
    """
    Create an MCP client connected to the Research MCP server
    through the stdio transport.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp.servers.research_server",
        ],
        cwd=str(PROJECT_ROOT),
        env={
            "PYTHONPATH": str(PROJECT_ROOT),
        },
    )

    return Client(server_params)


def create_file_client() -> Client:
    """
    Create an MCP client connected to the File MCP server
    through the stdio transport.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp.servers.file_server",
        ],
        cwd=str(PROJECT_ROOT),
        env={
            "PYTHONPATH": str(PROJECT_ROOT),
        },
    )

    return Client(server_params)


def extract_tool_result(result):
    """
    Extract application-level data from an MCP CallToolResult.

    Prefers structured_content when available and falls back
    to parsing JSON text content.
    """

    import json

    if result.is_error:
        raise RuntimeError(
            "MCP tool execution failed."
        )

    # ---------------------------------------------------------
    # Preferred path: structured content
    # ---------------------------------------------------------

    if result.structured_content:

        if "result" in result.structured_content:
            return result.structured_content["result"]

        return result.structured_content

    # ---------------------------------------------------------
    # Fallback: parse text content
    # ---------------------------------------------------------

    extracted = []

    for item in result.content:

        if getattr(item, "type", None) != "text":
            continue

        text = item.text.strip()

        if not text:
            continue

        # Try to parse JSON text.
        try:
            extracted.append(
                json.loads(text)
            )

        except json.JSONDecodeError:
            extracted.append(text)

    # If there is exactly one result,
    # return the result itself rather than a list.
    if len(extracted) == 1:
        return extracted[0]

    return extracted