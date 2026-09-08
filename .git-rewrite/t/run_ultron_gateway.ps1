<#================================================================
  run_ultron_gateway.ps1
  ---------------------------------------------------------------
  One‑script bootstrap + run‑time for a local HTTP gateway that
  lets you interact with the ultron_agent repository.

  What it does (in order)

   1. Activate the existing .venv (you already have this)
   2. Install Flask‑related Python packages (if missing)
   3. Write two tiny Python modules:
        • gateway\utils.py   – git, file‑io and subprocess helpers
        • gateway\server.py – Flask API (protected by a bearer token)
   4. Determine an API secret token:
        • If the Windows env‑var ULTRON_API_TOKEN exists → use it
        • Otherwise generate a GUID, store it in ULTRON_API_TOKEN
   5. Launch the Flask server (Ctrl‑C to stop)

  Prerequisites
   • Python 3.10+ is on the PATH
   • You already have a virtual‑env at .venv (created by your own
     earlier bootstrap step)
   • Any external API keys you need (e.g. OpenAI, AWS) are already in
     the **Windows user environment** (they’ll be visible to the
     Python process automatically).

  Usage
   cd C:\Projects\ultron_agent_2
   .\run_ultron_gateway.ps1
================================================================#>

# -------------------------------------------------
# 0️⃣  Helper – abort on any error
# -------------------------------------------------
$ErrorActionPreference = 'Stop'

Write-Host "`n=== Ultron‑Agent local gateway – single‑script bootstrap ===`n"

# -------------------------------------------------
# 1️⃣  Activate the already‑existing virtual environment
# -------------------------------------------------
$venvPath = Join-Path $PSScriptRoot '.venv\Scripts\Activate.ps1'
if (-Not (Test-Path $venvPath)) {
    Write-Error "Virtual‑env not found at $venvPath. Create it first (python -m venv .venv)."
}
& $venvPath
Write-Host "✅ Activated .venv"

# -------------------------------------------------
# 2️⃣  Install Python dependencies (Flask, GitPython, …)
# -------------------------------------------------
$requirements = @"
Flask==3.0.3
Flask-HTTPAuth==4.8.0
GitPython==3.1.43
watchdog==4.0.1   # optional – enables auto‑reload while you develop
"@

$reqFile = Join-Path $PSScriptRoot 'gateway_requirements.txt'
$requirements | Out-File -Encoding UTF8 -FilePath $reqFile -Force

# pip may not be on PATH inside the venv on some machines – use the python
# executable directly to be safe.
python -m pip install --upgrade pip > $null
python -m pip install -r $reqFile
Write-Host "✅ Python packages installed"

# -------------------------------------------------
# 3️⃣  Write the two helper modules (utils.py + server.py)
# -------------------------------------------------
$gatewayDir = Join-Path $PSScriptRoot 'gateway'
if (-Not (Test-Path $gatewayDir)) { New-Item -ItemType Directory -Path $gatewayDir | Out-Null }

# ---------- utils.py ----------
$utilsCode = @"
import os
import subprocess
from pathlib import Path
from git import Repo, InvalidGitRepositoryError

BASE_DIR = Path(__file__).resolve().parents[1]   # repository root

# ---------- Git helpers ----------
def _repo():
    try:
        return Repo(BASE_DIR)
    except InvalidGitRepositoryError:
        raise RuntimeError("Directory is not a Git repository")

def git_status():
    return _repo().git.status()

def git_pull():
    return _repo().remotes.origin.pull()

def git_push():
    return _repo().remotes.origin.push()

# ---------- File helpers ----------
def list_files(rel_path: str = ""):
    target = (BASE_DIR / rel_path).resolve()
    if not target.is_dir():
        raise FileNotFoundError(f"Directory not found: {rel_path}")
    return sorted([p.relative_to(BASE_DIR).as_posix() for p in target.rglob('*') if p.is_file()])

