"""Gmail operations module for search, read, and draft creation.

Never sends or deletes any emails. Keeps each file under 150 lines.
"""

from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Any

from auth import get_gmail_service


def _extract_body(payload: dict[str, Any]) -> str:
    """Extract decoded plain-text or HTML body from a message payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain" and "data" in part.get("body", {}):
                data = part["body"]["data"]
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            if "parts" in part:
                nested = _extract_body(part)
                if nested:
                    return nested
    if "body" in payload and "data" in payload["body"]:
        data = payload["body"]["data"]
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def search_emails_impl(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search emails matching a query string and return summaries."""
    service = get_gmail_service()
    max_results = max(1, min(max_results, 50))
    res = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = res.get("messages", [])

    results = []
    for m in messages:
        msg = service.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        results.append({
            "id": msg.get("id"),
            "threadId": msg.get("threadId"),
            "subject": headers.get("Subject", "(No Subject)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return results


def read_email_impl(message_id: str) -> dict[str, Any]:
    """Retrieve full email content and metadata by message ID."""
    service = get_gmail_service()
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = msg.get("payload", {})
    headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

    body = _extract_body(payload)
    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "subject": headers.get("Subject", "(No Subject)"),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "date": headers.get("Date", ""),
        "snippet": msg.get("snippet", ""),
        "body": body or msg.get("snippet", ""),
    }


def create_draft_impl(to: str, subject: str, body: str) -> dict[str, Any]:
    """Create a draft email without sending it."""
    service = get_gmail_service()
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft_body = {"message": {"raw": encoded_message}}
    draft = service.users().drafts().create(userId="me", body=draft_body).execute()

    return {
        "status": "draft_created",
        "draft_id": draft.get("id"),
        "message_id": draft.get("message", {}).get("id"),
        "to": to,
        "subject": subject,
    }
