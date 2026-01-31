# Bolt's Performance Journal ⚡

## 2025-05-15 - Graph Compilation Bottleneck
**Learning:** In LangGraph, calling `workflow.compile()` is an expensive operation (measured at ~21ms for this project's graph). When this happens on every API request, it accounts for over 80% of the total execution time for simple paths.
**Action:** Always cache the compiled graph at the module level or use a singleton pattern to ensure it only compiles once.
**Result:** Improved `run_sre_loop` latency from 26.2ms to 2.8ms (~89% improvement).
