# Part 1 — Using the GitHub MCP Server

This part shows how to connect an **existing** MCP server (GitHub's official one) to VS Code GitHub Copilot so Copilot can perform GitHub operations on your behalf.

---

## What is the GitHub MCP Server?

It is an MCP server maintained by GitHub that exposes your GitHub account as tools Copilot can call — searching repos, reading issues, creating PRs, listing branches, and more.

Official repo: https://github.com/github/github-mcp-server

---

## Setup (VS Code + GitHub Copilot)

### Step 1 — Enable MCP in VS Code settings

Open VS Code Settings (`Ctrl+,`) and search for `mcp`. Enable:
```
chat.mcp.enabled = true
```

### Step 2 — Open this folder as a workspace

Open the `exercise_5_mcp` folder in VS Code. The `.vscode/mcp.json` file already contains the GitHub server configuration:

```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/"
}
```

This uses GitHub's **remote hosted** MCP server over HTTP — no Docker, no local binary needed.

### Step 3 — Authenticate

1. Open the Copilot Chat panel (`Ctrl+Alt+I`)
2. In the chat input area, look for the MCP icon or the "Tools" button
3. You will see "github" listed — click **Auth** or **Connect**
4. VS Code will open a browser window to complete GitHub OAuth login
5. After authorising, the server status changes to connected

### Step 4 — Use it

Switch Copilot Chat to **Agent mode** (click the mode dropdown in the chat input).

Example prompts:
```
List my GitHub repositories
Show open issues in repo <owner>/<repo>
Create a new branch called feature/test in <owner>/<repo>
Summarise the latest 3 pull requests in <owner>/<repo>
```

Copilot will call the GitHub MCP tools automatically.

---

## Alternative: Personal Access Token (PAT)

If OAuth does not work in your environment, replace the `github` entry in `.vscode/mcp.json` with:

```json
"github": {
  "type": "stdio",
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
    "ghcr.io/github/github-mcp-server"
  ],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
  }
}
```

This runs the server in Docker and prompts for your PAT. Required scopes: `repo`, `read:user`, `read:org`.

---

## Available GitHub MCP Tools (examples)

| Tool | What it does |
|---|---|
| `search_repositories` | Search GitHub repos |
| `list_issues` | List issues in a repo |
| `create_issue` | Create a new issue |
| `get_pull_request` | Get PR details |
| `create_pull_request` | Open a new PR |
| `list_branches` | List branches in a repo |
| `get_file_contents` | Read a file from a repo |
| `push_files` | Push files to a branch |

---

## Key Concepts Learned

- **Existing MCP server**: You did not write any code — you just configured a server someone else built.
- **Remote transport**: The GitHub server uses `url` (HTTP/SSE) rather than `stdio`.
- **OAuth vs PAT**: Remote servers can authenticate via OAuth; local servers usually need API keys passed as env vars.
- **VS Code mcp.json**: The `inputs` array lets VS Code prompt you for secrets at connection time so they are never hardcoded.
