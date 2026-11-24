"""Google authentication module for Gmail and Google Calendar MCP server.

Reuses existing token.json and client_secret*.json from GOOGLE_PRIVATE_DIR.
Never copies secrets into the project, never prints secrets, and never opens
a browser from the server.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build

DEFAULT_PRIVATE_DIR = r"C:\my-private"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]

_gmail_service: Resource | None = None
_calendar_service: Resource | None = None


def get_private_directory() -> Path:
    """Return the private directory path from the environment variable."""
    dir_path = Path(os.environ.get("GOOGLE_PRIVATE_DIR", DEFAULT_PRIVATE_DIR))
    if not dir_path.is_dir():
        raise FileNotFoundError(
            f"Private directory not found at: {dir_path}. "
            "Please check the GOOGLE_PRIVATE_DIR environment variable."
        )
    return dir_path


def find_client_secret_file(private_dir: Path) -> Path:
    """Find a client_secret*.json file in the private directory."""
    matches = glob.glob(str(private_dir / "client_secret*.json"))
    if not matches:
        raise FileNotFoundError(
            f"No client_secret*.json file found in {private_dir}."
        )
    return Path(matches[0])


def get_credentials() -> Credentials:
    """Load valid credentials from token.json without opening a browser."""
    private_dir = get_private_directory()
    token_file = private_dir / "token.json"

    if not token_file.is_file():
        raise FileNotFoundError(
            f"token.json not found in {private_dir}. "
            "Server requires an existing pre-authorized token file."
        )

    try:
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load credentials from {token_file}: {exc}. "
            "The token file must contain valid OAuth authorization (refresh_token). "
            "Browser authentication cannot be launched from the server."
        ) from exc

    if not creds:
        raise ValueError("Could not parse credentials from token.json.")

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            client_secret_file = find_client_secret_file(private_dir)
            creds.refresh(Request())
            # Save updated refreshed token back to the private directory
            with open(token_file, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError(
                "Credentials in token.json are expired/invalid and cannot be refreshed. "
                "Browser authentication cannot be launched from the server."
            )

    return creds


def get_gmail_service() -> Resource:
    """Return an authorized Gmail API service instance."""
    global _gmail_service
    if _gmail_service is None:
        creds = get_credentials()
        _gmail_service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    return _gmail_service


def get_calendar_service() -> Resource:
    """Return an authorized Google Calendar API service instance."""
    global _calendar_service
    if _calendar_service is None:
        creds = get_credentials()
        _calendar_service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return _calendar_service
