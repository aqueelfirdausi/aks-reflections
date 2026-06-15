import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# When frozen by PyInstaller (--windowed), stdout is a NullWriter with no reconfigure().
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Double-click on the exe → no CLI args → default to serve.
if getattr(sys, "frozen", False) and len(sys.argv) == 1:
    os.chdir(os.path.dirname(sys.executable))
    sys.argv.append("serve")

AKS_FILE    = "reflections.json"
REGISTRY    = Path.home() / ".aks-reflections" / "projects.json"

# ── embedded dashboard ──────────────────────────────────────────────────────────

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AKS Reflections</title>
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg:     #07070f;
  --glass:  rgba(255,255,255,0.04);
  --gbord:  rgba(255,255,255,0.08);
  --ghover: rgba(255,255,255,0.07);
  --text:   #f1f5f9;
  --sub:    #94a3b8;
  --muted:  #64748b;
  --dim:    #334155;
  --green:  #4ade80;
  --blue:   #60a5fa;
  --purple: #a78bfa;
  --red:    #f87171;
  --orange: #fb923c;
  --amber:  #fbbf24;
}

body {
  background: var(--bg);
  background-image:
    radial-gradient(ellipse at 15% 40%, rgba(139,92,246,.13) 0%, transparent 55%),
    radial-gradient(ellipse at 85% 15%, rgba(59,130,246,.10) 0%, transparent 55%),
    radial-gradient(ellipse at 50% 95%, rgba(16,185,129,.06) 0%, transparent 50%);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
  min-height: 100vh;
  padding: 20px;
}

.glass {
  background: var(--glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--gbord);
  border-radius: 16px;
}

/* ── header ── */
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  margin-bottom: 14px;
  gap: 16px;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -.5px;
  white-space: nowrap;
}
.header-left h1 .accent { color: var(--purple); }
.header-left .sub {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--green);
  animation: pulse 2.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.25} }

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.proj-select {
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.12);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
  transition: border-color .2s;
  max-width: 200px;
}
.proj-select:hover  { border-color: rgba(167,139,250,.5); }
.proj-select:focus  { border-color: rgba(167,139,250,.7); }
.proj-select option { background: #0d0d1a; }

.copy-btn {
  background: linear-gradient(135deg, rgba(167,139,250,.18), rgba(96,165,250,.18));
  border: 1px solid rgba(167,139,250,.38);
  color: var(--text);
  padding: 9px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all .2s;
}
.copy-btn:hover {
  background: linear-gradient(135deg, rgba(167,139,250,.32), rgba(96,165,250,.32));
  border-color: rgba(167,139,250,.65);
  box-shadow: 0 4px 22px rgba(139,92,246,.22);
  transform: translateY(-1px);
}
.copy-btn:active { transform: translateY(0); }

/* ── action bar ── */
.actions {
  display: flex;
  gap: 9px;
  padding: 14px 18px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  align-items: center;
}

.act {
  padding: 8px 16px;
  border-radius: 9px;
  border: 1px solid;
  background: transparent;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all .18s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.act:hover  { transform: translateY(-1px); }
.act:active { transform: translateY(0); }

.act-done   { color: var(--green);  border-color: rgba(74,222,128,.32); }
.act-done:hover   { background: rgba(74,222,128,.11);  box-shadow: 0 0 18px rgba(74,222,128,.14); }
.act-bug    { color: var(--red);    border-color: rgba(248,113,113,.32); }
.act-bug:hover    { background: rgba(248,113,113,.11); box-shadow: 0 0 18px rgba(248,113,113,.14); }
.act-next   { color: var(--amber);  border-color: rgba(251,191,36,.32); }
.act-next:hover   { background: rgba(251,191,36,.11);  box-shadow: 0 0 18px rgba(251,191,36,.14); }
.act-status { color: var(--blue);   border-color: rgba(96,165,250,.32); }
.act-status:hover { background: rgba(96,165,250,.11);  box-shadow: 0 0 18px rgba(96,165,250,.14); }

.refresh-btn {
  margin-left: auto;
  background: none;
  border: 1px solid var(--dim);
  color: var(--muted);
  padding: 7px 13px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all .18s;
}
.refresh-btn:hover { border-color: var(--muted); color: var(--text); }

/* ── grid ── */
#grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  transition: opacity .2s;
}
@media (max-width: 860px) { #grid { grid-template-columns: repeat(2,1fr); } }
@media (max-width: 520px) { #grid { grid-template-columns: 1fr; } }

.card {
  padding: 18px 20px;
  min-height: 130px;
  transition: border-color .2s, transform .15s;
}
.card:hover { border-color: rgba(255,255,255,.13); }

.card-head {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 12px;
}
.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.card-label {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.badge {
  margin-left: auto;
  font-size: 10px;
  color: var(--muted);
  background: rgba(255,255,255,.07);
  padding: 2px 7px;
  border-radius: 10px;
}

.entry {
  font-size: 13px;
  line-height: 1.5;
  padding: 7px 0;
  border-bottom: 1px solid rgba(255,255,255,.05);
}
.entry:last-child  { border-bottom: none; padding-bottom: 0; }
.entry:first-child { padding-top: 0; }
.entry-text  { color: var(--text); display: block; }
.entry-time  { font-size: 11px; color: var(--muted); margin-top: 2px; display: block; }
.none        { font-size: 13px; color: var(--muted); font-style: italic; }

/* next task card — spans full row width */
.card-next {
  grid-column: 1 / -1;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: auto;
}
.card-next .card-head { margin-bottom: 0; flex-shrink: 0; }
.next-divider { width: 1px; height: 36px; background: rgba(255,255,255,.08); flex-shrink: 0; }
.next-body { flex: 1; }
.next-text { font-size: 16px; font-weight: 600; }
.next-time { font-size: 12px; color: var(--muted); margin-top: 3px; }

/* ── modal ── */
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.55);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  opacity: 0;
  pointer-events: none;
  transition: opacity .2s;
}
.overlay.open { opacity: 1; pointer-events: all; }

.modal {
  background: rgba(12,12,22,.96);
  border: 1px solid rgba(255,255,255,.11);
  border-radius: 18px;
  padding: 26px 28px;
  width: 100%;
  max-width: 460px;
  transform: translateY(14px) scale(.97);
  transition: transform .22s cubic-bezier(.34,1.56,.64,1);
}
.overlay.open .modal { transform: translateY(0) scale(1); }

.modal h2 { font-size: 15px; font-weight: 700; margin-bottom: 5px; }
.modal p  { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
.modal textarea {
  width: 100%;
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 10px;
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
  padding: 11px 13px;
  resize: none;
  height: 88px;
  outline: none;
  transition: border-color .2s;
}
.modal textarea:focus  { border-color: rgba(255,255,255,.24); }
.modal textarea.shake  { border-color: rgba(248,113,113,.6) !important; animation: shake .3s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)} }

.modal-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
}
.modal-hint { font-size: 11px; color: var(--dim); }
.modal-btns { display: flex; gap: 9px; }

