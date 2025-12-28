# Task Templates for AI Agents

This file contains common task patterns and workflows for editing this project.

---

## 🆕 Adding a New Scraped Field

**When to use**: User wants to extract additional data from vehicle listings

**Steps**:

1. **Update data model** (`database.py`):
   - Add field to `Vehicle` dataclass
   - Add field type hint and default value

2. **Update database schema** (`database.py`):
   - Add column to `CREATE TABLE` statement in `_create_tables()`
   - Document the new field

3. **Create migration** (`migrate_db.py`):
   - Add new migration function (e.g., `add_column_X()`)
   - Use `ALTER TABLE` to add column with default value
   - Add migration to `run_migrations()` list

4. **Extract in scraper** (`scraper_table.py`):
   - Find the CSS selector or XPath for the new field
   - Extract in `run()` method where other fields are extracted
   - Handle missing/optional fields gracefully
   - Update progress messages if needed

5. **Display in reports** (`report_generator.py`):
   - Add field to HTML template
   - Update vehicle card layout if needed

6. **Update API response** (`app.py`):
   - Add field to `vehicle_dict` in `/api/vehicles` endpoint

7. **Update frontend** (`templates/index.html`):
   - Display new field in vehicle cards
   - Add filtering/sorting if applicable

**Example**:

```python
# database.py - Add field
@dataclass
class Vehicle:
   # ... existing fields ...
   warranty_months: Optional[int] = None  # NEW FIELD


# database.py - Add column
CREATE
TABLE
vehicles(
   -- ...
existing
columns...
warranty_months
INTEGER - - NEW
COLUMN
)

# migrate_db.py - Create migration
def add_warranty_months_column(conn):
   cursor = conn.cursor()
   cursor.execute('ALTER TABLE vehicles ADD COLUMN warranty_months INTEGER')
   conn.commit()


# scraper_table.py - Extract field
warranty_elem = ad.find_element(By.CSS_SELECTOR, '.warranty-info')
warranty_months = int(warranty_elem.text.split()[0]) if warranty_elem else None
```

---

## 🔧 Modifying Scraping Logic

**When to use**: Website structure changed or scraping is failing

**Steps**:

1. **Identify the issue**:
   - Check `debug_fail_page.html` if it exists
   - Review console error messages
   - Inspect the target website manually

2. **Update selectors** (`scraper_table.py`):
   - Find the outdated CSS selectors or XPath expressions
   - Test new selectors in browser DevTools first
   - Update in `run()` method

3. **Adjust wait conditions**:
   - Update explicit waits if timing changed
   - Use `WebDriverWait` instead of `time.sleep()`
   - Wait for specific elements, not arbitrary delays

4. **Test changes**:
   ```bash
   python scraper_table.py
   ```
   - Verify debug output
   - Check database entries
   - Review generated report

5. **Update error handling**:
   - Add try/except for new failure modes
   - Save debug HTML on failures
   - Log meaningful error messages

**Common selector patterns**:

```python
# Wait for element
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
   EC.presence_of_element_located((By.CSS_SELECTOR, '.selector'))
)

# Handle optional elements
try:
   optional_elem = ad.find_element(By.CSS_SELECTOR, '.optional')
   value = optional_elem.text
except NoSuchElementException:
   value = None
```

---

## 🎨 Adding New API Endpoint

**When to use**: Need new functionality in the Flask API

**Steps**:

1. **Define route** (`app.py`):
   - Add `@app.route()` decorator
   - Choose appropriate HTTP method (GET, POST, etc.)
   - Use consistent URL pattern (`/api/...`)

2. **Implement handler**:
   - Use try/except for error handling
   - Return JSON with `jsonify()`
   - Include `success` boolean in response
   - Return appropriate HTTP status codes

3. **Access database if needed**:
   - Create `Database` instance
   - Perform operations
   - Always close connection (use try/finally)

4. **Update frontend** (`templates/index.html`):
   - Add JavaScript fetch call
   - Update UI based on response
   - Handle loading states and errors

**Template**:

```python
@app.route('/api/your-endpoint', methods=['POST'])
def your_endpoint():
   """Description of what this endpoint does"""
   try:
      # Get request data
      data = request.get_json()

      # Validate input
      if not data or 'required_field' not in data:
         return jsonify({
            'success': False,
            'error': 'Missing required field'
         }), 400

      # Perform operation
      db = Database(DB_PATH)
      result = db.some_operation(data['required_field'])
      db.close()

      # Return success response
      return jsonify({
         'success': True,
         'data': result
      })

   except Exception as e:
      return jsonify({
         'success': False,
         'error': str(e)
      }), 500
```

---

## 📊 Adding Database Query/Filter

**When to use**: Need new way to query or filter vehicle data

**Steps**:

