"""
Agent Core - LangChain agent with tool calling via Ollama
"""

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

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

SYSTEM_PROMPT = """You are a helpful Windows PC personal assistant running locally on the user's machine.

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
6. You are running 100% locally - no data leaves the machine

When a user says things like:
- "what's my IP" → use get_system_info
- "create a folder called X" → use create_folder
- "show files in Downloads" → use list_directory  
- "search for X" → use search_web
- "open notepad" → use open_application
- "run ipconfig" → use run_command
"""


def build_agent() -> AgentExecutor:
    """Build and return the LangChain agent with all tools."""
    llm = ChatOllama(
        model="llama3.1",
        temperature=0,          # Deterministic responses for system tasks
        num_predict=512,        # Max tokens per response
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=False,          # Set True to see agent reasoning steps
        max_iterations=6,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )
