"""
Agent Core - LangChain agent with tool calling via Google Gemini
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from typing import Any
import config

from tools.filesystem import create_folder, list_directory, read_file, delete_file
from tools.shell import run_command, open_application
from tools.system_info import get_system_info
from tools.web_search import search_web

TOOLS = [
    run_command,
    open_application,
    create_folder,
    list_directory,
    read_file,
    delete_file,
    get_system_info,
    search_web,
]

SYSTEM_PROMPT = """You are a helpful Windows PC personal assistant.

You have access to powerful tools to help the user:
- Run shell commands and scripts
- Create, read, list, and delete files/folders
- Get system information (IP, RAM, CPU, disk)
- Search the web using DuckDuckGo
- Open applications

RULES:
1. Always be concise and clear in your responses
2. Before deleting anything, warn the user
3. When running commands, show the output clearly
4. If unsure about a file path, ask the user to confirm
5. For web searches, summarize the top results clearly
6. Think step-by-step when executing complex tasks

When a user says things like:
- "what's my IP" → use get_system_info
- "create a folder called X" → use create_folder
- "show files in Downloads" → use list_directory  
- "search for X" → use search_web
- "open notepad" → use open_application
- "run ipconfig" → use run_command
"""


def build_agent() -> Any:
    """Build and return the LangChain agent with all tools using Gemini."""

    if not config.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Add it to .env before starting the assistant."
        )

    llm = ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        temperature=config.GEMINI_TEMPERATURE,
        max_output_tokens=config.GEMINI_MAX_TOKENS,
        google_api_key=config.GOOGLE_API_KEY,
    )

    agent_executor = create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)

    return agent_executor
