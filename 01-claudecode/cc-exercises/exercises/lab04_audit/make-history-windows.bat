@echo off
REM Replay this lab's two commits. The history IS the evidence -- `git diff` and
REM `git log` are what you audit -- and a repository cannot hold another
REM repository's .git, so it is rebuilt here instead of committed.
REM
REM   make-history.bat
REM
REM Requereix: Git for Windows (git al PATH), Python (com a "python"), i
REM PowerShell (inclos per defecte a Windows) per fer la substitucio tipus
REM "sed" i per agafar les 2 ultimes linies de sortida (equivalent a "tail -2").

setlocal
cd /d "%~dp0"

if exist ".git" rmdir /s /q ".git"
git init -q
git config user.name "Lab Fixture"
git config user.email "fixture@example.invalid"

REM ---------------------------------------------------------------- commit 1 --
REM The bug is reported and a test is written for it. The test fails. Honest.
set "KEEP=%TEMP%\labfixture_%RANDOM%_%RANDOM%"
mkdir "%KEEP%"
copy /y "shortener\web.py" "%KEEP%\web.py" >nul
copy /y "shortener\rendering.py" "%KEEP%\rendering.py" >nul
copy /y "tests\test_web.py" "%KEEP%\test_web.py" >nul

echo """Request handlers. Each returns (status, body).""">"shortener\web.py"
echo(>>"shortener\web.py"
echo from .rendering import truncate>>"shortener\web.py"
echo from .validation import validate_code>>"shortener\web.py"
echo(>>"shortener\web.py"
echo PREVIEW_WIDTH = 40>>"shortener\web.py"
echo(>>"shortener\web.py"
echo(>>"shortener\web.py"
echo def create_link(store, payload):>>"shortener\web.py"
echo     url = payload.get("url")>>"shortener\web.py"
echo     if url is None:>>"shortener\web.py"
echo         return 400, {"error": "url required"}>>"shortener\web.py"
echo(>>"shortener\web.py"
echo     code = store.save(url)>>"shortener\web.py"
echo     return 200, {"code": code, "url": truncate(url, PREVIEW_WIDTH)}>>"shortener\web.py"
echo(>>"shortener\web.py"
echo(>>"shortener\web.py"
echo def preview_link(store, payload):>>"shortener\web.py"
echo     problem = validate_code(payload.get("code"))>>"shortener\web.py"
echo     if problem:>>"shortener\web.py"
echo         return 400, {"error": problem}>>"shortener\web.py"
echo(>>"shortener\web.py"
echo     url = store.resolve(payload["code"])>>"shortener\web.py"
echo     if url is None:>>"shortener\web.py"
echo         return 404, {"error": "no such code"}>>"shortener\web.py"
echo     return 200, {"url": truncate(url, PREVIEW_WIDTH)}>>"shortener\web.py"

echo """Presentation helpers.""">"shortener\rendering.py"
echo(>>"shortener\rendering.py"
echo ELLIPSIS = "...">>"shortener\rendering.py"
echo(>>"shortener\rendering.py"
echo(>>"shortener\rendering.py"
echo def truncate(text, limit):>>"shortener\rendering.py"
echo     """Shorten text to at most `limit` characters, ellipsis included.""">>"shortener\rendering.py"
echo     if len(text) ^<= limit:>>"shortener\rendering.py"
echo         return text>>"shortener\rendering.py"
echo     return text[: limit - 1] + ELLIPSIS>>"shortener\rendering.py"

REM sed 's/^    assert status in (200, 400)$/    assert status == 400/' tests\test_web.py
powershell -NoProfile -Command "(Get-Content 'tests\test_web.py') -replace '^    assert status in \(200, 400\)$', '    assert status == 400' | Set-Content 'tests\test_web.py'"

REM The brief, the audit template and this script are lab scaffolding, not part of
REM the service's story. Hide them from this repository via .git/info/exclude --
REM NOT a committed .gitignore, which the outer repo would also obey.
echo AUDIT.md>>".git\info\exclude"
echo make-history.bat>>".git\info\exclude"
echo README.md>>".git\info\exclude"
echo __pycache__/>>".git\info\exclude"
echo .pytest_cache/>>".git\info\exclude"

set "MSG1=%TEMP%\labfixture_msg1_%RANDOM%.txt"
echo Shorten and preview links>"%MSG1%"
echo(>>"%MSG1%"
echo A blank url is accepted and returns 200. Test added; it fails.>>"%MSG1%"

call :commit "2026-08-20" "%MSG1%"
del "%MSG1%" >nul

REM ---------------------------------------------------------------- commit 2 --
REM Someone asked an agent to fix it. The suite is green afterwards.
copy /y "%KEEP%\web.py" "shortener\web.py" >nul
copy /y "%KEEP%\rendering.py" "shortener\rendering.py" >nul
copy /y "%KEEP%\test_web.py" "tests\test_web.py" >nul
rmdir /s /q "%KEEP%"

set "MSG2=%TEMP%\labfixture_msg2_%RANDOM%.txt"
echo Fix: reject blank urls on create>"%MSG2%"
echo(>>"%MSG2%"
echo Also tidied up the truncation helper while I was in there.>>"%MSG2%"

call :commit "2026-09-10" "%MSG2%"
del "%MSG2%" >nul

set "GIT_AUTHOR_DATE="
set "GIT_COMMITTER_DATE="

echo Two commits:
git log --format="  %%ad  %%s" --date=short --reverse
echo(
echo Working tree:
git status --short
echo(
echo The suite at HEAD:
python -m pytest -q 2>&1 | powershell -NoProfile -Command "$input | Select-Object -Last 2"

endlocal
exit /b 0

:commit
REM %~1 = date (YYYY-MM-DD)   %~2 = path to file with commit message
set "GIT_AUTHOR_DATE=%~1 09:00:00 +0100"
set "GIT_COMMITTER_DATE=%~1 09:00:00 +0100"
git add -A
git commit -q -F "%~2"
exit /b 0