.btn-cancel {
  background: none;
  border: 1px solid var(--dim);
  color: var(--muted);
  padding: 8px 16px;
  border-radius: 9px;
  font-size: 13px;
  cursor: pointer;
  transition: all .15s;
}
.btn-cancel:hover { border-color: var(--muted); color: var(--text); }

.btn-save {
  border: none;
  padding: 8px 20px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all .15s;
}
.btn-save:hover { opacity: .85; transform: translateY(-1px); }
.btn-save:active { transform: translateY(0); }

/* ── toast ── */
.toast {
  position: fixed;
  bottom: 26px; right: 26px;
  background: rgba(14,14,26,.96);
  border: 1px solid rgba(255,255,255,.11);
  border-radius: 12px;
  padding: 11px 18px;
  font-size: 13px;
  font-weight: 500;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 8px;
  transform: translateY(70px);
  opacity: 0;
  transition: all .25s cubic-bezier(.34,1.56,.64,1);
  pointer-events: none;
}
.toast.show { transform: translateY(0); opacity: 1; }
.toast.ok  { border-color: rgba(74,222,128,.4); }
.toast.err { border-color: rgba(248,113,113,.4); }
</style>
</head>
<body>

<header class="glass">
  <div class="header-left">
    <h1>AKS <span class="accent">Reflections</span> &mdash; <span id="proj-name">&hellip;</span></h1>
    <div class="sub">
      Last updated: <span id="last-upd">&mdash;</span>
      &nbsp;&middot;&nbsp;
      <span class="pulse"></span> live
    </div>
  </div>
  <div class="header-right">
    <select class="proj-select" id="proj-select" onchange="switchProject(this.value)" title="Switch project">
      <option value="">Loading projects&hellip;</option>
    </select>
    <button class="copy-btn" onclick="copyDump()">&#128203; Copy Dump</button>
  </div>
</header>

<div class="actions glass">
  <button class="act act-done"   onclick="openModal('done',       '&#10003; Log Done',     'What did you just finish building?',    '#4ade80')">&#10003; Done</button>
  <button class="act act-bug"    onclick="openModal('bug',        '&#128027; Bug Fix',     'What bug did you fix?',                 '#f87171')">&#128027; Bug Fix</button>
  <button class="act act-next"   onclick="openModal('next',       '&#8594; Next Task',     'What should be done next?',             '#fbbf24')">&#8594; Next Task</button>
  <button class="act act-status" onclick="openModal('inprogress', '&#8635; In Progress',   'What are you currently working on?',    '#60a5fa')">&#8635; In Progress</button>
  <button class="refresh-btn"    onclick="refresh()">&#8635; Refresh</button>
