"""Gmail and Google Calendar MCP server using FastMCP and stdio transport.

Exposes exactly 6 tools for search, read, draft creation, event listing,
slot finding, and event creation. Never sends or deletes anything.
File kept under 150 lines.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from calendar_service import create_event_impl, find_free_slots_impl, list_events_impl
from gmail_service import create_draft_impl, read_email_impl, search_emails_impl

# Initialize FastMCP server named "gmail-calendar"
mcp = FastMCP("gmail-calendar")


@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> str:
    """Search Gmail messages matching a search query."""
    results = search_emails_impl(query=query, max_results=max_results)
    return json.dumps(results, indent=2, ensure_ascii=False)


@mcp.tool()
def read_email(message_id: str) -> str:
    """Read full details and content of an email by its message ID."""
    result = read_email_impl(message_id=message_id)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def create_draft(to: str, subject: str, body: str) -> str:
    """Create an email draft in Gmail without sending it."""
    result = create_draft_impl(to=to, subject=subject, body=body)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def list_events(days_ahead: int = 7) -> str:
    """List upcoming Google Calendar events for a given number of days."""
    results = list_events_impl(days_ahead=days_ahead)
    return json.dumps(results, indent=2, ensure_ascii=False)


@mcp.tool()
def find_free_slots(date: str, duration_minutes: int = 30) -> str:
    """Find available free time slots on a specific date in Asia/Jerusalem."""
    results = find_free_slots_impl(date=date, duration_minutes=duration_minutes)
    return json.dumps(results, indent=2, ensure_ascii=False)


@mcp.tool()
def create_event(
    title: str, start: str, end: str, description: str = ""
) -> str:
    """Create a new calendar event in Google Calendar in Asia/Jerusalem."""
    result = create_event_impl(
        title=title, start=start, end=end, description=description
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


def main() -> None:
    """Entry point running the MCP server over stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
