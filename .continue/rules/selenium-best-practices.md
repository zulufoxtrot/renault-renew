---
globs: scraper*.py
---

Use explicit waits (WebDriverWait) instead of time.sleep(). Handle NoSuchElementException for optional elements. Save
debug HTML on failures. Use progress callbacks for long operations. Clean up WebDriver with quit().