</div>

<div id="grid"></div>

<!-- modal -->
<div class="overlay" id="overlay" onclick="overlayClick(event)">
  <div class="modal">
    <h2 id="m-title"></h2>
    <p  id="m-desc"></p>
    <textarea id="m-input" placeholder="Type here&hellip;"></textarea>
    <div class="modal-foot">
      <span class="modal-hint">Ctrl+Enter to save &middot; Esc to cancel</span>
      <div class="modal-btns">
        <button class="btn-cancel" onclick="closeModal()">Cancel</button>
        <button class="btn-save"   onclick="submitModal()" id="m-save">Save</button>
      </div>
    </div>
  </div>
</div>

<!-- toast -->
<div class="toast" id="toast"></div>

<script>
var _action  = null;
var _mtime   = 0;
var _toastTm = null;

// ── api ───────────────────────────────────────────────────────────────────────

async function apiFetch(path) {
  var r = await fetch(path);
  if (!r.ok) throw new Error(r.status);
  return r.json();
}

async function apiPost(path, body) {
  var r = await fetch(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error(r.status);
  return r.json();
}

// ── project switcher ──────────────────────────────────────────────────────────

async function loadProjects() {
  try {
    var res = await apiFetch('/api/projects');
    var sel = document.getElementById('proj-select');
    sel.innerHTML = '';
    if (!res.projects || !res.projects.length) {
      sel.innerHTML = '<option value="">No other projects</option>';
      return;
    }
    res.projects.forEach(function(p) {
      var opt = document.createElement('option');
      opt.value = p.path;
      opt.textContent = p.name;
      if (p.current) opt.selected = true;
      sel.appendChild(opt);
    });
  } catch(e) {
    document.getElementById('proj-select').innerHTML = '<option value="">—</option>';
  }
}

async function switchProject(path) {
  if (!path) return;
  try {
    await apiPost('/api/switch', {path: path});
    _mtime = 0;
    await loadData(false);
    await loadProjects();
    toast('Switched project', 'ok');
  } catch(e) {
    toast('Switch failed', 'err');
  }
}

// ── render ────────────────────────────────────────────────────────────────────

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

function eText(item) { return typeof item === 'string' ? item : (item && item.text || ''); }
function eAt(item)   { return typeof item === 'string' ? '' :  (item && item.at   || ''); }

function renderList(items) {
  if (!items || !items.length) return '<div class="none">(none)</div>';
  return items.map(function(item) {
    var t  = esc(eText(item));
    var at = eAt(item);
    return '<div class="entry"><span class="entry-text">' + t + '</span>' +
           (at ? '<span class="entry-time">' + esc(at) + '</span>' : '') + '</div>';
  }).join('');
}

function render(d) {
  // header
  document.getElementById('proj-name').textContent = d.project_name || '—';
  var raw = d.last_updated || '';
  var upd = raw;
  if (raw) {
    try {
      upd = raw.replace('T',' ').replace('Z',' UTC');
    } catch(e) {}
  }
  document.getElementById('last-upd').textContent = upd;

  // sections
  var sections = [
    {key:'what_is_built',  label:'What is Built',  color:'#4ade80', list:true},
    {key:'in_progress',    label:'In Progress',     color:'#60a5fa', list:true},
    {key:'decisions_made', label:'Decisions Made',  color:'#a78bfa', list:true},
    {key:'bugs_fixed',     label:'Bugs Fixed',      color:'#f87171', list:true},
    {key:'do_not_touch',   label:'Do Not Touch',    color:'#fb923c', list:true},
  ];

  var html = sections.map(function(s) {
    var items = d[s.key] || [];
    return '<div class="card glass">' +
      '<div class="card-head">' +
        '<div class="dot" style="background:' + s.color + '"></div>' +
        '<span class="card-label" style="color:' + s.color + '">' + esc(s.label) + '</span>' +
        (items.length ? '<span class="badge">' + items.length + '</span>' : '') +
      '</div>' +
      renderList(items) +
      '</div>';
  }).join('');

  // next task — full-width row
  var nt     = d.next_task;
  var ntText = nt ? eText(nt) : '';
  var ntAt   = nt ? eAt(nt)   : '';
  html += '<div class="card card-next glass">' +
    '<div class="card-head">' +
      '<div class="dot" style="background:#fbbf24"></div>' +
      '<span class="card-label" style="color:#fbbf24">Next Task</span>' +
    '</div>' +
    '<div class="next-divider"></div>' +
    '<div class="next-body">' +
      (ntText
        ? '<div class="next-text" style="color:#fbbf24">' + esc(ntText) + '</div>' +
          (ntAt ? '<div class="next-time">' + esc(ntAt) + '</div>' : '')
        : '<div class="none">(none set)</div>') +
    '</div>' +
    '</div>';

  var grid = document.getElementById('grid');
  grid.innerHTML = html;
}

// ── data loading + polling ────────────────────────────────────────────────────

async function loadData(indicator) {
  try {
    var grid = document.getElementById('grid');
    grid.style.opacity = '.5';
    var d = await apiFetch('/api/data');
    render(d);
    grid.style.opacity = '1';
    if (indicator) toast('Refreshed', 'ok');
  } catch(e) {
    document.getElementById('grid').style.opacity = '1';
    toast('Could not load reflections.json', 'err');
  }
}

async function pollMtime() {
  try {
    var res = await apiFetch('/api/mtime');
    if (_mtime && res.mtime !== _mtime) {
      await loadData(false);
    }
    _mtime = res.mtime;
  } catch(e) {}
}

function refresh() { loadData(true); }

// ── modal ─────────────────────────────────────────────────────────────────────

function openModal(action, title, desc, color) {
  _action = action;
  document.getElementById('m-title').textContent = title;
  document.getElementById('m-desc').textContent  = desc;
  document.getElementById('m-input').value = '';
  document.getElementById('m-input').className = '';
  var btn = document.getElementById('m-save');
  btn.style.background = color;
  btn.style.color = '#07070f';
  document.getElementById('overlay').classList.add('open');
  setTimeout(function(){ document.getElementById('m-input').focus(); }, 80);
}

function closeModal() {
  document.getElementById('overlay').classList.remove('open');
  _action = null;
}

function overlayClick(e) {
  if (e.target === document.getElementById('overlay')) closeModal();
}

async function submitModal() {
  var inp  = document.getElementById('m-input');
  var text = inp.value.trim();
  if (!text) {
    inp.className = 'shake';
    setTimeout(function(){ inp.className = ''; }, 400);
    return;
  }
  try {
    await apiPost('/api/write', {action: _action, text: text});
    closeModal();
    await loadData(false);
    toast('Saved', 'ok');
  } catch(e) {
    toast('Save failed', 'err');
  }
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeModal();
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    if (document.getElementById('overlay').classList.contains('open')) submitModal();
  }
});

