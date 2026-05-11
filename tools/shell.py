"""
Shell Tools - Run Windows commands and open applications
"""

import subprocess
import os
import shutil
from langchain_core.tools import tool
import config
import os
import json
from datetime import datetime


def _resolve_executable(executable: str) -> str:
    """Resolve a runnable path for common Windows apps."""
    executable_lower = executable.lower().strip()

    browser_candidates = {
        "chrome.exe": [
            os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ],
        "msedge.exe": [
            os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        ],
        "firefox.exe": [
            os.path.join(os.environ.get("ProgramFiles", ""), "Mozilla Firefox", "firefox.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Mozilla Firefox", "firefox.exe"),
        ],
    }

    if os.path.isabs(executable) and os.path.exists(executable):
        return executable

    which = shutil.which(executable)
    if which:
        return which

    for candidate in browser_candidates.get(executable_lower, []):
        if candidate and os.path.exists(candidate):
            return candidate

    return executable


@tool
def run_command(command: str) -> str:
    """Run a Windows shell command and return the output.
    Use for: ipconfig, ping, tasklist, dir, systeminfo, etc.
    Example: run_command('ipconfig') or run_command('ping google.com -n 2')"""
    try:
        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - run_command - {json.dumps({'command': command})}\n")
        except Exception:
            pass
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,         # 30 second timeout
            encoding="utf-8",
            errors="ignore"
        )
        output = result.stdout.strip() or result.stderr.strip()
        if not output:
            return f"✅ Command executed: {command} (no output)"
        return f"Command output:\n{output}"
    except subprocess.TimeoutExpired:
        return f"❌ Command timed out after 30 seconds: {command}"
    except Exception as e:
        return f"❌ Error running command: {e}"


@tool
def open_application(app_name: str) -> str:
    """Open a Windows application by name.
    Examples: open_application('notepad'), open_application('chrome'),
    open_application('calculator'), open_application('vs code')"""
    
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "vlc": "vlc.exe",
        "snipping tool": "snippingtool.exe",
    }

    app_lower = app_name.lower().strip()
    executable = app_map.get(app_lower, app_name)
    executable = _resolve_executable(executable)

    try:
        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - open_application - {json.dumps({'app': app_name})}\n")
        except Exception:
            pass
        if os.path.exists(executable):
            subprocess.Popen([executable], shell=False)
        else:
            subprocess.Popen(executable, shell=True)
        return f"✅ Opened: {app_name}"
    except Exception as e:
        return f"❌ Could not open {app_name}: {e}"
