# Data Folder

This folder holds seed data and helper scripts for the **Cities API**.

## Files

- `cities_data.py` – Python list/dicts of seed cities (name, country, population, geometry, etc.).  
  Used by the management command to load sample data.

## How to Load the Data

```bash
# Activate venv & ensure DB is configured
python3 manage.py migrate
python3 manage.py load_cities  # if you created trails_api/management/commands/load_cities.py