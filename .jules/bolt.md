## 2026-02-04 - [Caching Expensive Initializations]
**Learning:** In a multi-agent system powered by LangGraph and ChromaDB, repeated initialization of the graph and the database client can add significant overhead (~22ms for LangGraph compilation and ~62ms for ChromaDB HttpClient instantiation). These "cold path" initializations can be easily optimized by module-level caching.
**Action:** Always cache the compiled LangGraph workflow and reuse database clients (like ChromaDB HttpClient) at the module level to minimize latency in the main execution loop.