// ── copy dump ─────────────────────────────────────────────────────────────────

async function copyDump() {
  try {
    var res = await apiFetch('/api/dump');
    await navigator.clipboard.writeText(res.text);
    toast('Copied to clipboard', 'ok');
  } catch(e) {
    toast('Copy failed — check browser permissions', 'err');
  }
}

// ── toast ─────────────────────────────────────────────────────────────────────

function toast(msg, type) {
  var el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast ' + type + ' show';
  clearTimeout(_toastTm);
  _toastTm = setTimeout(function(){ el.classList.remove('show'); }, 2400);
}

// ── boot ──────────────────────────────────────────────────────────────────────

loadData(false);
loadProjects();
setInterval(pollMtime, 2500);
</script>
</body>
</html>"""


# ── utilities ───────────────────────────────────────────────────────────────────

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def entry_text(item):
    if isinstance(item, dict):
        return item.get("text", "")
    return str(item)


def entry_at(item):
    if isinstance(item, dict):
        return item.get("at", "")
    return ""


def make_entry(text):
    return {"text": text, "at": now_ts()}


def load_data(path=None):
    target = path or AKS_FILE
    if not os.path.exists(target):
        print(f"Error: {target} not found. Run 'aks-reflections init' first.")
        sys.exit(1)
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {target} is corrupted (invalid JSON). Fix or delete it and run init again.")
        sys.exit(1)


def save_data(data, path=None):
    target = path or AKS_FILE
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def fmt_last_updated(raw):
    if not raw:
        return ""
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M") + " UTC"
    except ValueError:
        return raw


# ── global project registry ──────────────────────────────────────────────────

def load_registry():
    if not REGISTRY.exists():
        return []
    try:
        with open(REGISTRY, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_registry(projects):
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)


def register_project(name, path):
    """Add or update a project in the global registry."""
    projects = load_registry()
    path_str = str(Path(path).resolve())
    for p in projects:
        if p["path"] == path_str:
            p["name"] = name  # update name if renamed
            save_registry(projects)
            return
    projects.append({"name": name, "path": path_str})
    save_registry(projects)


def unregister_project(path):
    projects = load_registry()
    path_str = str(Path(path).resolve())
    projects = [p for p in projects if p["path"] != path_str]
    save_registry(projects)


# ── dump builder ──────────────────────────────────────────────────────────────

def build_dump(data):
    name    = data.get("project_name", "unknown")
    updated = fmt_last_updated(data.get("last_updated", ""))
    lines   = [f"=== AKS REFLECTION — {name} ===", f"Last updated: {updated}", ""]

    def section(title, items):
        lines.append(f"{title}:")
        if items:
            for item in items:
                text   = entry_text(item)
                at     = entry_at(item)
                suffix = f"  [{at}]" if at else ""
                lines.append(f"- {text}{suffix}")
        else:
            lines.append("- (none)")
        lines.append("")

    section("WHAT IS BUILT",   data.get("what_is_built",  []))
    section("IN PROGRESS",     data.get("in_progress",    []))
    section("DECISIONS MADE",  data.get("decisions_made", []))
    section("BUGS FIXED",      data.get("bugs_fixed",     []))
    section("DO NOT TOUCH",    data.get("do_not_touch",   []))

    next_task = data.get("next_task", "")
    lines.append("NEXT TASK:")
    if next_task:
        text   = entry_text(next_task)
        at     = entry_at(next_task)
        suffix = f"  [{at}]" if at else ""
        lines.append(f"- {text}{suffix}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("=== END OF REFLECTION ===")
    lines.append("Paste this at the start of any AI chat to restore full context.")
    return "\n".join(lines)


# ── HTTP server ─────────────────────────────────────────────────────────────────

# Mutable server state — active project path (can be switched at runtime)
_active_path = [AKS_FILE]   # list so it's mutable from handler


class AKSHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence default access log

    def _send(self, body, content_type, status=200):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, status=200):
        self._send(json.dumps(data, ensure_ascii=False), "application/json; charset=utf-8", status)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            self._send(HTML_PAGE, "text/html; charset=utf-8")

        elif path == "/api/data":
            try:
                self._json(load_data(_active_path[0]))
            except SystemExit:
                self._json({"error": "reflections.json not found"}, 404)

        elif path == "/api/mtime":
            mtime = os.path.getmtime(_active_path[0]) if os.path.exists(_active_path[0]) else 0
            self._json({"mtime": mtime})

        elif path == "/api/dump":
            try:
                self._json({"text": build_dump(load_data(_active_path[0]))})
            except SystemExit:
                self._json({"error": "reflections.json not found"}, 404)

        elif path == "/api/projects":
            cwd_file = str(Path(_active_path[0]).resolve())
            projects = load_registry()
            result = []
            for p in projects:
                proj_file = str(Path(p["path"]) / AKS_FILE)
                result.append({
                    "name":    p["name"],
                    "path":    proj_file,
                    "current": proj_file == cwd_file
                })
            self._json({"projects": result})

        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON"}, 400)
            return

        if path == "/api/switch":
            new_path = body.get("path", "").strip()
            if not new_path or not os.path.exists(new_path):
                self._json({"error": "project file not found"}, 404)
                return
            _active_path[0] = new_path
            self._json({"ok": True})
            return

        if path != "/api/write":
            self._json({"error": "not found"}, 404)
            return

        action = body.get("action", "")
        text   = body.get("text", "").strip()

        if not text:
            self._json({"error": "empty text"}, 400)
            return

        try:
            data = load_data(_active_path[0])
        except SystemExit:
            self._json({"error": "reflections.json not found"}, 404)
            return

        if   action == "done":        data["what_is_built"].append(make_entry(text))
        elif action == "bug":         data["bugs_fixed"].append(make_entry(text))
        elif action == "next":        data["next_task"] = make_entry(text)
        elif action == "inprogress":  data["in_progress"].append(make_entry(text))
        elif action == "decision":    data["decisions_made"].append(make_entry(text))
        elif action == "donttouch":   data["do_not_touch"].append(make_entry(text))
        else:
            self._json({"error": f"unknown action: {action}"}, 400)
            return

        save_data(data, _active_path[0])
        self._json({"ok": True})


# ── commands ────────────────────────────────────────────────────────────────────

def cmd_init(args):
    if os.path.exists(AKS_FILE):
        print(f"{AKS_FILE} already exists. Delete it first if you want to reinitialize.")
        sys.exit(1)
    name = args.name if args.name else os.path.basename(os.getcwd())
    data = {
        "project_name":  name,
        "last_updated":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "what_is_built": [],
        "in_progress":   [],
        "decisions_made":[],
        "bugs_fixed":    [],
        "do_not_touch":  [],
        "next_task":     ""
    }
    save_data(data)
    register_project(name, os.getcwd())
    print(f"Initialized {AKS_FILE} for project: {name}")
    print(f"Registered in global projects list.")


def cmd_done(args):
    text = args.text.strip()
    if not text:
        print("Error: description cannot be empty.")
        sys.exit(1)
    data = load_data()
    data["what_is_built"].append(make_entry(text))
    save_data(data)
    print(f"Logged as built: {text}")


def cmd_bug(args):
    text = args.text.strip()
    if not text:
        print("Error: description cannot be empty.")
        sys.exit(1)
    data = load_data()
    data["bugs_fixed"].append(make_entry(text))
    save_data(data)
    print(f"Bug fix logged: {text}")


def cmd_inprogress(args):
    text = args.text.strip()
    if not text:
        print("Error: description cannot be empty.")
        sys.exit(1)
    data = load_data()
    data["in_progress"].append(make_entry(text))
    save_data(data)
    print(f"Logged as in progress: {text}")


def cmd_decision(args):
    text = args.text.strip()
    if not text:
        print("Error: description cannot be empty.")
        sys.exit(1)
    data = load_data()
    data["decisions_made"].append(make_entry(text))
    save_data(data)
    print(f"Decision logged: {text}")


def cmd_donttouch(args):
    text = args.text.strip()
    if not text:
        print("Error: description cannot be empty.")
        sys.exit(1)
    data = load_data()
    data["do_not_touch"].append(make_entry(text))
    save_data(data)
    print(f"Logged as do not touch: {text}")


def cmd_next(args):
    text = args.text.strip()
    if not text:
        print("Error: task description cannot be empty.")
        sys.exit(1)
    data = load_data()
    data["next_task"] = make_entry(text)
    save_data(data)
    print(f"Next task set: {text}")


def cmd_status(args):
    data    = load_data()
    name    = data.get("project_name", "unknown")
    updated = fmt_last_updated(data.get("last_updated", ""))
    divider = "=" * 50

    print(divider)
    print(f"  AKS REFLECTIONS — {name}")
    if updated:
        print(f"  Last updated: {updated}")
    print(divider)

    def section(title, items):
        count = len(items) if items else 0
        label = f"  ({count})" if count else ""
        print(f"\n{title}{label}")
        if not items:
            print("  (none)")
            return
        for item in items:
            at     = entry_at(item)
            text   = entry_text(item)
            prefix = f"  [{at}]  " if at else "  "
            print(f"{prefix}{text}")

    section("WHAT IS BUILT",   data.get("what_is_built",  []))
    section("IN PROGRESS",     data.get("in_progress",    []))
    section("DECISIONS MADE",  data.get("decisions_made", []))
    section("BUGS FIXED",      data.get("bugs_fixed",     []))
    section("DO NOT TOUCH",    data.get("do_not_touch",   []))

    next_task = data.get("next_task", "")
    print("\nNEXT TASK")
    if next_task:
        at     = entry_at(next_task)
        text   = entry_text(next_task)
        prefix = f"  [{at}]  " if at else "  "
        print(f"{prefix}{text}")
    else:
        print("  (none)")

    print(f"\n{divider}")


def cmd_dump(args):
    data   = load_data()
    output = build_dump(data)
    print(output)

    if getattr(args, "copy", False):
        try:
            import pyperclip
            pyperclip.copy(output)
            print("\n[Copied to clipboard]")
        except ImportError:
            print("\nTip: install pyperclip for auto-copy  →  pip install pyperclip")


def cmd_register(args):
    """Register the current folder's project into the global list."""
    if not os.path.exists(AKS_FILE):
        print(f"Error: {AKS_FILE} not found. Run 'aks-reflections init' first.")
        sys.exit(1)
    data = load_data()
    name = data.get("project_name", os.path.basename(os.getcwd()))
    register_project(name, os.getcwd())
    print(f"Registered '{name}' → {os.getcwd()}")


