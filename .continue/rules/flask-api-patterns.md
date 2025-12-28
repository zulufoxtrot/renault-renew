---
globs: app.py
---

All Flask routes must: 1) Use try/except for error handling, 2) Return JSON with jsonify(), 3) Include 'success' boolean
in response, 4) Return appropriate HTTP status codes (200, 400, 500), 5) Close database connections in finally block.