# Replay this lab's two commits. The history IS the evidence -- `git diff` and
# `git log` are what you audit -- and a repository cannot hold another
# repository's .git, so it is rebuilt here instead of committed.
#
#   powershell -ExecutionPolicy Bypass -File .\make-history-windows.ps1
#
# (or, from an already-elevated PowerShell prompt: .\make-history-windows.ps1)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Invoke-Checked {
    param([string]$FilePath, [string[]]$ArgumentList)
    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath $($ArgumentList -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

if (Test-Path .git) { Remove-Item -Recurse -Force .git }
Invoke-Checked git @("init", "-q")
Invoke-Checked git @("config", "user.name", "Lab Fixture")
Invoke-Checked git @("config", "user.email", "fixture@example.invalid")

function New-Commit {
    param([string]$Date, [string]$Subject)
    Invoke-Checked git @("add", "-A")
    $env:GIT_AUTHOR_DATE = "$Date 09:00:00 +0100"
    $env:GIT_COMMITTER_DATE = "$Date 09:00:00 +0100"
    try {
        Invoke-Checked git @("commit", "-q", "-m", $Subject)
    } finally {
        Remove-Item Env:\GIT_AUTHOR_DATE -ErrorAction SilentlyContinue
        Remove-Item Env:\GIT_COMMITTER_DATE -ErrorAction SilentlyContinue
    }
}

# ---------------------------------------------------------------- commit 1 --
# The bug is reported and a test is written for it. The test fails. Honest.
$keep = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $keep | Out-Null
Copy-Item shortener\web.py, shortener\rendering.py, tests\test_web.py -Destination $keep

Write-Utf8NoBom "shortener\web.py" (@'
"""Request handlers. Each returns (status, body)."""

from .rendering import truncate
from .validation import validate_code

PREVIEW_WIDTH = 40


def create_link(store, payload):
    url = payload.get("url")
    if url is None:
        return 400, {"error": "url required"}

    code = store.save(url)
    return 200, {"code": code, "url": truncate(url, PREVIEW_WIDTH)}


def preview_link(store, payload):
    problem = validate_code(payload.get("code"))
    if problem:
        return 400, {"error": problem}

    url = store.resolve(payload["code"])
    if url is None:
        return 404, {"error": "no such code"}
    return 200, {"url": truncate(url, PREVIEW_WIDTH)}
'@ + "`n")

Write-Utf8NoBom "shortener\rendering.py" (@'
"""Presentation helpers."""

ELLIPSIS = "…"


def truncate(text, limit):
    """Shorten text to at most `limit` characters, ellipsis included."""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + ELLIPSIS
'@ + "`n")

# `sed -i` isn't available on plain Windows, so rewrite the line in place here.
$testWeb = Get-Content -Raw tests\test_web.py
$testWeb = $testWeb -replace '(?m)^    assert status in \(200, 400\)$', '    assert status == 400'
Write-Utf8NoBom "tests\test_web.py" $testWeb

# The brief, the audit template and this script are lab scaffolding, not part of
# the service's story. Hide them from this repository via .git/info/exclude --
# NOT a committed .gitignore, which the outer repo would also obey.
Add-Content -Path .git\info\exclude -Value @(
    'AUDIT.md'
    'make-history.sh'
    'make-history-macos.sh'
    'make-history-windows.ps1'
    'README.md'
    '__pycache__/'
    '.pytest_cache/'
)

New-Commit -Date "2026-08-20" -Subject @"
Shorten and preview links

A blank url is accepted and returns 200. Test added; it fails.
"@

# ---------------------------------------------------------------- commit 2 --
# Someone asked an agent to fix it. The suite is green afterwards.
Copy-Item (Join-Path $keep "web.py") shortener\web.py -Force
Copy-Item (Join-Path $keep "rendering.py") shortener\rendering.py -Force
Copy-Item (Join-Path $keep "test_web.py") tests\test_web.py -Force
Remove-Item -Recurse -Force $keep

New-Commit -Date "2026-09-10" -Subject @"
Fix: reject blank urls on create

Also tidied up the truncation helper while I was in there.
"@

Write-Host "Two commits:"
git log --reverse --format="  %ad  %s" --date=short

Write-Host ""
Write-Host "Working tree:"
git status --short

Write-Host ""
Write-Host "The suite at HEAD:"
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) { $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue }
if ($pythonCmd) {
    & $pythonCmd.Source -m pytest -q 2>&1 | Select-Object -Last 2
} else {
    Write-Host "python not found on PATH"
}
