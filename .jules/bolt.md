## 2026-02-03 - [LangGraph & ChromaDB Initialization Overhead]
**Learning:** LangGraph `.compile()` has a significant overhead (~22ms). Additionally, instantiating `chromadb.HttpClient` is surprisingly expensive (~62ms) even when the connection fails.
**Action:** Always cache compiled graphs and reuse external service clients at the module level or via a singleton pattern to avoid adding 80ms+ of latency to every request.
