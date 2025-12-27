
# Running Renault Scraper with Docker Compose

## Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## Using Pre-built Image from GitHub Container Registry

You can use the pre-built image instead of building locally:

```bash
# Pull and run the latest image
docker-compose -f docker-compose.ghcr.yml up
```

**Note:** Edit `docker-compose.ghcr.yml` first and replace `YOUR_USERNAME/YOUR_REPO` with the actual GitHub repository path.

See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) for complete setup instructions.

## Quick Start (Build Locally)

### 1. Build the Docker image
```bash
docker-compose build
```

### 2. Run the scraper
```bash
docker-compose up
```

To run in detached mode (background):
```bash
docker-compose up -d
```

### 3. View logs
```bash
docker-compose logs -f scraper
```

### 4. Stop the scraper
```bash
docker-compose down
```

## Output Files

All output files will be saved to the `./output` directory on your host machine:
- `renault_megane_v15.csv` - CSV file with vehicle data
- `vehicle_report.html` - HTML report with price tracking
- `debug_fail_page.html` - Debug file (if scraping fails)

Database files will be saved to the `./data` directory:
- `vehicles.db` - SQLite database with price history

## Running on a Schedule

### Option 1: Manual runs
Run the scraper manually whenever you want:
```bash
docker-compose run --rm scraper
```

### Option 2: Continuous loop (run every hour)
Edit `docker-compose.yml` and uncomment the last line to run every hour:
```yaml
command: sh -c "while true; do python scraper_table.py; sleep 3600; done"
```

Then:
```bash
docker-compose up -d
```

### Option 3: Use cron (Linux/Mac)
Add to your crontab:
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/scraper && docker-compose run --rm scraper
```

### Option 4: Use Windows Task Scheduler
Create a task that runs:
```cmd
docker-compose -f C:\path\to\scraper\docker-compose.yml run --rm scraper
```

## Customization

### Change output directory
Edit the volumes in `docker-compose.yml`:
```yaml
volumes:
  - /custom/path:/app/output
```

### Use different scraper version
Edit the CMD in `Dockerfile` to use `scraper_csv.py` instead:
```dockerfile
CMD ["python", "scraper_csv.py"]
```

## Troubleshooting

### Container exits immediately
Check logs:
```bash
docker-compose logs scraper
```

### Permission errors
Create the output directories first:
```bash
mkdir -p output data
chmod 777 output data  # Linux/Mac only
```

### Rebuild after code changes
```bash
docker-compose build --no-cache
docker-compose up
```

### Access container shell
```bash
docker-compose run --rm scraper /bin/bash
```

## Clean Up

Remove containers and images:
```bash
docker-compose down
docker rmi renault-scraper:latest
```

Remove all output files:
```bash
rm -rf output/* data/*
```
