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
├── test_server.py      # MCP client test script
├── reflection.md       # Project reflection document
└── README.md           # Documentation
```
*All Python files are kept strictly under 150 lines.*

---

## Prompts Used Today

1. `Check that the folder C:\my-private contains a Google client file (client_secret*.json) and a token.json file. Only tell me whether each file exists and its date. Do NOT print the contents of these files.`
2. `now?`
3. `השם client_secret json עכשיו תבדוק`
4. `תבדוק לי עכשיו`
5. `Build an MCP server in Python in the current folder, named "gmail-calendar". Use the official MCP Python SDK (FastMCP), run it with uv, and use the stdio transport. It must reuse the Google client and token.json from last week. They are in the private folder C:\my-private; read that path from the environment variable GOOGLE_PRIVATE_DIR. Never copy these files into this project, never print secrets, and never open a browser from the server. Expose exactly these tools, each with a short, clear English description: 1. search_emails(query, max_results) 2. read_email(message_id) 3. create_draft(to, subject, body) - a DRAFT only 4. list_events(days_ahead) 5. find_free_slots(date, duration_minutes) 6. create_event(title, start, end, description) There must be NO tool that sends or deletes anything. Time zone: Asia/Jerusalem. Keep each Python file under 150 lines. Add a .gitignore for token.json, client_secret*.json, credentials.json and .env. Write a README.md that explains how to run it.`
6. `Show me the file tree of this folder. Then show a table of the tools in server.py: name, one-line description, and which Google API call each tool uses. Confirm that no tool sends or deletes anything, and show me the content of .gitignore.`
7. `Write and run a small test script, test_server.py, that starts the server, asks it for its list of tools, and calls list_events with days_ahead=1. Set GOOGLE_PRIVATE_DIR=C:\my-private for the test. Show me the output.`
8. `Register this server in Claude Code with "claude mcp add": local scope, name "gmail-calendar", stdio transport, the environment variable GOOGLE_PRIVATE_DIR=C:\my-private, and the command "uv run --directory <this folder> server.py". Then tell me exactly what to do next.`
9. `Add this MCP server to Antigravity's workspace MCP config file .agents/mcp_config.json (create it if missing): name "gmail-calendar", command "uv", args ["run", "--directory", "<this folder>", "server.py"], env GOOGLE_PRIVATE_DIR = C:\my-private. Keep valid JSON and show me the final file.`
10. `What do I have in my calendar tomorrow?`
11. `Please finish Step 6 in the current project. Run uv run python setup_auth.py with GOOGLE_PRIVATE_DIR set to C:\my-private. Preserve the Google client credentials in a separate file before replacing the incorrect token.json. If Google opens a sign-in or consent screen, pause so I can approve it myself. Then run uv run test_server.py and show the six tool names and the actual result of list_events(days_ahead=1). If it fails, report the exact error without printing any secrets or tokens.`
12. `I don’t see a Google authorization tab in Edge. Please check whether setup_auth.py is still running and give me the Google consent URL so I can open it myself. If the process already stopped, restart it and give me the new URL.`
13. `i did it`
14. `now?`
15. `Write a Gmail draft to myself with the subject "L07 test" and add a calendar event for today, 4 hours from now, called "MCP works".`
16. `Find a free hour tomorrow between 09:00 and 17:00 and add an event called "Study group" there.`
17. `Great. Now send the "L07 test" draft.`
18. `Delete the "Study group" event.`
19. `Initialize a git repository in this folder. Before the first commit, show me git status and confirm that no token.json, client_secret*.json or .env file will be committed. Then commit with the message "L07gmail-calendar MCP server".`
20. `Act as my meeting coordinator. Find the latest meeting request in my email. Check my calendar for that time. If I am free, create the event and prepare a reply draft confirming it. If I am busy, do not create an event; prepare a reply draft that suggests two free times. Never send anything. Show me what you did, step by step.`
21. `Create reflection.md with four empty sections: "What did we ask the agent?", "How did we check that the result is correct?", "Which tool did we leave out, and why?", "L05 vs L06: what changed?". Also add to README.md the list of prompts we used today. Then commit.`
