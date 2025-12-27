#!/usr/bin/env python3
"""
HTML Report Generator for Renault Scraper
Creates human-friendly HTML reports with vehicle photos and highlighting
"""

from datetime import datetime, timedelta
from typing import List
from database import VehicleRecord, Database
import os


class HTMLReportGenerator:
    def __init__(self, db: Database):
        self.db = db

    def _get_relative_time(self, date_str: str) -> str:
        """Convert datetime to relative time (e.g., '2 days ago')"""
        date = datetime.fromisoformat(date_str)
        now = datetime.now()
        diff = now - date

        seconds = diff.total_seconds()

        if seconds < 3600:  # Less than 1 hour
            minutes = int(seconds / 60)
            return f"{minutes} min ago" if minutes != 1 else "1 min ago"
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds / 3600)
            return f"{hours}h ago" if hours != 1 else "1h ago"
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds / 86400)
            return f"{days} days ago" if days != 1 else "1 day ago"
        elif seconds < 2592000:  # Less than 30 days
            weeks = int(seconds / 604800)
            return f"{weeks} weeks ago" if weeks != 1 else "1 week ago"
        else:
            months = int(seconds / 2592000)
            return f"{months} months ago" if months != 1 else "1 month ago"

    def generate_report(self, output_file: str = "vehicle_report.html"):
        """Generate HTML report with all vehicles"""
        vehicles = self.db.get_all_vehicles()
        stats = self.db.get_statistics()
        
        html = self._generate_html(vehicles, stats)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📄 Report generated: {output_file}")
        return output_file

    def _generate_html(self, vehicles: List[VehicleRecord], stats: dict) -> str:
        """Generate the complete HTML structure"""
        
        # Generate timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate table rows
        table_rows = ""
        for vehicle in vehicles:
            if vehicle.is_new:
                row_style = 'style="background-color: #d4edda;"'  # Light green for new
                new_badge = ' <span class="badge badge-new">NEW</span>'
            else:
                row_style = ''
                new_badge = ''
            
            # Price change indicator
            price_change = ""
            if vehicle.original_price and vehicle.price != vehicle.original_price:
                diff = vehicle.price - vehicle.original_price
                if diff < 0:
                    price_change = f' <span class="badge badge-price-down">-{abs(diff)}€</span>'
                else:
                    price_change = f' <span class="badge badge-price-up">+{diff}€</span>'
            
                        # Photo handling with link
            photo_html = ""
            if vehicle.photo_url:
                photo_html = f'''
                <a href="{vehicle.url}" target="_blank" class="photo-link">
                    <img src="{vehicle.photo_url}" 
                         alt="{vehicle.title}" 
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22150%22 height=%22100%22%3E%3Crect fill=%22%23ddd%22 width=%22150%22 height=%22100%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3ENo Image%3C/text%3E%3C/svg%3E';">
                </a>
                '''
            else:
                photo_html = f'''
                <a href="{vehicle.url}" target="_blank" class="photo-link">
                    <div class="no-photo">No Photo</div>
                </a>
                '''
            
            # Format dates with relative time
            first_seen = datetime.fromisoformat(vehicle.first_seen).strftime("%Y-%m-%d %H:%M")
            last_seen = datetime.fromisoformat(vehicle.last_seen).strftime("%Y-%m-%d %H:%M")
            first_seen_relative = self._get_relative_time(vehicle.first_seen)
            last_seen_relative = self._get_relative_time(vehicle.last_seen)

            # Get price history
            price_history = self.db.get_price_history(vehicle.url)
            price_history_html = self._format_price_history(price_history)
            
            table_rows += f"""
            <tr {row_style}>
                <td class="photo-cell">{photo_html}{new_badge}</td>
                <td class="price-cell" data-sort="{vehicle.price}"><strong>{vehicle.price:,}€</strong>{price_change}</td>
                <td data-sort="{vehicle.original_price}">{vehicle.original_price:,}€</td>
                <td>{vehicle.trim}</td>
                <td>{vehicle.charge_type}</td>
                <td><span class="color-badge" style="background-color: {self._get_color_hex(vehicle.exterior_color)};">{vehicle.exterior_color}</span></td>
                <td>{vehicle.seat_type}</td>
                <td class="packs-cell">{vehicle.packs}</td>
                <td>{vehicle.location}</td>
                <td data-sort="{vehicle.first_seen}"><span class="relative-date">{first_seen_relative}</span><br><span class="absolute-date">{first_seen}</span></td>
                <td data-sort="{vehicle.last_seen}"><span class="relative-date">{last_seen_relative}</span><br><span class="absolute-date">{last_seen}</span></td>
                <td>{price_history_html}</td>
            </tr>
            """
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Renault Mégane E-Tech - Vehicle Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .stat-box {{
            text-align: center;
            padding: 15px;
        }}
        
        .stat-box .number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-box .label {{
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }}
        
        .table-container {{
            overflow-x: auto;
            padding: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        th {{
            background: #2c3e50;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            cursor: pointer;
            user-select: none;
        }}
        
        th:hover {{
            background: #34495e;
        }}
        
        th.sort-asc::after {{
            content: " ▲";
            font-size: 0.8em;
        }}
        
        th.sort-desc::after {{
            content: " ▼";
            font-size: 0.8em;
        }}
        
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background-color: #f8f9fa !important;
        }}
        
        .photo-cell {{
            width: 150px;
            text-align: center;
        }}
        
        .photo-cell img {{
            max-width: 150px;
            max-height: 100px;
            object-fit: cover;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .photo-link {{
            display: inline-block;
            position: relative;
        }}
        
        .photo-link:hover img {{
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .photo-link:hover .no-photo {{
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .no-photo {{
            width: 150px;
            height: 100px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 0.85em;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .relative-date {{
            font-weight: 600;
            color: #667eea;
        }}
        
        .absolute-date {{
            font-size: 0.8em;
            color: #6c757d;
        }}
        
        .price-cell {{
            font-size: 1.1em;
        }}
        
        .packs-cell {{
            max-width: 250px;
            font-size: 0.85em;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.75em;
            font-weight: bold;
            margin-left: 5px;
        }}
        
        .badge-new {{
            background: #28a745;
            color: white;
        }}
        
        .badge-price-down {{
            background: #28a745;
            color: white;
        }}
        
        .badge-price-up {{
            background: #dc3545;
            color: white;
        }}
        
        .color-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            color: white;
            font-weight: 500;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.3);
        }}
        
        .price-history {{
            font-size: 0.8em;
            color: #6c757d;
        }}
        
        .price-history-item {{
            white-space: nowrap;
        }}
        
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Renault Mégane E-Tech</h1>
            <div class="subtitle">Iconic | Optimum Charge | €19k-25k</div>
            <div class="subtitle">Generated: {now}</div>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="number">{stats['total_vehicles']}</div>
                <div class="label">Total Vehicles</div>
            </div>
            <div class="stat-box">
                <div class="number">{stats['available_vehicles']}</div>
                <div class="label">Available Now</div>
            </div>
            <div class="stat-box">
                <div class="number">{stats['new_vehicles_24h']}</div>
                <div class="label">New (24h)</div>
            </div>
            <div class="stat-box">
                <div class="number">{stats['vehicles_with_price_history']}</div>
                <div class="label">Price Tracked</div>
            </div>
        </div>
        
        <div class="table-container">
            <table id="vehicleTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Photo</th>
                        <th onclick="sortTable(1)">Current Price</th>
                        <th onclick="sortTable(2)">Original Price</th>
                        <th onclick="sortTable(3)">Trim</th>
                        <th onclick="sortTable(4)">Charge</th>
                        <th onclick="sortTable(5)">Color</th>
                        <th onclick="sortTable(6)">Seats</th>
                        <th onclick="sortTable(7)">Packs</th>
                        <th onclick="sortTable(8)">Location</th>
                        <th onclick="sortTable(9)">First Seen</th>
                        <th onclick="sortTable(10)">Last Seen</th>
                        <th onclick="sortTable(11)">Price History</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Generated by Renault Scraper v15 | Database: {self.db.db_path}<br>
            Click column headers to sort
        </div>
    </div>
    
    <script>
        let currentSort = {{ column: -1, ascending: true }};
        
        function sortTable(columnIndex) {{
            const table = document.getElementById('vehicleTable');
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);
            const headers = table.tHead.rows[0].cells;
            
            // Toggle sort direction
            if (currentSort.column === columnIndex) {{
                currentSort.ascending = !currentSort.ascending;
            }} else {{
                currentSort.column = columnIndex;
                currentSort.ascending = true;
            }}
            
            // Remove sort indicators from all headers
            for (let header of headers) {{
                header.classList.remove('sort-asc', 'sort-desc');
            }}
            
            // Add sort indicator to current header
            headers[columnIndex].classList.add(currentSort.ascending ? 'sort-asc' : 'sort-desc');
            
            // Sort rows
            rows.sort((a, b) => {{
                let aCell = a.cells[columnIndex];
                let bCell = b.cells[columnIndex];
                
                // Use data-sort attribute if available
                let aValue = aCell.getAttribute('data-sort') || aCell.textContent.trim();
                let bValue = bCell.getAttribute('data-sort') || bCell.textContent.trim();
                
                // Try date comparison (ISO format detection)
                if (aValue.match(/^\d{{4}}-\d{{2}}-\d{{2}}T/) && bValue.match(/^\d{{4}}-\d{{2}}-\d{{2}}T/)) {{
                    let aDate = new Date(aValue);
                    let bDate = new Date(bValue);
                    return currentSort.ascending ? aDate - bDate : bDate - aDate;
                }}
                
                // Try numeric comparison
                let aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
                let bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return currentSort.ascending ? aNum - bNum : bNum - aNum;
                }}
                
                // Fall back to string comparison
                return currentSort.ascending 
                    ? aValue.localeCompare(bValue)
                    : bValue.localeCompare(aValue);
            }});
            
            // Reorder rows in the table
            rows.forEach(row => tbody.appendChild(row));
        }}
        
        // Sort by "Last Seen" descending by default on page load
        window.addEventListener('DOMContentLoaded', () => {{
            // Set initial sort state to descending for Last Seen
            currentSort.column = 10;
            currentSort.ascending = false;
            sortTable(10); // Last Seen column
        }});
    </script>
</body>
</html>"""
        
        return html

    def _format_price_history(self, history: List[dict]) -> str:
        """Format price history for display"""
        if not history or len(history) <= 1:
            return "—"
        
        html_items = []
        for i, item in enumerate(history):
            date = datetime.fromisoformat(item['date']).strftime("%m/%d")
            price = f"{item['price']:,}€"
            
            # Show arrow if not first item
            if i > 0:
                prev_price = history[i-1]['price']
                if item['price'] < prev_price:
                    arrow = "↓"
                elif item['price'] > prev_price:
                    arrow = "↑"
                else:
                    arrow = "="
                html_items.append(f'<div class="price-history-item">{date}: {price} {arrow}</div>')
            else:
                html_items.append(f'<div class="price-history-item">{date}: {price}</div>')
        
        return '<div class="price-history">' + ''.join(html_items) + '</div>'

    def _get_color_hex(self, color_name: str) -> str:
        """Convert color name to hex code for display"""
        color_map = {
            'blanc': '#FFFFFF',
            'blanc nacré': '#F5F5F5',
            'noir': '#1a1a1a',
            'noir étoilé': '#0a0a0a',
            'gris': '#808080',
            'gris schiste': '#6B7280',
            'gris rafale': '#5a5a5a',
            'bleu': '#0066CC',
            'bleu iron': '#1e3a5f',
            'rouge': '#CC0000',
            'rouge flamme': '#DC143C',
        }
        
        color_lower = color_name.lower()
        
        # Try exact match
        if color_lower in color_map:
            return color_map[color_lower]
        
        # Try partial match
        for key, value in color_map.items():
            if key in color_lower:
                return value
        
        # Default
        return '#6c757d'
