"""
Agent Core - LangChain agent with tool calling via Ollama (Local, 100% Private)
"""

from langchain_ollama import ChatOllama
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
    """Build and return the LangChain agent with all tools (Ollama - functionary-7b-v1)."""
    
    # Initialize Ollama model
    llm = ChatOllama(
        model=config.OLLAMA_MODEL,  # Reads from config.py
        temperature=config.OLLAMA_TEMPERATURE,
        num_predict=config.OLLAMA_MAX_TOKENS,
    )
    
    # Bind the system prompt to the model
    llm_with_system = llm.bind(system=SYSTEM_PROMPT)

    # Create the agent using langgraph's create_react_agent
    # This returns a runnable that handles the ReAct loop internally
    agent_executor = create_react_agent(llm_with_system, TOOLS)

    return agent_executor
