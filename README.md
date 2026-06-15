# AKS Reflections

**Local AI memory system for your projects**

AKS Reflections keeps a living `reflections.json` file in each project folder, tracking what's been built, what's in progress, decisions made, bugs fixed, and what comes next. Run `dump` at any time to get a paste-ready context block for any AI chat — so every new conversation starts with full project context. No cloud, no accounts, no dependencies. One Python file.

---

## Installation

Download `aks_reflections.py` and place it in your project folder or anywhere on your PATH.

**Requirements:** Python 3.7+ — no third-party packages needed.

```bash
# Optional: enables --copy flag on dump
pip install pyperclip
```

## Setup

```bash
cd your-project/
python aks_reflections.py init

# → Initialized reflections.json for project: your-project
# → Registered in global projects list.
```

Add `reflections.json` to your `.gitignore` — it's local state, not source code.

---

## Command Reference

| Command | What it does |
|---|---|
| `init [name]` | Create `reflections.json` and register the project |
| `done <text>` | Log a completed item (What is Built) |
| `bug <text>` | Log a bug fix |
| `inprogress <text>` | Log something currently being worked on |
| `decision <text>` | Log a decision made |
| `donttouch <text>` | Mark something that should not be changed |
| `next <text>` | Set the next task (replaces the previous one) |
| `undo` | Remove the most recently added entry |
| `rename <name>` | Rename the project, syncs registry |
| `status` | Pretty-print all sections in the terminal |
| `dump [--copy]` | Print AI-ready context block; optionally copy to clipboard |
| `export [path]` | Save project as a Markdown file |
| `search <query>` | Case-insensitive search across all sections |
| `clear <section>` | Clear a named section |
| `clear --all --confirm` | Wipe all sections (requires `--confirm`) |
| `serve` | Open live web dashboard in browser |
| `projects` | List all registered projects |
| `register` | Register the current folder in the global list |
| `unregister` | Remove the current folder from the global list |
| `switch <name>` | Print the path to a registered project by name |

---

## Example Usage

### `init`

```bash
python aks_reflections.py init
python aks_reflections.py init "my-api"
```

Creates `reflections.json` in the current folder and registers the project globally. The name defaults to the folder name if omitted.

---

### `done`

```bash
python aks_reflections.py done "added JWT authentication"
# Logged as built: added JWT authentication
```

Appends a timestamped entry to the **What is Built** section.

---

### `bug`

```bash
python aks_reflections.py bug "fixed null pointer on empty config file"
# Bug fix logged: fixed null pointer on empty config file
```

Appends to **Bugs Fixed**.

---

### `inprogress`

```bash
python aks_reflections.py inprogress "refactoring the database layer"
# Logged as in progress: refactoring the database layer
```

Appends to **In Progress**.

---

### `decision`

```bash
python aks_reflections.py decision "use PostgreSQL over SQLite for multi-user support"
# Decision logged: use PostgreSQL over SQLite for multi-user support
```

Appends to **Decisions Made**.

---

### `donttouch`

```bash
python aks_reflections.py donttouch "legacy_auth.py — clients depend on exact response shape"
# Logged as do not touch: legacy_auth.py — clients depend on exact response shape
```

Appends to **Do Not Touch**.

---

### `next`

```bash
python aks_reflections.py next "add rate limiting to the API"
# Next task set: add rate limiting to the API
```

Sets the single **Next Task** field, replacing whatever was there before.

---

### `undo`

```bash
python aks_reflections.py done "oops wrong entry"
python aks_reflections.py undo
# Undone [Done]: oops wrong entry
```

Removes the most recently added entry across all sections, determined by timestamp. Works on any section including Next Task. No confirmation needed — it's just one step back.

---

### `rename`

```bash
python aks_reflections.py rename "my-api-v2"
# Renamed: 'my-api' → 'my-api-v2'
```

Updates `project_name` in `reflections.json` and syncs the entry in `~/.aks-reflections/projects.json` in a single step. The `projects` list and dashboard header both reflect the new name immediately.

---

### `status`

```bash
python aks_reflections.py status
```

```
==================================================
  AKS REFLECTIONS — my-api
  Last updated: 2026-06-15 14:00 UTC
==================================================

WHAT IS BUILT  (2)
  [2026-06-15 13:45]  added JWT authentication
  [2026-06-15 13:52]  fixed null pointer on empty config file

IN PROGRESS  (1)
  [2026-06-15 13:58]  refactoring the database layer

DECISIONS MADE  (1)
  [2026-06-15 13:50]  use PostgreSQL over SQLite for multi-user support

NEXT TASK
  [2026-06-15 14:00]  add rate limiting to the API
==================================================
```

---

### `dump`

```bash
python aks_reflections.py dump
python aks_reflections.py dump --copy   # also copies to clipboard (requires pyperclip)
```

Prints a plain-text context block. Paste it at the start of any AI chat to instantly restore full project context. `--copy` puts it in the clipboard automatically.

---

### `search`

```bash
python aks_reflections.py search auth
# 2 results for 'auth':
#
#   [Done]  [2026-06-15 13:45]
#     added JWT authentication
#   [Decisions Made]  [2026-06-15 13:50]
#     use PostgreSQL over SQLite for multi-user support
```

Case-insensitive substring match. Searches all six sections including Next Task.

---

### `export`