def cmd_projects(args):
    """List all registered projects."""
    projects = load_registry()
    if not projects:
        print("No projects registered yet.")
        print("Tip: 'aks-reflections init' auto-registers, or use 'aks-reflections register' in existing projects.")
        return

    cwd_resolved = str(Path(os.getcwd()).resolve())
    divider = "=" * 50
    print(divider)
    print("  AKS REFLECTIONS — Registered Projects")
    print(divider)
    for i, p in enumerate(projects, 1):
        is_current = str(Path(p["path"]).resolve()) == cwd_resolved
        marker = "  ◀ current" if is_current else ""
        status = ""
        rf = Path(p["path"]) / AKS_FILE
        if not rf.exists():
            status = "  ⚠ reflections.json missing"
        print(f"  {i}. {p['name']}{marker}{status}")
        print(f"     {p['path']}")
    print(divider)


def cmd_switch(args):
    """Print cd command to switch to a registered project."""
    projects = load_registry()
    if not projects:
        print("No projects registered. Run 'aks-reflections init' in a project folder first.")
        sys.exit(1)

    name_query = args.name.lower()
    matches = [p for p in projects if name_query in p["name"].lower()]

    if not matches:
        print(f"No project matching '{args.name}' found.")
        print("Registered projects:")
        for p in projects:
            print(f"  {p['name']}  →  {p['path']}")
        sys.exit(1)

    if len(matches) > 1:
        print(f"Multiple matches for '{args.name}':")
        for p in matches:
            print(f"  {p['name']}  →  {p['path']}")
        print("Be more specific.")
        sys.exit(1)

    proj = matches[0]
    print(proj["path"])
    print(f"\n# To switch, run:")
    print(f"  cd \"{proj['path']}\"")


