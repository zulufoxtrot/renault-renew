---
globs: migrate_db.py
---

Never delete or modify existing migration functions. Always add new migrations to the end of the list. Handle 'duplicate
column' errors gracefully. Test migrations on a copy of the database first. Include descriptive migration names and
docstrings.