## 2026-02-20 - [LangGraph Graph Caching]
**Learning:** Compiling a LangGraph `StateGraph` is a computationally expensive operation because it requires schema validation and internal state machine preparation. Re-compiling on every request (as seen in `run_sre_loop`) introduces unnecessary latency.
**Action:** Store the compiled graph in a module-level variable to ensure "Compile Once, Run Many" behavior. This is critical for high-frequency SRE loops.
