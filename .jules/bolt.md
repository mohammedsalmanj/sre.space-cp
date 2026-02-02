## 2026-02-02 - [Caching LangGraph and ChromaDB Clients]
**Learning:** Compiling a LangGraph `StateGraph` on every request introduces a measurable ~20ms latency. Additionally, initializing a new `chromadb.HttpClient` and fetching a collection for every request adds ~175ms of overhead due to connection setup and metadata retrieval.
**Action:** Always cache compiled graphs and database clients at the module level (singleton pattern) to ensure minimal request latency in high-throughput SRE loops. Use relative imports within agent packages to share these cached resources efficiently.