def cmd_unregister(args):
    """Remove current project from the global registry."""
    cwd = str(Path(os.getcwd()).resolve())
    projects_before = load_registry()
    unregister_project(cwd)
    projects_after = load_registry()
    if len(projects_before) == len(projects_after):
        print(f"This folder was not in the registry: {cwd}")
    else:
        print(f"Unregistered: {cwd}")


SECTION_MAP = {
    "done":       "what_is_built",
    "bugs":       "bugs_fixed",
    "inprogress": "in_progress",
    "decisions":  "decisions_made",
    "donttouch":  "do_not_touch",
    "next":       "next_task",
}

SECTION_LABELS = {
    "what_is_built":  "Done",
    "bugs_fixed":     "Bugs Fixed",
    "in_progress":    "In Progress",
    "decisions_made": "Decisions Made",
    "do_not_touch":   "Do Not Touch",
    "next_task":      "Next Task",
}


def cmd_search(args):
    data  = load_data()
    query = args.query.lower()

    sections = [
        ("what_is_built",  "Done"),
        ("in_progress",    "In Progress"),
        ("decisions_made", "Decisions Made"),
        ("bugs_fixed",     "Bugs Fixed"),
        ("do_not_touch",   "Do Not Touch"),
    ]

    hits = []
    for key, label in sections:
        for item in data.get(key, []):
            text = entry_text(item)
            if query in text.lower():
                hits.append((label, entry_at(item), text))

    nt = data.get("next_task", "")
    if nt:
        text = entry_text(nt)
        if query in text.lower():
            hits.append(("Next Task", entry_at(nt), text))

    if not hits:
        print(f"No results for '{args.query}'.")
        return

    print(f"{len(hits)} result{'s' if len(hits) != 1 else ''} for '{args.query}':\n")
    for label, at, text in hits:
        ts = f"  [{at}]" if at else ""
        print(f"  [{label}]{ts}")
        print(f"    {text}")


