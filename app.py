#!/usr/bin/env python3
"""
Flask API for Renault Scraper
Provides web interface with real-time scraping
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from threading import Thread, Lock
import time
from datetime import datetime
from typing import Optional
import os

from database import Database
from scraper_table import RenaultScraper

app = Flask(__name__)
CORS(app)

# Database path configuration
DB_PATH = '/app/data/renault_vehicles.db' if os.path.exists('/app/data') else 'renault_vehicles.db'

# Global state
scraper_state = {
    'is_running': False,
    'progress': 0,
    'status_message': 'Ready',
    'last_run': None,
    'error': None,
    'pages_processed': 0,
    'ads_processed': 0,
    'ads_added': 0
}
scraper_lock = Lock()


def progress_callback(progress_data):
    """Callback to update progress from scraper"""
    global scraper_state
    scraper_state['pages_processed'] = progress_data.get('pages_processed', 0)
    scraper_state['ads_processed'] = progress_data.get('ads_processed', 0)
    scraper_state['ads_added'] = progress_data.get('ads_added', 0)

    # Update status message with progress details
    pages = progress_data.get('pages_processed', 0)
    ads = progress_data.get('ads_processed', 0)
    added = progress_data.get('ads_added', 0)
    scraper_state['status_message'] = f'Scraping... Page {pages} | Ads: {ads} | New: {added}'


def run_scraper_background():
    """Run the scraper in a background thread"""
    global scraper_state
    
    with scraper_lock:
        if scraper_state['is_running']:
            return
        scraper_state['is_running'] = True
        scraper_state['progress'] = 0
        scraper_state['status_message'] = 'Starting scraper...'
        scraper_state['error'] = None
        scraper_state['pages_processed'] = 0
        scraper_state['ads_processed'] = 0
        scraper_state['ads_added'] = 0

    try:
        # Update status
        scraper_state['status_message'] = 'Initializing...'
        scraper = RenaultScraper(use_database=True, db_path=DB_PATH, progress_callback=progress_callback)

        scraper_state['status_message'] = 'Scraping vehicle listings...'
        scraper_state['progress'] = 10
        
        # Run the scraper
        scraper.run()
        
        scraper_state['progress'] = 100
        scraper_state[
            'status_message'] = f'Completed! Pages: {scraper_state["pages_processed"]} | Ads: {scraper_state["ads_processed"]} | New: {scraper_state["ads_added"]}'
        scraper_state['last_run'] = datetime.now().isoformat()
        
    except Exception as e:
        scraper_state['error'] = str(e)
        scraper_state['status_message'] = f'Error: {str(e)}'
        print(f"❌ Scraper error: {e}")
    
    finally:
        time.sleep(2)  # Keep success message visible
        scraper_state['is_running'] = False


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/vehicles')
def get_vehicles():
    """Get all vehicles from database"""
    try:
        db = Database(DB_PATH)
        vehicles = db.get_all_vehicles()
        stats = db.get_statistics()
        db.close()
        
        # Convert to dict format
        vehicles_data = []
        for v in vehicles:
            vehicle_dict = {
                'url': v.url,
                'title': v.title,
                'price': v.price,
                'original_price': v.original_price,
                'trim': v.trim,
                'charge_type': v.charge_type,
                'exterior_color': v.exterior_color,
                'seat_type': v.seat_type,
                'packs': v.packs,
                'location': v.location,
                'photo_url': v.photo_url,
                'latitude': v.latitude,
                'longitude': v.longitude,
                'first_seen': v.first_seen,
                'last_seen': v.last_seen,
                'is_new': v.is_new
            }
            
            # Get price history
            db2 = Database(DB_PATH)
            price_history = db2.get_price_history(v.url)
            db2.close()
            vehicle_dict['price_history'] = price_history
            
            vehicles_data.append(vehicle_dict)
        
        return jsonify({
            'success': True,
            'vehicles': vehicles_data,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Trigger a new scrape"""
    global scraper_state
    
    with scraper_lock:
        if scraper_state['is_running']:
            return jsonify({
                'success': False,
                'message': 'Scraper is already running'
            }), 400
    
    # Start scraper in background thread
    thread = Thread(target=run_scraper_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Scraping started'
    })


@app.route('/api/status')
def get_status():
    """Get current scraper status"""
    return jsonify({
        'success': True,
        'is_running': scraper_state['is_running'],
        'progress': scraper_state['progress'],
        'status_message': scraper_state['status_message'],
        'last_run': scraper_state['last_run'],
        'error': scraper_state['error'],
        'pages_processed': scraper_state['pages_processed'],
        'ads_processed': scraper_state['ads_processed'],
        'ads_added': scraper_state['ads_added']
    })


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        db = Database(DB_PATH)
        stats = db.get_statistics()
        db.close()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Initialize database on startup
    print(f"📁 Using database path: {DB_PATH}")
    db = Database(DB_PATH)
    db.close()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
