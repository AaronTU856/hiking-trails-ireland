# Web Mapping Project (Django + GeoDjango + PostGIS + Leaflet)

## Overview
This project is a minimal full-stack web mapping app built with:

- **Backend**: Django + GeoDjango with PostgreSQL/PostGIS
- **Frontend**: Leaflet.js for interactive maps
- **Features**:
  - Leaflet map on the homepage (`/`)
  - Basic JSON API endpoints:
    - `/api/status/` – health/status check
    - `/api/locations/add/` – add a new location
  - Django Admin interface for managing spatial data

---

## How to Run (Local)

```bash
# 1) Activate the virtual environment
source webmapping_env/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure the database
# settings_production.py is preconfigured to use:
#   DB name: webmapping_production
#   Host: 127.0.0.1
#   User: webmapping
#   Password:

# 4) Apply migrations & collect static files
python manage.py migrate --settings=webmapping_project.settings_production
python manage.py collectstatic --noinput --settings=webmapping_project.settings_production

# 5) Create an admin (superuser) account
python manage.py createsuperuser --settings=webmapping_project.settings_production

# 6) Run the development server (with static files in production mode)
python manage.py runserver --insecure --settings=webmapping_project.settings_production


## How to Run (Dev)

1. **Environment**
   
   python3 -m venv webmapping_env
   source webmapping_env/bin/activate
   pip install -r requirements.txt

2. **Create a PostgreSQL DB and enable PostGIS:**
    CREATE DATABASE webmapping_db;
    \c webmapping_db
    CREATE EXTENSION IF NOT EXISTS postgis;

3. **Migrations**
    python3 manage.py migrate
    python3 manage.py load_cities

4. **Run Server**
    python3 manage.py runserver

    Admin: http://127.0.0.1:8000/admin/
    Site root/Map: http://127.0.0.1:8000/
    API root: http://127.0.0.1:8000/api/cities/

   **API Endpoints (Cities API)**

List / Create: GET|POST /api/cities/

Detail / Update / Delete: GET|PUT|PATCH|DELETE /api/cities/{id}/

GeoJSON: GET /api/cities/geojson/

Stats: GET /api/cities/stats/

Countries summary: GET /api/cities/countries/

Spatial (within radius): POST /api/cities/within-radius/

Spatial (bounding box): POST /api/cities/bbox/


     **Running Tests**
# Make sure your DB user can create test DBs and PostGIS is available in template1
python3 manage.py test cities_api -v 2
# Save output as artifact for submission:
python3 manage.py test cities_api -v 2 > documentation/test_results.txt

**Screenshots Location**

Put all screenshots in documentation/:

swagger_ui_screenshot.png

api_endpoints_overview.png

pytest_screenshots.png

any admin/map screenshots