```bash
python aks_reflections.py export                      # → reflections.md in current dir
python aks_reflections.py export ~/docs/my-api.md     # absolute path
python aks_reflections.py export reports/week-1.md    # relative path, dirs auto-created
```

Saves all sections as a formatted Markdown file with emoji headings and timestamps.

---

### `clear`

```bash
python aks_reflections.py clear done         # clears What is Built
python aks_reflections.py clear bugs         # clears Bugs Fixed
python aks_reflections.py clear inprogress   # clears In Progress
python aks_reflections.py clear decisions    # clears Decisions Made
python aks_reflections.py clear donttouch    # clears Do Not Touch
python aks_reflections.py clear next         # clears Next Task

python aks_reflections.py clear --all                 # blocked — prints re-run hint
python aks_reflections.py clear --all --confirm       # wipes all sections
```

Each clear prints how many entries were removed. `--all` without `--confirm` is blocked with an explicit re-run instruction.

---

### `serve`

```bash
python aks_reflections.py serve
# AKS Reflections Dashboard  →  http://localhost:5050
# Press Ctrl+C to stop.
```

Opens a local web dashboard. Tries ports 5050, 5051, 5052, 8080, 8081 in order.

- **Live reload** — auto-refreshes every 2.5 seconds when `reflections.json` changes
- **Inline logging** — Done / Bug Fix / Next Task / In Progress buttons log entries without the terminal
- **Copy Dump** — copies the full AI context block to clipboard
- **Project switcher** — dropdown in the header switches between all registered projects instantly

---

## Multi-project Workflow

AKS Reflections maintains a global registry at `~/.aks-reflections/projects.json`. Every `init` call registers automatically. You can manage as many projects as you like from a single install.

### Setting up multiple projects

```bash
cd ~/projects/api
python aks_reflections.py init "api"

cd ~/projects/frontend
python aks_reflections.py init "frontend"
```

### Listing all projects

```bash
python aks_reflections.py projects
```

```
==================================================
  AKS REFLECTIONS — Registered Projects
==================================================
  1. api
     /home/user/projects/api
  2. frontend  ◀ current
     /home/user/projects/frontend
==================================================
```

The `◀ current` marker shows which project your shell is in. A `⚠ reflections.json missing` warning appears if a registered folder no longer has its data file.

### Switching to another project

```bash
python aks_reflections.py switch api
# /home/user/projects/api
#
# To switch, run:
#   cd "/home/user/projects/api"
```

Partial name matching works — `switch ap` finds `api`. Prints the `cd` command to run.

### Registering an existing project

If your project already has a `reflections.json` but was never registered (e.g. created before v0.3):

```bash
python aks_reflections.py register
# Registered 'my-app' → /home/user/projects/my-app
```

### Removing a project from the registry

```bash
python aks_reflections.py unregister
# Unregistered: /home/user/projects/my-app
```

Only removes the registry entry — `reflections.json` is untouched.

### Switching projects in the dashboard

The `serve` dashboard has a project switcher dropdown in the header. Click any project name to load its data without leaving the browser. Entries logged from the dashboard go to whichever project is selected.

---

## Data Files

### `reflections.json`

Created by `init` in the current project folder. Contains all entries for that project.

```json
{
  "project_name": "my-api",
  "last_updated": "2026-06-15T14:00:00Z",
  "what_is_built": [
    { "text": "added JWT authentication", "at": "2026-06-15 13:45" }
  ],
  "in_progress": [],
  "decisions_made": [],
  "bugs_fixed": [],
  "do_not_touch": [],
  "next_task": { "text": "add rate limiting", "at": "2026-06-15 14:00" }
}
```

- Add to `.gitignore` — it's local state
- Backward compatible: entries can be plain strings (v0.1 format) or `{text, at}` dicts (v0.2+)
- `next_task` is a single value, not a list

### `~/.aks-reflections/projects.json`

Global registry shared across all projects. Created automatically on first `init` or `register`.

```json
[
  { "name": "my-api",     "path": "/home/user/projects/api" },
  { "name": "frontend",   "path": "/home/user/projects/frontend" }
]
```

- Lives in your home directory, not inside any project
- Updated automatically by `init`, `register`, `unregister`, and `rename`
- Used by `projects`, `switch`, and the dashboard project switcher

---

## Version History

| Version | What shipped |
|---|---|
| v0.1 | `init`, `done`, `bug`, `next`, `dump` — Windows UTF-8 encoding fixed |
| v0.2 | `status` command, auto-timestamps on all entries, backward compat with plain-string entries |
| v0.3 | Renamed to `aks-reflections`, data file renamed to `reflections.json`, multi-project support (`projects`, `register`, `unregister`, `switch`), web dashboard with project switcher |
| v0.4 | `export` command — saves project as Markdown, user-specified path, auto-creates directories |
| v0.5 | `clear` command — per-section or `--all --confirm`, safety guard, prints count removed |
| v0.6 | `search` command — case-insensitive across all sections, shows section + timestamp + text |
| v0.7 | `inprogress`, `decision`, `donttouch` commands — full CLI parity, all sections writable from terminal |
| v1.0 | Stable release — 14 commands, complete multi-project support, dashboard, export, search, clear |
| v1.1 | `undo` command (timestamp-based, tie-break with `>=`), `rename` command (syncs `reflections.json` + registry) |
