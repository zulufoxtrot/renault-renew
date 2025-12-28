---
globs: "**/*.py"
regex: Database\(|\.conn\.|cursor\(
---

Always close database connections after use. Use try/finally blocks or context managers. Never leave connections open in
long-running functions.