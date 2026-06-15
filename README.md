# AKS Reflections

**Local AI memory system for your projects**

AKS Reflections keeps a living `reflections.json` file in each of your project folders, tracking what's been built, what's in progress, bugs fixed, decisions made, and what comes next. Run `dump` at any time to get a paste-ready context block for any AI chat — no cloud, no accounts, just a single Python file.

---

## Installation

No `pip install` needed. Just download `aks_reflections.py` and drop it into your project folder (or anywhere on your PATH).

**Requirements:** Python 3.7+ — no third-party dependencies.

```bash
# Optional: clipboard support for dump --copy
pip install pyperclip
```

---

## Commands

### `init [name]`
Create a `reflections.json` for the current project and register it in the global project list.

```bash
python aks_reflections.py init
python aks_reflections.py init "my-app"
```

---

### `done <text>`
Log something you just finished building into `what_is_built`.

```bash
python aks_reflections.py done "added user auth with JWT"
python aks_reflections.py done "wired up the dashboard API"
```

---

### `bug <text>`
Log a bug fix into `bugs_fixed`.

```bash
python aks_reflections.py bug "fixed Windows encoding crash on startup"
python aks_reflections.py bug "resolved race condition in save_data"
```

---

### `next <text>`
Set the single next task (replaces the previous one).

```bash
python aks_reflections.py next "add pagination to the projects list"
```

---

### `status`
Pretty-print the current project state in the terminal.

```bash
python aks_reflections.py status
```

Output:
```
==================================================
  AKS REFLECTIONS — my-app
  Last updated: 2026-06-15 05:30 UTC
==================================================

WHAT IS BUILT  (2)
  [2026-06-15 05:10]  added user auth with JWT
  [2026-06-15 05:28]  wired up the dashboard API

NEXT TASK
  [2026-06-15 05:30]  add pagination to the projects list
==================================================
```

---

### `dump [--copy]`
Print the full reflection as a plain-text context block, ready to paste into any AI chat. Add `--copy` to also copy it to the clipboard (requires `pyperclip`).

```bash
python aks_reflections.py dump
python aks_reflections.py dump --copy
```

---

### `serve`
Launch a local web dashboard and open it in the browser. Auto-refreshes every 2.5 seconds when the file changes. Supports logging entries directly from the UI.

```bash
python aks_reflections.py serve
# → AKS Reflections Dashboard  →  http://localhost:5050
```

---

### `projects`
List every project registered in the global registry. Marks the current folder with `◀ current`.

```bash
python aks_reflections.py projects
```

Output:
```
==================================================
  AKS REFLECTIONS — Registered Projects
==================================================
  1. my-app  ◀ current
     /home/user/projects/my-app
  2. side-project
     /home/user/projects/side-project
==================================================
```

---

### `register`
Manually register the current folder's project into the global list. (`init` does this automatically — use `register` for projects that already have a `reflections.json`.)

```bash
python aks_reflections.py register
```

---

### `unregister`
Remove the current folder from the global registry.

```bash
python aks_reflections.py unregister
```

---

### `switch <name>`
Find a registered project by name (partial match works) and print its path.

```bash
python aks_reflections.py switch side
# → /home/user/projects/side-project
# To switch, run:
#   cd "/home/user/projects/side-project"
```

---

## Multi-project support

AKS Reflections maintains a global registry at:

```
~/.aks-reflections/projects.json
```

Every `init` call registers the project automatically. You can also call `register` manually in any existing project. The `projects` command lists all registered projects, and the `serve` dashboard includes a project switcher dropdown so you can view any project without leaving the browser.

---

## Dashboard

Run `serve` in any project folder to open the web dashboard:

```bash
python aks_reflections.py serve
```

- Opens at `http://localhost:5050` (falls back to 5051, 5052, 8080, 8081 if busy)
- Live-updates every 2.5 seconds when `reflections.json` changes on disk
- **Done / Bug Fix / Next Task / In Progress** buttons open a modal to log entries without touching the terminal
- **Copy Dump** button copies the full AI context block to clipboard
- **Project switcher** dropdown in the header lets you flip between all registered projects instantly

---

## File layout

```
your-project/
├── aks_reflections.py   ← the whole tool, one file
└── reflections.json     ← auto-created by init, gitignored
```

Global registry (shared across all projects):
```
~/.aks-reflections/
└── projects.json
```
