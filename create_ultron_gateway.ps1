<#================================================================
  create_ultron_gateway.ps1
  ---------------------------------------------------------------
  Run this once inside C:\Projects\ultron_agent_2.
  It creates the folder-structure and all the source files that
  your Ultron-Agent local HTTP gateway needs.

  What it does:
   • creates the folder  gateway\
   • writes gateway\requirements.txt
   • writes gateway\utils.py
   • writes gateway\server.py (Flask API)
   • writes setup.ps1   – bootstrap helper (activate venv, install deps,
     create secret token)
   • writes start_gateway.ps1 – short helper that launches the API
   • optionally writes a .env file with a generated API token
  -----------------------------------------------------------------
  Prerequisites:
   • PowerShell 5.1+ (built-in on Windows)
   • You already have a Python virtual-env at .venv (the original repo
     creates it). This script never touches that venv.
   • Any external API keys you need are already stored in Windows user
     environment variables (e.g. OPENAI_API_KEY). The gateway will see
     them automatically.
================================================================#>

# -------------------------------------------------
# 0️⃣  Fail fast on any error
# -------------------------------------------------
$ErrorActionPreference = 'Stop'

Write-Host "`n=== Creating Ultron-Agent gateway skeleton ===`n"

# -----------------------------------------------------------------
# 1️⃣  Resolve the repository root (the folder where this script lives)
# -----------------------------------------------------------------
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot
Write-Host "Repository root: $repoRoot"

# -----------------------------------------------------------------
# 2️⃣  Helper: write a text file from a here-string
# -----------------------------------------------------------------
function Write-File {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [string] $Content
    )
    $folder = Split-Path $Path -Parent
    if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
    $Content | Out-File -Encoding ASCII -FilePath $Path -Force
    Write-Host "✔ $Path"
}

# -----------------------------------------------------------------
# 3️⃣  Write gateway\requirements.txt
# -----------------------------------------------------------------
$reqTxt = @"
Flask==3.0.3
Flask-HTTPAuth==4.8.0
GitPython==3.1.43
watchdog==4.0.1   # optional – enables auto-reload while you develop
"@
Write-File -Path "$repoRoot\gateway\requirements.txt" -Content $reqTxt

# -----------------------------------------------------------------
# 4️⃣  Write gateway\utils.py  (the tiny helper library)
# -----------------------------------------------------------------
$utilsPy = @"
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
Write-File -Path "$repoRoot\gateway\utils.py" -Content $utilsPy

# -----------------------------------------------------------------
# 5️⃣  Write gateway\server.py  (the Flask API)
# -----------------------------------------------------------------
$serverPy = @"
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

# -----------------------------------------------------------------
# Load the secret token.
#   1) Prefer a Windows user env‑var ULTRON_API_TOKEN (you can set it
#      once via $env:ULTRON_API_TOKEN = '…' in your profile)
#   2) If not present, fall back to a .env file that we create later.
# -----------------------------------------------------------------
TOKEN = os.getenv('ULTRON_API_TOKEN')
if not TOKEN:
    dotenv_path = Path(__file__).parents[1] / '.env'
    if dotenv_path.is_file():
        for line in dotenv_path.read_text().splitlines():
            if line.startswith('API_TOKEN'):
                TOKEN = line.split('=', 1)[1].strip()
if not TOKEN:
    TOKEN = 'CHANGE_ME'   # should never happen – bootstrap creates it

@auth.verify_token
def verify_token(token):
    return token == TOKEN

# -------------------------------------------------
#  Basic health check
# -------------------------------------------------
@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'repo_root': str(Path.cwd()),
        'token_present': bool(TOKEN and TOKEN != 'CHANGE_ME')
    })

# -------------------------------------------------
#  Git endpoints (protected)
# -------------------------------------------------
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

# -------------------------------------------------
#  File helpers
# -------------------------------------------------
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

# -------------------------------------------------
#  Run arbitrary shell commands (use carefully!)
# -------------------------------------------------
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

# -------------------------------------------------
#  Main entry point
# -------------------------------------------------
if __name__ == '__main__':
    # Bind only to localhost – keep it safe. Change to 0.0.0.0 if you tunnel it.
    app.run(host='127.0.0.1', port=5001, debug=False)
"@
Write-File -Path "$repoRoot\gateway\server.py" -Content $serverPy

# -----------------------------------------------------------------
# 6️⃣  Write the bootstrap script – setup.ps1
# -----------------------------------------------------------------
$setupPs = @"
<#================================================================
  setup.ps1 – run once
  ---------------------------------------------------------------
  * Activates the existing .venv (you already have it)
  * Installs the Flask requirements (if they are missing)
  * Creates a secret bearer token:
        – uses Windows env‑var ULTRON_API_TOKEN if you already set it,
        – otherwise generates a GUID, writes it to .env and to the
          current session environment variable.
  * Prints a short usage note.