def cmd_clear(args):
    data = load_data()

    if args.all:
        if not args.confirm:
            print("This will erase all entries in every section.")
            print("Re-run with --confirm to proceed:")
            print("  python aks_reflections.py clear --all --confirm")
            sys.exit(1)
        cleared = []
        for key in ("what_is_built", "in_progress", "decisions_made", "bugs_fixed", "do_not_touch"):
            count = len(data.get(key, []))
            if count:
                cleared.append(f"  {SECTION_LABELS[key]} ({count} entries)")
            data[key] = []
        if data.get("next_task"):
            cleared.append("  Next Task")
        data["next_task"] = ""
        save_data(data)
        if cleared:
            print("Cleared:")
            print("\n".join(cleared))
        else:
            print("Nothing to clear — all sections already empty.")
        return

    if not args.section:
        print("Specify a section to clear, or use --all --confirm to wipe everything.")
        print("Sections: done, bugs, inprogress, decisions, donttouch, next")
        sys.exit(1)

    key = SECTION_MAP.get(args.section.lower())
    if not key:
        print(f"Unknown section '{args.section}'. Choose from: {', '.join(SECTION_MAP)}")
        sys.exit(1)

    label = SECTION_LABELS[key]
    if key == "next_task":
        if not data.get("next_task"):
            print(f"{label} is already empty.")
        else:
            data["next_task"] = ""
            save_data(data)
            print(f"Cleared: {label}")
    else:
        count = len(data.get(key, []))
        if count == 0:
            print(f"{label} is already empty.")
        else:
            data[key] = []
            save_data(data)
            print(f"Cleared: {label} ({count} entr{'y' if count == 1 else 'ies'} removed)")


