"""Test script that starts the gmail-calendar MCP server over stdio.

Lists available tools and calls list_events with days_ahead=1.
File kept strictly under 150 lines.
"""

from __future__ import annotations

import os
import sys

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    # Set the required environment variable
    os.environ["GOOGLE_PRIVATE_DIR"] = r"C:\my-private"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env={**os.environ, "GOOGLE_PRIVATE_DIR": r"C:\my-private"},
    )

    print("Connecting to gmail-calendar MCP server over stdio...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            init_res = await session.initialize()
            server_name = init_res.serverInfo.name
            server_version = init_res.serverInfo.version
            print(f"Connected to: {server_name} (v{server_version})\n")

            # 1. Ask for list of tools
            print("=== Registered Tools ===")
            tools_res = await session.list_tools()
            for tool in tools_res.tools:
                print(f"- {tool.name}: {tool.description}")
            print(f"\nTotal tools found: {len(tools_res.tools)}\n")

            # 2. Call list_events with days_ahead=1
            print("=== Calling list_events(days_ahead=1) ===")
            result = await session.call_tool(
                "list_events", arguments={"days_ahead": 1}
            )

            if result.isError:
                print("Tool call completed with error status:")
            else:
                print("Tool call succeeded:")

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(content)


if __name__ == "__main__":
    anyio.run(main)
