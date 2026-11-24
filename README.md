# gmail-calendar MCP Server

A Model Context Protocol (MCP) server built with Python using the official MCP Python SDK (`FastMCP`) and stdio transport. It integrates with **Gmail** and **Google Calendar** while maintaining strict safety guarantees.

---

## Features & Safety Guarantees

- **Stdio Transport**: Seamlessly integrates with MCP hosts (Claude Desktop, Antigravity, Cursor, etc.).
- **Read-Only & Draft Only**: **No tools send emails or delete anything**. The draft tool only creates drafts for human review.
- **Privacy & Security**: Credentials and tokens are kept in an external directory (`GOOGLE_PRIVATE_DIR`) and are **never copied into this repository**. Secrets are never printed to logs or standard streams.
- **Headless Server**: **Never opens a browser from the server**, preventing hangs or crashes in stdio mode.
- **Timezone**: All calendar operations are localized to **`Asia/Jerusalem`**.

---

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Google API credentials (`client_secret*.json`) and an authorized `token.json` in your private folder (default: `C:\my-private`).

---

## Tools Exposed

The server exposes **exactly 6 tools**:

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `search_emails` | `query: str`, `max_results: int = 10` | Search Gmail messages matching a search query. |
| `read_email` | `message_id: str` | Read full details and content of an email by its message ID. |
| `create_draft` | `to: str`, `subject: str`, `body: str` | Create an email draft in Gmail without sending it. |
| `list_events` | `days_ahead: int = 7` | List upcoming Google Calendar events for a given number of days. |
| `find_free_slots` | `date: str`, `duration_minutes: int = 30` | Find available free time slots on a specific date in Asia/Jerusalem (08:00–18:00). |
| `create_event` | `title: str`, `start: str`, `end: str`, `description: str = ""` | Create a new calendar event in Google Calendar in Asia/Jerusalem. |

---

## Configuration

Set the environment variable `GOOGLE_PRIVATE_DIR` to specify the location of `client_secret*.json` and `token.json` (defaults to `C:\my-private` if unset):

### Windows (PowerShell)
```powershell
$env:GOOGLE_PRIVATE_DIR = "C:\my-private"
```

### Windows (CMD)
```cmd
set GOOGLE_PRIVATE_DIR=C:\my-private
```

---

## Running the MCP Server

Run the server using `uv`:

```bash
uv run python server.py
```

Or run via the project script:

```bash
uv run gmail-calendar
```

---

## MCP Host Configuration

Add this server to your MCP client configuration (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gmail-calendar": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\shams\\OneDrive\\Desktop\\l07",
        "run",
        "python",
        "server.py"
      ],
      "env": {
        "GOOGLE_PRIVATE_DIR": "C:\\my-private"
      }
    }
  }
}
```

---

## One-Time Authorization (If Needed)

If `token.json` is missing or needs initial authorization from `client_secret*.json`:
1. Run the standalone setup helper (outside the MCP server):
   ```bash
   uv run python setup_auth.py
   ```
2. Complete the OAuth consent in your browser once.
3. The generated `token.json` will be saved directly into `C:\my-private`.
4. Start the MCP server normally.

---

## Project Structure

```
├── .gitignore          # Ignores token.json, client_secret*.json, credentials.json, .env
├── .env.example        # Example configuration for GOOGLE_PRIVATE_DIR
├── pyproject.toml      # Project metadata & dependencies
├── auth.py             # Google OAuth token loader (headless, no secrets logged)
├── gmail_service.py    # Gmail operations (search, read, draft only)
├── calendar_service.py # Calendar operations (Asia/Jerusalem timezone)
├── server.py           # FastMCP server entry point (stdio transport)
├── setup_auth.py       # Standalone one-time OAuth authorization helper
└── README.md           # Documentation
```
*All Python files are kept strictly under 150 lines.*
