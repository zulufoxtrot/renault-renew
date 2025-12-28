# Renault Renew - Project Context

## 🎯 Project Overview

**Purpose**: Web scraper for Renault Megane E-Tech listings with price tracking and alerting
**Type**: Python Flask web application with background scraping
**Main Technologies**: Python, Flask, Selenium, SQLite

## 📁 Project Structure

```
renault-renew/
├── app.py                    # Flask API server with real-time scraping
├── scraper_table.py          # Main scraper (database version)
├── database.py               # SQLite database operations
├── report_generator.py       # HTML report generation with price tracking
├── migrate_db.py             # Database schema migrations
├── templates/                # Flask HTML templates
│   └── index.html           # Web UI for scraper
├── .github/workflows/        # GitHub Actions CI/CD
├── Dockerfile               # Docker container configuration
├── docker-compose.*.yml     # Docker compose configurations
└── requirements.txt         # Python dependencies
```

## 🏗️ Architecture

### Core Components

1. **Web Scraper** (`scraper_table.py`)
   - Selenium-based scraper using Chrome WebDriver
   - Scrolls through infinite-scroll pages
   - Extracts: title, price, location, specs, photos, GPS coordinates
   - Progress callback system for real-time updates

2. **Database Layer** (`database.py`)
   - SQLite with two tables: `vehicles` and `price_history`
   - Tracks price changes over time
   - Auto-creates schema if not exists
   - Supports filtering (new ads, price drops)

3. **Flask API** (`app.py`)
   - RESTful endpoints for vehicle data
   - Background scraping with thread safety
   - Real-time progress updates
   - CORS enabled for frontend integration

4. **Report Generator** (`report_generator.py`)
   - HTML reports with embedded images
   - Price history tracking
   - Highlights new listings and price drops

### Data Flow

```
Renault Website → Selenium Scraper → Database (SQLite)
                                          ↓
                           Flask API ← Web UI (templates/)
                                          ↓
                                   Report Generator → HTML Reports
```

## 🔑 Key Files to Understand

### app.py

- **Entry point**: Flask server
- **Global state**: `scraper_state` dict tracks scraping progress
- **Thread safety**: Uses `scraper_lock` for concurrent access
- **Database path**: Auto-detects `/app/data/` (Docker) or local path

### scraper_table.py

- **Class**: `RenaultScraper`
- **Key method**: `run()` - main scraping loop
- **Callback**: `progress_callback` for real-time updates
- **Output**: Saves to database and generates report

### database.py

- **Class**: `Database` and `Vehicle` dataclass
- **Schema**: Auto-creates on first run
- **Price tracking**: Separate `price_history` table
- **Methods**: CRUD operations + statistics

## 🎨 Coding Conventions

### Python Style

- **Format**: PEP 8 compliant
- **Docstrings**: Google-style docstrings for functions/classes
- **Type hints**: Use for function signatures where practical
- **Imports**: Grouped (standard lib, third-party, local)

### Error Handling

- Use try/except blocks with specific exceptions
- Log errors with emoji prefixes (❌ for errors, ✅ for success, 📊 for info)
- Return meaningful error messages in API responses

### Database Operations

- Always close database connections
- Use context managers where possible
- Handle schema migrations gracefully

## 🔧 Environment & Dependencies

### Required Environment Variables

- `PORT` - Flask server port (default: 5000)
- Database path auto-detected based on `/app/data/` existence

### Key Dependencies

- **selenium** - Web scraping
- **beautifulsoup4** - HTML parsing
- **Flask** - Web framework
- **flask-cors** - CORS support
- **Pillow** - Image processing

## 🐳 Deployment

### Docker

- **Base image**: `python:3.11-slim` with Chrome/ChromeDriver
- **Volumes**: `./output` and `./data` mounted for persistence
- **Networks**: Can be exposed on port 5000

### GitHub Actions

- Auto-builds and pushes to GitHub Container Registry
- Runs on push to main branch
- See `GITHUB_ACTIONS.md` for setup

## 🧪 Testing & Debugging

### Manual Testing

```bash
# Test scraper directly
python scraper_table.py

# Test Flask API
python app.py
# Then visit http://localhost:5000
```

### Debug Files

- `debug_fail_page.html` - Created when scraping fails
- Console logs with emoji indicators

## 🎯 Common Tasks

### Adding a new field to scrape

1. Update `Vehicle` dataclass in `database.py`
2. Add column to database schema
3. Create migration in `migrate_db.py`
4. Extract field in `scraper_table.py`
5. Display in `templates/index.html` and `report_generator.py`

### Changing scraping logic

- Edit `scraper_table.py` → `run()` method
- Test with debug logging enabled
- Update progress callbacks if needed

### Adding new API endpoint

1. Add route in `app.py`
2. Follow existing patterns (use try/except, return JSON)
3. Update frontend in `templates/index.html` if needed

## 📝 Notes for AI Agents

- **Database migrations**: Always create migration scripts, never delete old tables
- **Thread safety**: Use `scraper_lock` when modifying `scraper_state`
- **Selenium waits**: Use explicit waits, avoid hardcoded `time.sleep()`
- **Error recovery**: Scraper should save debug HTML on failures
- **Progress tracking**: Update progress callbacks for long-running operations
- **Docker paths**: Handle both local (`./`) and Docker (`/app/`) paths

## 🔗 Related Documentation

- `API_SETUP.md` - Flask API detailed documentation
- `README_DOCKER.md` - Docker deployment guide
- `GITHUB_ACTIONS.md` - CI/CD setup instructions
