**Things Done Today**
- **Provider switch**: Replaced local Ollama usage with Google Gemini; added `GOOGLE_API_KEY` loading via `.env` and pinned `GEMINI_MODEL` to a supported model.
- **Config & requirements**: Updated `requirements.txt` and `config.py` for Gemini, dotenv, and voice settings.
- **Agent changes**: Replaced `ChatOllama` with `ChatGoogleGenerativeAI` in `agent.py`; agent now reads `config.GOOGLE_API_KEY`.
- **Local routing for resilience**: Implemented local handlers in `main.py` for system info, open application, create/list/delete folders, time/date, open path — these run locally to avoid Gemini quota outages.
- **Tools compatibility fix**: Updated tools in `tools/` to use `langchain_core.tools.tool` and adjusted test harness to call `StructuredTool.invoke()`.
- **Chrome launcher fix**: Fixed `tools/shell.py` to resolve Chrome on Windows when it's not on `PATH`.
- **Voice (Phase 4)**: Implemented `voice/stt.py` improvements — model caching, CPU int8, beam_size=1, VAD/silence detection, async listen paths, and clearer error codes.
- **Tests & scripts**: Added/updated `tests/test_tools_local.py` and `scripts/delete_test1.py`; validated create/list/delete and system-info flows locally.
- **Docs**: Added integration/setup notes (`GEMINI_INTEGRATION.md`, `GEMINI_SETUP.md`) and updated README and progress notes.

**Things To Be Done (Prioritized)**
- **Sanitize .env before commit**: Replace the real `GOOGLE_API_KEY` in `.env` with a placeholder and ensure `.env` is in `.gitignore` before pushing.
- **Replace `duckduckgo_search` with `ddgs`**: Update `tools/web_search.py` and `requirements.txt` to remove runtime warnings from `duckduckgo_search`.
- **Add agent decision logging**: Instrument the agent to log tool-call decisions (tool name, args, timestamps) for debugging and auditing (`main.py`, `agent.py`).
- **Add more local commands**: Implement create/read arbitrary files, recursive file search, and improved file-management tools in `tools/filesystem.py` and expose them to the agent.
- **Voice UX features**: Add mic device selection, push-to-talk toggle, and optional TTS responses (TTS integration and UI/CLI flags).
- **Expand automated tests**: Add unit and integration tests for local routing, voice pipeline, and tool invocation behavior (`tests/`).
- **Add no-Gemini / offline toggle**: Provide an environment or config toggle to run in fully-local fallback mode for contributors without API access.

**Files You Should Look At First**
- [config.py](config.py) — central settings and `.env` loading
- [agent.py](agent.py) — LangChain agent construction
- [main.py](main.py) — local router and main loop (where local handlers run)
- [voice/stt.py](voice/stt.py) — voice STT pipeline and model caching
- [tools/](tools/) — local tool implementations (filesystem, shell, system_info, web_search)
- [tests/test_tools_local.py](tests/test_tools_local.py) — local command tests and examples

**Quick run / test commands**
```bash
# create and activate venv (Windows)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# run basic syntax checks
py -m py_compile config.py agent.py main.py voice\stt.py tools\filesystem.py

# run local tests
python -m pytest tests/ -q
```

**Notes & Recommendations for the Contributor**
- DO NOT commit the real API key. Use `.env.example` to populate `GOOGLE_API_KEY` locally.
- If Gemini returns quota errors (`RESOURCE_EXHAUSTED`), use the local handlers in `main.py` for system operations. See the `resolve_...` handlers in `main.py` for examples.
- To remove runtime warnings from web search, switch to the `ddgs` package and update `tools/web_search.py` accordingly.

If you want, I can now: (1) sanitize `.env` in the repo, (2) open a PR-ready branch and commit this file, or (3) implement one of the prioritized tasks above. Tell me which next step to take.
