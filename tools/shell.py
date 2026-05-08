"""
Shell Tools - Run Windows commands and open applications
"""

import subprocess
import os
from langchain.tools import tool


@tool
def run_command(command: str) -> str:
    """Run a Windows shell command and return the output.
    Use for: ipconfig, ping, tasklist, dir, systeminfo, etc.
    Example: run_command('ipconfig') or run_command('ping google.com -n 2')"""
    try:
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

    try:
        subprocess.Popen(executable, shell=True)
        return f"✅ Opened: {app_name}"
    except Exception as e:
        return f"❌ Could not open {app_name}: {e}"
