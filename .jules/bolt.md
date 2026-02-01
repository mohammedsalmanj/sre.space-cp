# Bolt's Journal - Critical Learnings

## 2026-02-01 - [Graph Compilation and ChromaDB Client Caching]
**Learning:** Found that compiling a LangGraph workflow takes ~21ms, which is significant when done on every request in a high-latency agentic loop. Similarly, instantiating `chromadb.HttpClient` takes ~44ms as it attempts to connect and verify identity upon creation.
**Action:** Always move graph compilation to the module level (or a singleton) and cache ChromaDB clients/collections to avoid redundant network-bound initialization.
