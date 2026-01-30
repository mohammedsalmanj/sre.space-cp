## 2024-05-20 - The Importance of Atomic Commits

**Learning:** A pull request should be focused on a single, atomic change. I received blocking feedback on a performance optimization because I bundled it with two unrelated and harmful changes: committing a `server.log` file and adding an out-of-scope `openai` dependency to `requirements.txt`. This violated the "single concern" principle of good source control.

**Action:** Before every commit, I must review all changed files and ensure they are *directly* related to the specific task. Unrelated changes, especially dependency modifications or the addition of generated artifacts, must be reverted and addressed in a separate, dedicated PR. Log files and other build artifacts should always be added to `.gitignore`.
