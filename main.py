"""
Personal AI Assistant - Main Entry Point
Run this file to start the assistant: python main.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage, AIMessage
from agent import build_agent

console = Console()
chat_history = []

DANGEROUS_KEYWORDS = ["delete", "remove", "format", "rm -rf", "del ", "rmdir"]


def is_dangerous(text: str) -> bool:
    return any(word in text.lower() for word in DANGEROUS_KEYWORDS)


def main():
    console.print(Panel.fit(
        "🤖 [bold cyan]Personal AI Assistant[/bold cyan]\n"
        "[dim]Powered by Ollama (functionary-7b-v1) — 100% Local & Private[/dim]\n\n"
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

            # Run the agent
            with console.status("[cyan]🤔 Thinking...[/cyan]"):
                # langgraph expects input as messages
                response = agent.invoke({
                    "messages": chat_history + [HumanMessage(user_input)]
                })

            # Extract the response (langgraph returns in different format)
            if isinstance(response, dict) and "messages" in response:
                last_message = response["messages"][-1]
                answer = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                answer = str(response)
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