def cmd_export(args):
    data = load_data()
    name    = data.get("project_name", "unknown")
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [f"# {name}", f"*Exported on {updated}*", ""]

    def md_section(heading, items):
        lines.append(f"## {heading}")
        if items:
            for item in items:
                at   = entry_at(item)
                text = entry_text(item)
                ts   = f"`{at}` " if at else ""
                lines.append(f"- {ts}{text}")
        else:
            lines.append("- *(none)*")
        lines.append("")

    md_section("✅ Done",  data.get("what_is_built",  []))
    md_section("🐛 Bugs",  data.get("bugs_fixed",     []))
    md_section("🔄 In Progress", data.get("in_progress", []))
    md_section("🧠 Decisions",   data.get("decisions_made", []))
    md_section("🚫 Do Not Touch", data.get("do_not_touch", []))

    lines.append("## 🔜 Next")
    nt = data.get("next_task", "")
    if nt:
        at   = entry_at(nt)
        text = entry_text(nt)
        ts   = f"`{at}` " if at else ""
        lines.append(f"- {ts}{text}")
    else:
        lines.append("- *(none)*")
    lines.append("")

    raw_path = args.path if args.path else "reflections.md"
    out_path = Path(os.path.expanduser(raw_path)).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Exported to {out_path}")


def cmd_serve(args):
    if not os.path.exists(AKS_FILE):
        print(f"Error: {AKS_FILE} not found. Run 'aks-reflections init' first.")
        sys.exit(1)

    _active_path[0] = os.path.abspath(AKS_FILE)

    ports  = [5050, 5051, 5052, 8080, 8081]
    server = None
    port   = None
    for p in ports:
        try:
            server = HTTPServer(("localhost", p), AKSHandler)
            port   = p
            break
        except OSError:
            continue

    if not server:
        print(f"Error: could not bind to any port ({', '.join(str(p) for p in ports)}).")
        sys.exit(1)

    url = f"http://localhost:{port}"
    print(f"AKS Reflections Dashboard  →  {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


# ── CLI wiring ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="aks-reflections",
        description="AKS Reflections — local AI memory system for your projects"
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    p_init = sub.add_parser("init", help="Create reflections.json for this project")
    p_init.add_argument("name", nargs="?", help="Project name (defaults to folder name)")
    p_init.set_defaults(func=cmd_init)

    p_done = sub.add_parser("done", help="Log something as built")
    p_done.add_argument("text", help="What was built")
    p_done.set_defaults(func=cmd_done)

    p_bug = sub.add_parser("bug", help="Log a bug fix")
    p_bug.add_argument("text", help="What was fixed")
    p_bug.set_defaults(func=cmd_bug)

    p_inprogress = sub.add_parser("inprogress", help="Log something as in progress")
    p_inprogress.add_argument("text", help="What you are working on")
    p_inprogress.set_defaults(func=cmd_inprogress)

    p_decision = sub.add_parser("decision", help="Log a decision made")
    p_decision.add_argument("text", help="What was decided")
    p_decision.set_defaults(func=cmd_decision)

    p_donttouch = sub.add_parser("donttouch", help="Mark something as do not touch")
    p_donttouch.add_argument("text", help="What to leave alone")
    p_donttouch.set_defaults(func=cmd_donttouch)

    p_next = sub.add_parser("next", help="Set the next task")
    p_next.add_argument("text", help="What to do next")
    p_next.set_defaults(func=cmd_next)

    p_dump = sub.add_parser("dump", help="Print full context to paste into any AI")
    p_dump.add_argument("--copy", action="store_true", help="Copy output to clipboard (requires pyperclip)")
    p_dump.set_defaults(func=cmd_dump)

    p_status = sub.add_parser("status", help="Pretty-print current project state in terminal")
    p_status.set_defaults(func=cmd_status)

    p_serve = sub.add_parser("serve", help="Open local web dashboard in browser")
    p_serve.set_defaults(func=cmd_serve)

    p_projects = sub.add_parser("projects", help="List all registered projects")
    p_projects.set_defaults(func=cmd_projects)

    p_register = sub.add_parser("register", help="Register this folder into the global projects list")
    p_register.set_defaults(func=cmd_register)

    p_unregister = sub.add_parser("unregister", help="Remove this folder from the global projects list")
    p_unregister.set_defaults(func=cmd_unregister)

    p_switch = sub.add_parser("switch", help="Find a registered project path by name")
    p_switch.add_argument("name", help="Project name (partial match works)")
    p_switch.set_defaults(func=cmd_switch)

    p_export = sub.add_parser("export", help="Export project to a Markdown file")
    p_export.add_argument("path", nargs="?", help="Output path (default: reflections.md)")
    p_export.set_defaults(func=cmd_export)

    p_search = sub.add_parser("search", help="Search entries across all sections")
    p_search.add_argument("query", help="Text to search for (case-insensitive)")
    p_search.set_defaults(func=cmd_search)

    p_clear = sub.add_parser("clear", help="Clear a section or all entries")
    p_clear.add_argument("section", nargs="?",
                         help="Section to clear: done, bugs, inprogress, decisions, donttouch, next")
    p_clear.add_argument("--all",     action="store_true", help="Clear every section")
    p_clear.add_argument("--confirm", action="store_true", help="Required with --all")
    p_clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
