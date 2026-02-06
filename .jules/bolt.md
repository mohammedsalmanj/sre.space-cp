## 2026-02-06 - [Resource Initialization Caching]
**Learning:** Re-initializing heavy clients (like ChromaDB HttpClient) and re-compiling workflows (like LangGraph) on every request introduces significant overhead (~60-80ms total) that accumulates in multi-agent loops.
**Action:** Always cache expensive resource instances at the module level and share them across modules using centralized getters or relative imports to ensure singletons within the application lifecycle.
