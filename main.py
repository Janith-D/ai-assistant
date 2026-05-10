"""
Personal AI Assistant - Main Entry Point
Run this file to start the assistant: python main.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent
from tools.filesystem import delete_file
import json
import os
import re

console = Console()
chat_history = []

DANGEROUS_KEYWORDS = ["delete", "remove", "format", "rm -rf", "del ", "rmdir"]


def is_dangerous(text: str) -> bool:
    return any(word in text.lower() for word in DANGEROUS_KEYWORDS)


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

    while True:
        try:
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("[cyan]Goodbye! 👋[/cyan]")
                break

            # Voice mode toggle
            if user_input.lower() == "voice":
                try:
                    from voice.stt import listen
                    user_input = listen()
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

                    chat_history.append(HumanMessage(user_input))
                    chat_history.append(AIMessage(delete_result))
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
            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Try rephrasing your request.[/yellow]\n")


if __name__ == "__main__":
    main()