================================================================#>

`$ErrorActionPreference = 'Stop'

Write-Host "`n=== Ultron‑Agent gateway bootstrap ===`n"

# -------------------------------------------------
# 1️⃣ Activate the virtual‑env that already exists
# -------------------------------------------------
`$venv = Join-Path `$PSScriptRoot '.venv\Scripts\Activate.ps1'
if (-Not (Test-Path `$venv)) {
    Write-Error "Virtual‑env not found at `$venv – create it first (python -m venv .venv)."
}
& `$venv
Write-Host "✅ Activated .venv"

# -------------------------------------------------
# 2️⃣ Install the Flask deps (requirements.txt)
# -------------------------------------------------
`$reqFile = Join-Path `$PSScriptRoot 'gateway\requirements.txt'
python -m pip install --upgrade pip > `$null
python -m pip install -r `$reqFile
Write-Host "✅ Flask dependencies installed"

# -------------------------------------------------
# 3️⃣ Create / confirm the bearer token
# -------------------------------------------------
if (-not `$env:ULTRON_API_TOKEN) {
    `$newToken = [guid]::NewGuid().ToString('N')
    `$env:ULTRON_API_TOKEN = `$newToken
    `$dotEnv = Join-Path `$PSScriptRoot '.env'
    "API_TOKEN=$newToken" | Out-File -Encoding ASCII -FilePath `$dotEnv -Force
    Write-Host "🔑 Generated a new token and stored it in:`"
    Write-Host "   – Windows env‑var ULTRON_API_TOKEN (current session)`"
    Write-Host "   – $dotEnv (for future sessions)`"
} else {
    `$newToken = `$env:ULTRON_API_TOKEN
    Write-Host "🔑 Using existing Windows env‑var ULTRON_API_TOKEN"
}
Write-Host "Token (keep it secret!): $newToken`n"

# -------------------------------------------------
# 4️⃣ Show a tiny usage reminder
# -------------------------------------------------
Write-Host "You can now start the gateway with: .\start_gateway.ps1"
Write-Host "When the server is running, call it like:`"
Write-Host "   curl -H 'Authorization: Bearer $newToken' http://127.0.0.1:5001/health`"
"@
Write-File -Path "$repoRoot\setup.ps1" -Content $setupPs

# -----------------------------------------------------------------
# 7️⃣  Write the launch helper – start_gateway.ps1
# -----------------------------------------------------------------
$startPs = @"
<#================================================================
  start_gateway.ps1 – launch the Flask API
  ---------------------------------------------------------------
  * Activates the existing .venv
  * Prints the bearer token (so you can copy-paste it)
  * Starts the server (Ctrl-C to stop)
================================================================#>

`$ErrorActionPreference = 'Stop'

# -------------------------------------------------
# Activate venv
# -------------------------------------------------
& (Join-Path `$PSScriptRoot '.venv\Scripts\Activate.ps1')

# -------------------------------------------------
# Show the token
# -------------------------------------------------
`$token = (Get-Content (Join-Path `$PSScriptRoot '.env') `
    | Where-Object { `$_ -match '^API_TOKEN=' } `
    | ForEach-Object { `$_ -replace '^API_TOKEN=' })[0]

if (-not `$token) {
    `$token = `$env:ULTRON_API_TOKEN
}
Write-Host "`n=== Ultron‑Agent gateway ===`"
Write-Host "Token (Bearer): $token"
Write-Host "URL: http://127.0.0.1:5001"
Write-Host "Press Ctrl-C to stop the server.`n"

# -------------------------------------------------
# Run Flask
# -------------------------------------------------
python (Join-Path `$PSScriptRoot 'gateway\server.py')
"@
Write-File -Path "$repoRoot\start_gateway.ps1" -Content $startPs

# -----------------------------------------------------------------
# 8️⃣  (Optional) create a minimal .env if the user hasn't set the
#      Windows env-var already – the bootstrap will fill it later.
# -----------------------------------------------------------------
$envPath = Join-Path $repoRoot '.env'
if (-not (Test-Path $envPath)) {
    "# This file is generated by setup.ps1 if ULTRON_API_TOKEN is not set`n" |
        Out-File -Encoding ASCII -FilePath $envPath -Force
    Write-Host "✔ Created empty .env (will be populated by setup.ps1 if needed)"
}

Write-Host "`n=== All done! ==="
Write-Host "Next steps:"
Write-Host "  1️⃣  .\setup.ps1          # run once – installs deps & creates token"
Write-Host "  2️⃣  .\start_gateway.ps1  # launch the Flask API"
Write-Host "`nHappy hacking!"
