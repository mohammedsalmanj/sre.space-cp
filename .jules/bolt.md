## 2026-02-05 - [LangGraph compilation caching]
**Learning:** Compiling a LangGraph workflow is an expensive operation (~21-25ms). Caching it at the module level avoids redundant setup on every request, providing a significant latency reduction for low-overhead agent loops.
**Action:** Always compile LangGraph workflows at the module level when they are stateless and reused across multiple requests.
