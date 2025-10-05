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
