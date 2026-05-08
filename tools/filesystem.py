"""
Filesystem Tools - Create, read, list, delete files and folders
"""

import os
import shutil
from langchain.tools import tool


@tool
def create_folder(path: str) -> str:
    """Create a new folder at the specified path. 
    Example: create_folder('C:/Users/John/Desktop/MyProject')"""
    try:
        os.makedirs(path, exist_ok=True)
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