def read_file(rel_path: str):
    p = (BASE_DIR / rel_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {rel_path}")
    return p.read_text(encoding='utf-8')

def write_file(rel_path: str, content: str):
    p = (BASE_DIR / rel_path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    return f"Wrote {rel_path}"

# ---------- Subprocess helper ----------
def run_command(cmd: str, cwd: str = None):
    cwd_path = BASE_DIR if cwd is None else (BASE_DIR / cwd)
    result = subprocess.run(
        cmd,
        cwd=cwd_path,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
"@
$utilsPath = Join-Path $gatewayDir 'utils.py'
$utilsCode | Out-File -Encoding UTF8 -FilePath $utilsPath -Force
Write-Host "✅ utils.py written"

# ---------- server.py ----------
$serverCode = @"
import os
from pathlib import Path
from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPTokenAuth
from utils import (
    git_status, git_pull, git_push,
    list_files, read_file, write_file,
    run_command,
)

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

# ------------------------------------------------------------------
# Load the secret token.
#   1) If a Windows user env‑var ULTRON_API_TOKEN exists → use it.
#   2) Otherwise look for a .env file (created by the bootstrap section).
# ------------------------------------------------------------------
TOKEN = os.getenv('ULTRON_API_TOKEN')
if not TOKEN:
    env_path = Path(__file__).parents[1] / '.env'
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            if line.startswith('API_TOKEN'):
                TOKEN = line.split('=', 1)[1].strip()
if not TOKEN:
    TOKEN = 'CHANGE_ME'   # should never happen – the bootstrap always sets it

@auth.verify_token
def verify_token(token):
    return token == TOKEN

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'repo_root': str(Path.cwd()),
        'token_present': bool(TOKEN and TOKEN != 'CHANGE_ME')
    })

# ------------------------------------------------------------------
# Git endpoints (protected)
# ------------------------------------------------------------------
@app.route('/git/status')
@auth.login_required
def git_status_route():
    return jsonify({'status': git_status()})

@app.route('/git/pull', methods=['POST'])
@auth.login_required
def git_pull_route():
    out = git_pull()
    return jsonify({'result': [str(r) for r in out]})

@app.route('/git/push', methods=['POST'])
@auth.login_required
def git_push_route():
    out = git_push()
    return jsonify({'result': [str(r) for r in out]})

# ------------------------------------------------------------------
# File helpers
# ------------------------------------------------------------------
@app.route('/files')
@auth.login_required
def files():
    rel = request.args.get('path', '')
    try:
        return jsonify({'files': list_files(rel)})
    except FileNotFoundError as e:
        abort(404, str(e))

@app.route('/files/read')
@auth.login_required
def file_read():
    rel = request.args.get('path')
    if not rel:
        abort(400, 'Missing ?path= query parameter')
    try:
        return jsonify({'content': read_file(rel)})
    except FileNotFoundError as e:
        abort(404, str(e))

@app.route('/files/write', methods=['POST'])
@auth.login_required
def file_write():
    data = request.get_json()
    if not data or 'path' not in data or 'content' not in data:
        abort(400, 'JSON must contain `path` and `content`')
    msg = write_file(data['path'], data['content'])
    return jsonify({'msg': msg})

# ------------------------------------------------------------------
# Run arbitrary shell commands (use with caution!)
# ------------------------------------------------------------------
@app.route('/cmd', methods=['POST'])
@auth.login_required
def cmd():
    """
    JSON body: { "cmd": "pytest -q", "cwd": "tests" (optional) }
    """
    payload = request.get_json()
    if not payload or 'cmd' not in payload:
        abort(400, 'JSON must contain `cmd`')
    result = run_command(payload['cmd'], payload.get('cwd'))
    return jsonify(result)

# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------
if __name__ == '__main__':
    # Bind only to localhost – keep it safe. Change to 0.0.0.0 if you tunnel it.
    app.run(host='127.0.0.1', port=5001, debug=False)
"@
$serverPath = Join-Path $gatewayDir 'server.py'
$serverCode | Out-File -Encoding UTF8 -FilePath $serverPath -Force
Write-Host "✅ server.py written"

# -------------------------------------------------
# 4️⃣  Create / confirm the bearer token
# -------------------------------------------------
if (-not $env:ULTRON_API_TOKEN) {
    # No Windows env‑var – generate one and store it both in env and .env
    $newToken = [guid]::NewGuid().ToString('N')
    $env:ULTRON_API_TOKEN = $newToken          # make it visible to this process
    $dotEnvPath = Join-Path $PSScriptRoot '.env'
    "API_TOKEN=$newToken" | Out-File -Encoding UTF8 -FilePath $dotEnvPath -Force
    Write-Host "`n🔑 Generated a new API token and stored it in:"
    Write-Host "   – Windows env‑var ULTRON_API_TOKEN (current session)"
    Write-Host "   – $dotEnvPath (for future sessions)"
} else {
    $newToken = $env:ULTRON_API_TOKEN
    Write-Host "`n🔑 Using existing Windows env‑var ULTRON_API_TOKEN"
}
Write-Host "Token (keep it secret!): $newToken`n"

# -------------------------------------------------
# 5️⃣  Launch the Flask gateway
# -------------------------------------------------
Write-Host "🚀 Starting the Ultron‑Agent HTTP gateway..."
Write-Host "   → URL: http://127.0.0.1:5001"
Write-Host "   → Use the Bearer token shown above in the `Authorization:` header."
Write-Host "   → Press Ctrl‑C to stop."
Write-Host ""

# Run the server in the foreground (same window). If you prefer background,
# replace the line with `Start-Process python -ArgumentList $serverPath -NoNewWindow`.
python $serverPath
