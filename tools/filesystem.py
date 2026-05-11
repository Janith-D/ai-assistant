"""
Filesystem Tools - Create, read, list, delete files and folders
"""

import os
import shutil
import fnmatch
from datetime import datetime
import json
import config
from langchain_core.tools import tool


@tool
def create_folder(path: str) -> str:
    """Create a new folder at the specified path. 
    Example: create_folder('C:/Users/John/Desktop/MyProject')"""
    try:
        os.makedirs(path, exist_ok=True)
        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - create_folder - {json.dumps({'path': path})}\n")
        except Exception:
            pass
        return f"✅ Folder created successfully: {path}"
    except PermissionError:
        return f"❌ Permission denied: Cannot create folder at {path}"
    except Exception as e:
        return f"❌ Error creating folder: {e}"


@tool
def list_directory(path: str = ".") -> str:
    """List all files and folders in a directory.
    Example: list_directory('C:/Users/John/Desktop')"""
    try:
        items = os.listdir(path)
        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            from datetime import datetime as _dt
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{_dt.utcnow().isoformat()} - list_directory - {json.dumps({'path': path})}\n")
        except Exception:
            pass
        if not items:
            return f"📁 Directory is empty: {path}"
        
        folders = [f"📁 {i}" for i in items if os.path.isdir(os.path.join(path, i))]
        files = [f"📄 {i}" for i in items if os.path.isfile(os.path.join(path, i))]
        
        result = f"Contents of {path}:\n"
        result += "\n".join(folders + files)
        result += f"\n\nTotal: {len(folders)} folders, {len(files)} files"
        return result
    except FileNotFoundError:
        return f"❌ Directory not found: {path}"
    except PermissionError:
        return f"❌ Permission denied to access: {path}"
    except Exception as e:
        return f"❌ Error listing directory: {e}"


@tool
def read_file(path: str) -> str:
    """Read and return the contents of a text file.
    Example: read_file('C:/Users/John/notes.txt')"""
    try:
        size = os.path.getsize(path)
        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - read_file - {json.dumps({'path': path, 'size': size})}\n")
        except Exception:
            pass
        if size > 100_000:  # 100KB limit
            return f"⚠ File is too large ({size} bytes). Please use a smaller file."
        
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return f"📄 Contents of {path}:\n\n{content}"
    except FileNotFoundError:
        return f"❌ File not found: {path}"
    except PermissionError:
        return f"❌ Permission denied to read: {path}"
    except Exception as e:
        return f"❌ Error reading file: {e}"


@tool
def delete_file(path: str) -> str:
    """Delete a file or folder. USE WITH CAUTION - this is permanent!
    Example: delete_file('C:/Users/John/old_file.txt')"""
    try:
        # Log tool usage
        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} - delete_file - {json.dumps({'path': path})}\n")
        except Exception:
            pass
        if os.path.isfile(path):
            os.remove(path)
            return f"✅ File deleted: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"✅ Folder and all contents deleted: {path}"
        else:
            return f"❌ Path not found: {path}"
    except PermissionError:
        return f"❌ Permission denied to delete: {path}"
    except Exception as e:
        return f"❌ Error deleting: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write text content to a file (creates parent folders when needed).
    Example: write_file('C:/Users/John/Desktop/notes.txt', 'hello world')"""
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(
                    f"{datetime.utcnow().isoformat()} - write_file - "
                    f"{json.dumps({'path': path, 'chars': len(content)})}\n"
                )
        except Exception:
            pass

        return f"✅ File written: {path} ({len(content)} chars)"
    except PermissionError:
        return f"❌ Permission denied to write: {path}"
    except Exception as e:
        return f"❌ Error writing file: {e}"


@tool
def search_files(root_path: str, pattern: str = "*") -> str:
    """Recursively search files by wildcard pattern under a directory.
    Examples: search_files('C:/Users/John/Desktop', '*.txt'), search_files('.', 'config.py')"""
    try:
        if not os.path.exists(root_path):
            return f"❌ Path not found: {root_path}"

        matches = []
        for base, _, files in os.walk(root_path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    matches.append(os.path.join(base, name))
                    if len(matches) >= 100:
                        break
            if len(matches) >= 100:
                break

        try:
            os.makedirs(config.LOGS_DIR, exist_ok=True)
            with open(config.LOGS_DIR + "/tool_calls.log", "a", encoding="utf-8") as lf:
                lf.write(
                    f"{datetime.utcnow().isoformat()} - search_files - "
                    f"{json.dumps({'root_path': root_path, 'pattern': pattern, 'count': len(matches)})}\n"
                )
        except Exception:
            pass

        if not matches:
            return f"🔎 No files found matching '{pattern}' in {root_path}"

        lines = [f"🔎 Found {len(matches)} file(s) for '{pattern}' in {root_path}:"]
        lines.extend(matches)
        if len(matches) >= 100:
            lines.append("⚠ Showing first 100 matches only.")
        return "\n".join(lines)
    except PermissionError:
        return f"❌ Permission denied while searching: {root_path}"
    except Exception as e:
        return f"❌ Error searching files: {e}"
