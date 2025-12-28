---
globs: "**/*.py"
regex: cursor\.execute|conn\.execute
---

Always use parameterized queries with ? placeholders to prevent SQL injection. Never use f-strings or string
concatenation for SQL queries with user input.