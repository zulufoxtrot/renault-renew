# Renault Scraper - Web API Setup

Your scraper is now a **Flask web API** with a beautiful, interactive dashboard! 🎉

## What's New

### Backend (API)
- **Flask API** (`app.py`) - RESTful endpoints for data management
- **Real-time scraping** - Background thread for non-blocking updates
- **Status polling** - Live progress updates while scraping

### Frontend (Dashboard)
- **Interactive dashboard** - View all vehicles in a searchable, sortable table
- **Refresh button** - Click to trigger a new scrape
- **Loader animation** - Full-screen overlay with spinning loader
- **Success confirmation** - Toast notification when scraping completes
- **Auto-refresh** - Data updates every 30 seconds
- **Stats cards** - Total vehicles, available now, new in 24h, price tracked

## Running the Application

### With Docker Compose (Recommended)

**Build and run locally:**
```bash
docker-compose -f docker-compose.local.yml up
```

**Or use pre-built image from GitHub Container Registry:**
```bash
docker-compose -f docker-compose.ghcr.yml up
```

Then open your browser:
```
http://localhost:5000
```

### Without Docker

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the Flask app:**
```bash
python app.py
```

Then open:
```
http://localhost:5000
```

## API Endpoints

### `GET /`
- Serves the main dashboard page

### `GET /api/vehicles`
- Returns all vehicles with price history
- Response includes stats and timestamp

### `POST /api/refresh`
- Triggers a new scraping session
- Runs in background thread
- Returns success/error status

### `GET /api/status`
- Returns current scraper status
- Fields: `is_running`, `progress`, `status_message`, `last_run`, `error`

### `GET /api/stats`
- Returns database statistics
- Fields: `total_vehicles`, `available_vehicles`, `new_vehicles_24h`, `vehicles_with_price_history`

## Features

### Dashboard Features
✅ **Sortable columns** - Click headers to sort  
✅ **Color-coded badges** - NEW (green), Price Down (green), Price Up (red)  
✅ **Photo thumbnails** - Vehicle images with hover zoom  
✅ **Price history** - See all price changes with up/down arrows  
✅ **Relative timestamps** - "2 days ago" format  
✅ **Responsive table** - Horizontal scroll on mobile  

### Refresh Button Features
✅ **Loader animation** - Spinning loader while scraping  
✅ **Full-screen overlay** - Blocks interaction during scrape  
✅ **Status updates** - "Initializing...", "Scraping vehicles...", etc.  
✅ **Success confirmation** - Green toast "✅ Scraping completed successfully!"  
✅ **Error handling** - Red toast with error message if scraping fails  
✅ **Auto-reload** - Vehicle table refreshes with new data  

### Data Persistence
✅ Database stored in `/app/renault_vehicles.db`  
✅ All vehicle data persists across container restarts  
✅ Price history tracked for each vehicle  
✅ New/available status computed from timestamps  

## Directory Structure

```
.
├── app.py                    # Flask API server
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker image configuration
├── docker-compose.local.yml # Local dev (build from source)
├── docker-compose.ghcr.yml  # Pre-built image from GHCR
├── templates/
│   └── index.html          # Frontend dashboard
├── scraper_table.py        # Web scraping logic
├── database.py             # SQLite database manager
├── report_generator.py     # HTML report generation
└── renault_vehicles.db     # SQLite database (created at runtime)
```

## Environment Variables

```bash
PORT=5000              # Flask server port (default: 5000)
PYTHONUNBUFFERED=1    # Real-time Python logging
```

## Database

The application uses SQLite with two tables:

### `vehicles` table
- url (primary key)
- title, price, original_price
- trim, charge_type, exterior_color, seat_type, packs, location
- photo_url, first_seen, last_seen
- is_available (boolean)

### `price_history` table
- id (auto-increment)
- vehicle_url, price, scraped_at

## Development

### Adding Features

To add more API endpoints, edit `app.py`:
```python
@app.route('/api/your-endpoint')
def your_endpoint():
    return jsonify({'data': 'value'})
```

To modify the frontend, edit `templates/index.html`.

### Debugging

Check logs while running:
```bash
docker-compose -f docker-compose.local.yml logs -f scraper
```

Or without Docker:
```bash
python app.py
```

## Troubleshooting

### Port 5000 already in use?
Change the port in docker-compose:
```yaml
ports:
  - "8000:5000"  # Access at http://localhost:8000
```

### Database locked error?
The database is accessed by Flask. Make sure only one instance is running.

### Scraper not finding vehicles?
- Check network connectivity
- Verify the Renault Renew website is accessible
- Check logs for HTTP errors

### Images not loading in dashboard?
- Vehicle images come from external URLs
- They may fail if the listing is removed or CDN is down
- Check browser console for CORS errors

## Performance Notes

- Initial scrape: 2-5 minutes (depends on network)
- Auto-refresh: Every 30 seconds (only loads data, no scraping)
- Manual refresh: Background thread, non-blocking
- Database: SQLite suitable for <10,000 vehicles
- Memory: ~50MB base + <10MB per scrape

## Next Steps

1. Open http://localhost:5000 in your browser
2. Click **"🔄 Refresh Data"** to start scraping
3. Watch the loader animation while scraping
4. See the success confirmation when done
5. Click column headers to sort
6. Explore the price history and vehicle details

Happy scraping! 🚗