1. **Add method to Database class** (`database.py`):
   - Follow naming convention: `get_*` or `filter_*`
   - Use parameterized queries (prevent SQL injection)
   - Return appropriate type (list, dict, etc.)
   - Document with docstring

2. **Create API endpoint** (`app.py`):
   - Expose the new query via REST API
   - Add appropriate parameters
   - Return formatted JSON

3. **Update frontend** (optional):
   - Add UI controls for the filter
   - Display filtered results

**Example**:

```python
# database.py
def get_vehicles_by_location(self, location: str) -> List[Vehicle]:
   """Get all vehicles in a specific location"""
   cursor = self.conn.cursor()
   cursor.execute('''
        SELECT * FROM vehicles 
        WHERE location LIKE ? AND last_seen = (
            SELECT MAX(last_seen) FROM vehicles
        )
    ''', (f'%{location}%',))
   return [self._row_to_vehicle(row) for row in cursor.fetchall()]


# app.py
@app.route('/api/vehicles/by-location')
def get_vehicles_by_location():
   try:
      location = request.args.get('location', '')
      db = Database(DB_PATH)
      vehicles = db.get_vehicles_by_location(location)
      db.close()

      return jsonify({
         'success': True,
         'vehicles': [v.__dict__ for v in vehicles]
      })
   except Exception as e:
      return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 🐛 Debugging Scraper Issues

**When to use**: Scraper is failing or returning incorrect data

**Debugging checklist**:

1. ✅ Check `debug_fail_page.html` for actual page structure
2. ✅ Review console logs for error messages
3. ✅ Verify website hasn't changed structure
4. ✅ Test selectors in browser DevTools
5. ✅ Check if infinite scroll is working
6. ✅ Verify ChromeDriver version compatibility
7. ✅ Test with `headless=False` to watch scraping

**Debug mode template**:

```python
# Add to scraper_table.py for debugging
options.add_argument('--headless=no')  # Show browser
options.add_argument('--start-maximized')  # Full window

# Add breakpoints
import pdb;

pdb.set_trace()

# Save intermediate HTML
with open('debug_intermediate.html', 'w') as f:
   f.write(driver.page_source)
```

---

## 🔄 Database Migration

**When to use**: Schema needs to change (new column, alter type, etc.)

**Steps**:

1. **Create migration function** (`migrate_db.py`):
   - Name it descriptively (e.g., `add_column_X`, `rename_table_Y`)
   - Use ALTER TABLE or other DDL statements
   - Include error handling
   - Test with sample database first

2. **Add to migration list**:
   - Add function to `migrations` list in `run_migrations()`
   - Ensure order is correct (chronological)

3. **Test migration**:
   ```bash
   python migrate_db.py
   ```

4. **Update schema in database.py**:
   - Update `_create_tables()` to include new schema
   - This ensures fresh installations have correct schema

**Migration template**:

```python
def migration_name(conn):
   """Description of what this migration does"""
   cursor = conn.cursor()
   try:
      cursor.execute('ALTER TABLE vehicles ADD COLUMN new_field TYPE')
      conn.commit()
      print('✅ Migration: migration_name completed')
   except sqlite3.OperationalError as e:
      if 'duplicate column name' in str(e):
         print('⚠️  Migration: migration_name already applied')
      else:
         raise
```

---

## 🎨 Updating Frontend UI

**When to use**: Need to change web interface appearance or functionality

**File**: `templates/index.html`

**Common patterns**:

1. **Adding new filter**:

```html
<!-- Add filter control -->
<div class="filter-group">
   <label for="filterX">Filter by X:</label>
   <select id="filterX" onchange="filterVehicles()">
      <option value="">All</option>
      <option value="value1">Value 1</option>
   </select>
</div>
```

2. **Adding vehicle field display**:

```html
<!-- In vehicle card template -->
<div class="field">
   <strong>New Field:</strong> ${vehicle.new_field || 'N/A'}
</div>
```

3. **Adding API call**:

```javascript
async function callNewEndpoint() {
    try {
        const response = await fetch('/api/new-endpoint');
        const data = await response.json();
        if (data.success) {
            // Handle success
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
```

---

## 📝 General Guidelines

### Before making changes:

1. Read relevant files completely
2. Understand existing patterns
3. Check for similar existing functionality
4. Consider backward compatibility

### While making changes:

1. Follow existing code style
2. Add appropriate error handling
3. Update documentation if needed
4. Test changes locally

### After making changes:

1. Run the scraper to verify it works
2. Check database for expected data
3. Test API endpoints if modified
4. Review generated reports
5. Commit with descriptive message

### Code quality:

- ✅ Use type hints
- ✅ Add docstrings
- ✅ Handle errors gracefully
- ✅ Log meaningful messages with emojis
- ✅ Avoid hardcoded values (use constants)
- ✅ Keep functions focused (single responsibility)
