"""Standalone one-time OAuth authorization helper.

This script is NOT part of the server runtime. It can be run manually
by the user to authorize access and generate/update token.json in
GOOGLE_PRIVATE_DIR without touching project files or exposing secrets.
File kept under 150 lines.
"""

from __future__ import annotations

import secrets
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

from auth import SCOPES, find_client_secret_file, get_private_directory


def main() -> None:
    """Run interactive local OAuth flow and save token.json to private directory."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    private_dir = get_private_directory()
    client_secret_path = find_client_secret_file(private_dir)
    token_path = private_dir / "token.json"

    print(f"Using client secrets from: {client_secret_path.name}", flush=True)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path), SCOPES
    )

    session_state = secrets.token_urlsafe(16)

    prompt = (
        "\n" + "=" * 60 + "\n"
        "PLEASE OPEN THIS URL IN YOUR BROWSER TO AUTHORIZE:\n"
        "{url}\n"
        + "=" * 60 + "\n"
    )

    creds = flow.run_local_server(
        port=8085,
        open_browser=True,
        authorization_prompt_message=prompt,
        prompt="consent",
        access_type="offline",
        state=session_state,
    )

    # Save authorized credentials to the private directory
    with open(token_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"\nSuccessfully saved authorized token to {token_path}", flush=True)


if __name__ == "__main__":
    main()
