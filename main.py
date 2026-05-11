"""
Personal AI Assistant - Main Entry Point
Run this file to start the assistant: python main.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage, AIMessage
import config
from agent import build_agent
from tools.filesystem import create_folder, list_directory, delete_file, read_file, write_file, search_files
from tools.system_info import get_system_info
from tools.shell import open_application
import json
import os
import re
from datetime import datetime
import time
from queue import Queue
import threading

console = Console()
chat_history = []

DANGEROUS_KEYWORDS = ["delete", "remove", "format", "rm -rf", "del ", "rmdir"]


def maybe_speak(text: str) -> None:
    """Best-effort TTS playback for assistant responses when enabled."""
    try:
        from voice.tts import speak_text

        # Avoid reading very long payloads aloud.
        speak_text((text or "")[:600])
    except Exception:
        return


def is_dangerous(text: str) -> bool:
    return any(word in text.lower() for word in DANGEROUS_KEYWORDS)


def is_system_info_request(text: str) -> bool:
    lower = text.lower()
    keywords = ["ram", "memory", "cpu", "disk", "ip address", "ip", "system info", "system information"]
    return any(keyword in lower for keyword in keywords)


def is_help_request(text: str) -> bool:
    lower = text.lower().strip()
    return lower in ["what can you do", "help", "commands", "what are the commands", "what can you do?"]


def resolve_time_date_query(user_input: str) -> str | None:
    lower = user_input.lower().strip()
    now = datetime.now()

    if any(phrase in lower for phrase in ["current time", "what time", "time now", "time is it"]):
        return f"🕒 Current time: {now.strftime('%I:%M:%S %p')}"

    if any(phrase in lower for phrase in ["current date", "today date", "what date", "date today"]):
        return f"📅 Today's date: {now.strftime('%A, %d %B %Y')}"

    if lower in ["time", "date"]:
        return (
            f"🕒 Current time: {now.strftime('%I:%M:%S %p')}\n"
            f"📅 Today's date: {now.strftime('%A, %d %B %Y')}"
        )

    return None


def resolve_system_info_query(user_input: str) -> str | None:
    lower = user_input.lower()
    if any(word in lower for word in ["ram", "memory"]):
        return get_system_info.invoke("ram")
    if "cpu" in lower or "processor" in lower:
        return get_system_info.invoke("cpu")
    if "disk" in lower or "storage" in lower or "drive" in lower:
        return get_system_info.invoke("disk")
    if "ip" in lower or "address" in lower:
        return get_system_info.invoke("ip")
    if "system info" in lower or "system information" in lower:
        return get_system_info.invoke("all")
    return None


def resolve_create_folder_target(user_input: str) -> str | None:
    """Resolve folder creation requests for Desktop paths."""
    lower = user_input.lower().strip()
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    if "desktop" not in lower:
        return None

    patterns = [
        r"\b(?:create|make|add)\s+(?:the\s+)?(?:folder|directory)\s+(?:named\s+|name\s+)?['\"]?([^'\"\n]+?)['\"]?\s+(?:in|on|under|inside)\s+desktop\b",
        r"\b(?:create|make|add)\s+['\"]?([^'\"\n]+?)['\"]?\s+(?:folder|directory)\s+(?:in|on|under|inside)\s+desktop\b",
        r"\b(?:create|make|add)\s+(?:the\s+)?(?:folder|directory)\s+['\"]?([^'\"\n]+?)['\"]?\s+(?:in|on|under|inside)\s+desktop\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            name = match.group(1).strip().strip(". ,")
            if name:
                return os.path.join(desktop, name)

    return None


def resolve_list_directory_target(user_input: str) -> str | None:
    """Resolve directory listing requests for Desktop paths."""
    lower = user_input.lower().strip()
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    if "desktop" in lower and any(word in lower for word in ["list", "show", "files", "folders", "contents"]):
        return desktop
    return None


def resolve_open_path_target(user_input: str) -> str | None:
    """Resolve requests to open files/folders/paths locally."""
    text = user_input.strip()
    lower = text.lower()

    if not re.search(r"\b(open|launch|start|run)\b", lower):
        return None

    # Open File Explorer directly
    if any(term in lower for term in ["open pc", "open this pc", "open my computer", "open file explorer", "open explorer"]):
        return "__OPEN_EXPLORER__"

    # Quoted explicit path: open "C:\\Users\\User\\Desktop"
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return os.path.expandvars(quoted.group(1).strip())

    home = os.path.expanduser("~")
    known_targets = {
        "desktop": os.path.join(home, "Desktop"),
        "downloads": os.path.join(home, "Downloads"),
        "documents": os.path.join(home, "Documents"),
        "pictures": os.path.join(home, "Pictures"),
        "videos": os.path.join(home, "Videos"),
        "music": os.path.join(home, "Music"),
    }
    for key, path in known_targets.items():
        if re.search(rf"\bopen\s+(?:the\s+)?{key}\b", lower):
            return path

    # open folder test in desktop / open file notes.txt in desktop
    in_desktop = re.search(
        r"\bopen\s+(?:the\s+)?(?:folder|file)\s+(?:named\s+|name\s+)?['\"]?([^'\"\n]+?)['\"]?\s+(?:in|on|from)\s+desktop\b",
        lower,
    )
    if in_desktop:
        name = in_desktop.group(1).strip().strip(". ,")
        if name:
            return os.path.join(home, "Desktop", name)

    # open c:\something (without quotes)
    raw_path = re.search(r"\bopen\s+([a-zA-Z]:\\[^\n]+)$", text.strip())
    if raw_path:
        return raw_path.group(1).strip().strip('"\'')

    return None


def _resolve_special_path(token: str) -> str:
    t = token.strip().strip('"\'')
    lower = t.lower()
    home = os.path.expanduser("~")
    mapping = {
        "desktop": os.path.join(home, "Desktop"),
        "downloads": os.path.join(home, "Downloads"),
        "documents": os.path.join(home, "Documents"),
        "pictures": os.path.join(home, "Pictures"),
    }
    return mapping.get(lower, os.path.expandvars(os.path.expanduser(t)))


def resolve_read_file_target(user_input: str) -> str | None:
    text = user_input.strip()
    lower = text.lower()
    if not lower.startswith("read file"):
        return None

    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return _resolve_special_path(quoted.group(1))

    path = text[len("read file"):].strip()
    return _resolve_special_path(path) if path else None


def resolve_write_file_request(user_input: str) -> tuple[str, str] | None:
    text = user_input.strip()
    # Supported format:
    # write file <path> :: <content>
    match = re.match(r"(?i)^write\s+file\s+(.+?)\s*::\s*(.+)$", text)
    if not match:
        return None
    path = _resolve_special_path(match.group(1))
    content = match.group(2)
    if not path or not content:
        return None
    return (path, content)


def resolve_search_files_request(user_input: str) -> tuple[str, str] | None:
    text = user_input.strip()
    # Supported formats:
    # search files <pattern> in <path>
    # find files <pattern> in <path>
    match = re.match(r"(?i)^(?:search|find)\s+files\s+(.+?)\s+in\s+(.+)$", text)
    if not match:
        return None
    pattern = match.group(1).strip().strip('"\'')
    root = _resolve_special_path(match.group(2))
    if not pattern or not root:
        return None
    return (root, pattern)


def open_path_local(path_or_sentinel: str) -> str:
    """Open an existing file/folder path locally on Windows."""
    try:
        if path_or_sentinel == "__OPEN_EXPLORER__":
            return open_application.invoke("explorer")

        target = os.path.expandvars(os.path.expanduser(path_or_sentinel))
        if not os.path.exists(target):
            return f"❌ Path not found: {target}"

        os.startfile(target)
        return f"✅ Opened: {target}"
    except Exception as e:
        return f"❌ Could not open path: {e}"


def resolve_delete_target(user_input: str) -> str | None:
    """Resolve a delete request into a concrete path when possible."""
    text = user_input.strip()
    lower = text.lower()
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    if "desktop" not in lower:
        return None

    # Common patterns like:
    # - delete the folder test1 in desktop
    # - remove test1 from desktop
    patterns = [
        r"\b(?:delete|remove)\s+(?:the\s+)?(?:folder|file)\s+(?:named\s+|name\s+)?['\"]?([^'\"\n]+?)['\"]?\s+(?:in|on|from)\s+desktop\b",
        r"\b(?:delete|remove)\s+['\"]?([^'\"\n]+?)['\"]?\s+(?:in|on|from)\s+desktop\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            name = match.group(1).strip().strip(". ,")
            if not name:
                continue
            return os.path.join(desktop, name)

    return None


def resolve_open_app(user_input: str) -> str | None:
    """Resolve a request like 'open chrome' into an app name."""
    lower = user_input.strip().lower()
    match = re.search(r"\b(?:open|launch|start|run)\s+(?:the\s+)?(.+?)\s*$", lower)
    if not match:
        return None

    app_name = match.group(1).strip().strip(". ,")
    if not app_name:
        return None

    # Normalize common browser/app names.
    aliases = {
        "google chrome": "chrome",
        "chrome browser": "chrome",
        "chrome": "chrome",
        "terminal": "powershell",
        "windows terminal": "powershell",
        "command prompt": "cmd",
        "cmd": "cmd",
        "powershell": "powershell",
        "edge": "edge",
        "microsoft edge": "edge",
        "firefox": "firefox",
        "vs code": "vs code",
        "vscode": "vs code",
        "visual studio code": "vs code",
        "notepad": "notepad",
        "calculator": "calculator",
        "paint": "paint",
    }

    return aliases.get(app_name, app_name)


def local_help_text() -> str:
    return (
        "I can handle these locally right now:\n"
        "- Open apps: open chrome, open edge, open firefox, open notepad, open calculator\n"
        "- Open PC locations: open desktop, open downloads, open documents, open file explorer\n"
        "- Open specific desktop item: open folder test in desktop\n"
        "- Time/date: current time, current date\n"
        "- System info: ram, cpu, disk, ip address\n"
        "- Files: create folder ... on desktop, list files on desktop, delete folder ... on desktop\n"
        "- Read file: read file <path>\n"
        "- Write file: write file <path> :: <content>\n"
        "- Search files: search files <pattern> in <path>\n"
        "- Voice mode: type voice (manual)\n"
        "- Push-to-talk: type ptt\n"
        "- Exit: type exit"
    )


def main():
    console.print(Panel.fit(
        "🤖 [bold cyan]Personal AI Assistant[/bold cyan]\n"
        "[dim]Powered by Google Gemini — fast cloud-based responses[/dim]\n\n"
        "Type [bold green]'voice'[/bold green] to switch to voice input\n"
        "Type [bold red]'exit'[/bold red] to quit",
        border_style="cyan"
    ))

    console.print("[yellow]⏳ Loading agent...[/yellow]")
    agent = build_agent()
    console.print("[green]✓ Agent ready! Ask me anything.\n[/green]")

    # Warm up STT model once at startup so users do not need to run stt.py manually.
    try:
        from voice.stt import preload_model

        with console.status("[cyan]🎙 Initializing voice STT model...[/cyan]"):
            preload = preload_model()
        if preload.ok:
            console.print("[dim]Voice STT ready[/dim]")
        else:
            console.print(f"[yellow]Voice STT preload issue: {preload.message}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Voice STT not initialized: {e}[/yellow]")

    wake_enabled = str(getattr(config, "WAKEWORD_ENABLED", "0")).strip().lower() in {"1", "true", "yes", "on"}

    # Start wake-word service (background) only when explicitly enabled.
    wake_queue = Queue()

    def on_wake():
        try:
            wake_queue.put_nowait(True)
        except Exception:
            pass

    if wake_enabled:
        try:
            from voice.wake import start_wake_service, stop_wake_service

            try:
                start_wake_service(on_wake)
                console.print("[dim]Wake-word service started (say '{}')[/dim]".format(config.WAKEWORD_PHRASE))
            except Exception as e:
                console.print(f"[yellow]Wake service not started: {e}[/yellow]")
        except ImportError:
            console.print("[yellow]Wake module not available. Install 'vosk' and 'sounddevice' to enable wake-word.[/yellow]")
    else:
        console.print("[dim]Wake-word service disabled. Type 'voice' to speak a command.[/dim]")

    def _wake_handler():
        from voice.stt import listen_async
        while True:
            try:
                wake_queue.get()
                console.print("[cyan]🎧 Wake word detected. Speak your command now...[/cyan]")
                post_delay_ms = int(getattr(config, "WAKE_POST_TRIGGER_DELAY_MS", 500))
                if post_delay_ms > 0:
                    time.sleep(post_delay_ms / 1000.0)
                # On wake, capture audio and transcribe, then inject into agent flow
                duration = int(getattr(config, "WAKE_COMMAND_DURATION", getattr(config, "VOICE_DURATION", 3)))
                retry_duration = int(getattr(config, "WAKE_RETRY_DURATION", max(duration + 1, 5)))
                samplerate = int(getattr(config, "VOICE_SAMPLE_RATE", 16000))
                voice_future = listen_async(duration=duration, samplerate=samplerate)
                # wait for result
                voice_result = voice_future.result()
                # Retry once if user paused after wake phrase and first capture is silent.
                if (not voice_result.ok) and voice_result.code == "silent_audio":
                    console.print("[yellow]I heard the wake word, but not the command. Please say it again...[/yellow]")
                    voice_future = listen_async(duration=retry_duration, samplerate=samplerate)
                    voice_result = voice_future.result()
                if not voice_result.ok:
                    console.print(f"[yellow]Wake voice capture failed: {voice_result.code} - {voice_result.message}[/yellow]")
                    continue
                spoken = voice_result.text
                if spoken:
                    console.print(f"[green]📝 You (via wake):[/green] {spoken}")
                    # run through agent
                    response = agent.invoke({"messages": chat_history + [HumanMessage(spoken)]})
                    # same extraction logic as below
                    def _extract_text(obj):
                        if hasattr(obj, 'content'):
                            obj = obj.content
                        if isinstance(obj, str):
                            return obj
                        if isinstance(obj, dict):
                            if 'text' in obj and isinstance(obj['text'], str):
                                return obj['text']
                            if 'message' in obj and isinstance(obj['message'], str):
                                return obj['message']
                            return json.dumps(obj, ensure_ascii=False, indent=2)
                        if isinstance(obj, (list, tuple)):
                            parts = []
                            for el in obj:
                                if isinstance(el, str):
                                    parts.append(el)
                                elif isinstance(el, dict) and 'text' in el:
                                    parts.append(el['text'])
                                elif hasattr(el, 'content'):
                                    parts.append(str(el.content))
                                else:
                                    parts.append(json.dumps(el, ensure_ascii=False))
                            return "\n\n".join(parts)
                        try:
                            return str(obj)
                        except Exception:
                            return json.dumps(obj, ensure_ascii=False, default=str)

                    if isinstance(response, dict) and "messages" in response:
                        last_message = response["messages"][-1]
                        answer = _extract_text(last_message)
                    else:
                        answer = _extract_text(response)

                    console.print(Panel(
                        answer,
                        title="[bold cyan]🤖 Assistant[/bold cyan]",
                        border_style="cyan"
                    ))
                    console.print()
                    maybe_speak(answer)
                    chat_history.append(HumanMessage(spoken))
                    chat_history.append(AIMessage(answer))
                else:
                    console.print("[yellow]Wake triggered, but no speech was recognized.[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Wake handler error: {e}[/yellow]")
                time.sleep(0.5)

    if wake_enabled:
        threading.Thread(target=_wake_handler, daemon=True).start()

    while True:
        try:
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("[cyan]Goodbye! 👋[/cyan]")
                break

            # Voice mode toggle
            if user_input.lower() in {"voice", "ptt"}:
                try:
                    from voice.stt import listen_async, listen_push_to_talk
                    is_manual_voice = user_input.lower() == "voice"

                    if user_input.lower() == "ptt":
                        voice_result = listen_push_to_talk()
                    else:
                        duration = int(getattr(config, "VOICE_DURATION", 3))
                        retry_duration = int(getattr(config, "VOICE_RETRY_DURATION", max(duration + 2, 5)))
                        samplerate = int(getattr(config, "VOICE_SAMPLE_RATE", 16000))
                        console.print("[cyan]🎤 Speak now...[/cyan]")
                        with console.status("[cyan]🎤 Listening and transcribing in background...[/cyan]"):
                            voice_future = listen_async(duration=duration, samplerate=samplerate)
                            while not voice_future.done():
                                time.sleep(0.05)
                            voice_result = voice_future.result()

                        # Retry once for manual voice if first capture was silent.
                        if (not voice_result.ok) and voice_result.code == "silent_audio" and is_manual_voice:
                            console.print("[yellow]I couldn't hear that clearly. Please say your command again...[/yellow]")
                            console.print("[cyan]🎤 Speak now...[/cyan]")
                            with console.status("[cyan]🎤 Retrying voice capture...[/cyan]"):
                                voice_future = listen_async(duration=retry_duration, samplerate=samplerate)
                                while not voice_future.done():
                                    time.sleep(0.05)
                                voice_result = voice_future.result()

                    if not voice_result.ok:
                        code = voice_result.code
                        if code == "no_mic":
                            console.print("[red]No microphone found. Connect/enable a mic and try again.[/red]")
                        elif code == "permission_denied":
                            console.print("[red]Microphone permission denied. Allow microphone access for Python/terminal.[/red]")
                        elif code == "silent_audio":
                            console.print("[yellow]No clear speech detected. Speak louder or closer to the mic.[/yellow]")
                        elif code == "model_load_failure":
                            console.print(f"[red]Voice model failed to load: {voice_result.message}[/red]")
                        elif code == "missing_dependency":
                            console.print("[red]Voice dependencies missing. Install: pip install faster-whisper sounddevice scipy numpy[/red]")
                        else:
                            console.print(f"[red]Voice error: {voice_result.message}[/red]")
                        console.print()
                        continue

                    user_input = voice_result.text
                    console.print(f"[green]📝 You said:[/green] {user_input}")
                    console.print(
                        f"[dim]⏱ capture={voice_result.capture_ms}ms, "
                        f"transcribe={voice_result.transcribe_ms}ms, total={voice_result.total_ms}ms[/dim]"
                    )
                    if not user_input:
                        console.print("[red]Could not hear anything. Try again.[/red]")
                        continue
                except ImportError:
                    console.print("[red]Voice module not ready. Install faster-whisper and sounddevice.[/red]")
                    continue

            # Safety check for destructive commands
            if is_dangerous(user_input):
                confirm = Prompt.ask(
                    "[bold red]⚠ This could be destructive. Are you sure?[/bold red] (yes/no)"
                )
                if confirm.lower() != "yes":
                    console.print("[yellow]Action cancelled.[/yellow]\n")
                    continue

                delete_target = resolve_delete_target(user_input)
                if delete_target:
                    with console.status("[cyan]🗑 Deleting locally...[/cyan]"):
                        delete_result = delete_file.invoke(delete_target)

                    console.print(Panel(
                        delete_result,
                        title="[bold cyan]🤖 Assistant[/bold cyan]",
                        border_style="cyan"
                    ))
                    console.print()
                    maybe_speak(delete_result)

                    chat_history.append(HumanMessage(user_input))
                    chat_history.append(AIMessage(delete_result))
                    if len(chat_history) > 20:
                        chat_history.pop(0)
                        chat_history.pop(0)
                    continue

            # Handle folder creation locally so it does not depend on Gemini.
            create_target = resolve_create_folder_target(user_input)
            if create_target:
                with console.status("[cyan]📁 Creating folder locally...[/cyan]"):
                    create_result = create_folder.invoke(create_target)

                console.print(Panel(
                    create_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(create_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(create_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle directory listing locally.
            list_target = resolve_list_directory_target(user_input)
            if list_target:
                with console.status("[cyan]📂 Listing directory locally...[/cyan]"):
                    list_result = list_directory.invoke(list_target)

                console.print(Panel(
                    list_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(list_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(list_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle file read locally.
            read_target = resolve_read_file_target(user_input)
            if read_target:
                with console.status("[cyan]📄 Reading file locally...[/cyan]"):
                    read_result = read_file.invoke(read_target)

                console.print(Panel(
                    read_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(read_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(read_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle file write locally.
            write_req = resolve_write_file_request(user_input)
            if write_req:
                path, content = write_req
                with console.status("[cyan]📝 Writing file locally...[/cyan]"):
                    write_result = write_file.invoke({"path": path, "content": content})

                console.print(Panel(
                    write_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(write_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(write_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle file search locally.
            search_req = resolve_search_files_request(user_input)
            if search_req:
                root, pattern = search_req
                with console.status("[cyan]🔎 Searching files locally...[/cyan]"):
                    search_result = search_files.invoke({"root_path": root, "pattern": pattern})

                console.print(Panel(
                    search_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(search_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(search_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle time/date locally.
            time_date = resolve_time_date_query(user_input)
            if time_date:
                console.print(Panel(
                    time_date,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(time_date)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(time_date))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle open path/file/folder locally.
            open_path_target = resolve_open_path_target(user_input)
            if open_path_target:
                with console.status("[cyan]📂 Opening path locally...[/cyan]"):
                    open_path_result = open_path_local(open_path_target)

                console.print(Panel(
                    open_path_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(open_path_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(open_path_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle app-launch commands locally so they do not depend on Gemini.
            open_app = resolve_open_app(user_input)
            if open_app:
                with console.status("[cyan]🚀 Opening app locally...[/cyan]"):
                    open_result = open_application.invoke(open_app)

                console.print(Panel(
                    open_result,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(open_result)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(open_result))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Handle system information locally so it does not consume Gemini quota.
            if is_system_info_request(user_input):
                local_info = resolve_system_info_query(user_input)
                if local_info:
                    console.print(Panel(
                        local_info,
                        title="[bold cyan]🤖 Assistant[/bold cyan]",
                        border_style="cyan"
                    ))
                    console.print()
                    maybe_speak(local_info)

                    chat_history.append(HumanMessage(user_input))
                    chat_history.append(AIMessage(local_info))
                    if len(chat_history) > 20:
                        chat_history.pop(0)
                        chat_history.pop(0)
                    continue

            if is_help_request(user_input):
                help_text = local_help_text()
                console.print(Panel(
                    help_text,
                    title="[bold cyan]🤖 Assistant[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                maybe_speak(help_text)

                chat_history.append(HumanMessage(user_input))
                chat_history.append(AIMessage(help_text))
                if len(chat_history) > 20:
                    chat_history.pop(0)
                    chat_history.pop(0)
                continue

            # Run the agent
            with console.status("[cyan]🤔 Thinking...[/cyan]"):
                # langgraph expects input as messages
                response = agent.invoke({
                    "messages": chat_history + [HumanMessage(user_input)]
                })

            # Extract and normalize the response (handle dict/list/message objects)
            def _extract_text(obj):
                # If object has .content, use it
                if hasattr(obj, 'content'):
                    obj = obj.content

                # If it's already a string, return as-is
                if isinstance(obj, str):
                    return obj

                # If it's a dict with a text field, use that
                if isinstance(obj, dict):
                    if 'text' in obj and isinstance(obj['text'], str):
                        return obj['text']
                    # Try common nested structures
                    if 'message' in obj and isinstance(obj['message'], str):
                        return obj['message']
                    return json.dumps(obj, ensure_ascii=False, indent=2)

                # If it's a list, pull text from elements
                if isinstance(obj, (list, tuple)):
                    parts = []
                    for el in obj:
                        if isinstance(el, str):
                            parts.append(el)
                        elif isinstance(el, dict) and 'text' in el:
                            parts.append(el['text'])
                        elif hasattr(el, 'content'):
                            parts.append(str(el.content))
                        else:
                            parts.append(json.dumps(el, ensure_ascii=False))
                    return "\n\n".join(parts)

                # Fallback to string conversion
                try:
                    return str(obj)
                except Exception:
                    return json.dumps(obj, ensure_ascii=False, default=str)

            if isinstance(response, dict) and "messages" in response:
                last_message = response["messages"][-1]
                answer = _extract_text(last_message)
            else:
                answer = _extract_text(response)

            console.print(Panel(
                answer,
                title="[bold cyan]🤖 Assistant[/bold cyan]",
                border_style="cyan"
            ))
            console.print()
            maybe_speak(answer)

            # Update conversation memory
            chat_history.append(HumanMessage(user_input))
            chat_history.append(AIMessage(answer))

            # Keep only last 10 exchanges to avoid context overflow
            if len(chat_history) > 20:
                chat_history.pop(0)
                chat_history.pop(0)

        except KeyboardInterrupt:
            console.print("\n[cyan]Interrupted. Goodbye! 👋[/cyan]")
            break
        except Exception as e:
            error_text = str(e)
            if "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
                console.print("[red]Gemini quota is temporarily exhausted.[/red]")
                console.print("[yellow]Try again after the retry delay, or ask a local question like RAM/IP/CPU/Disk so it bypasses Gemini.[/yellow]\n")
                continue

            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Try rephrasing your request.[/yellow]\n")


if __name__ == "__main__":
    main()
