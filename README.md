# 🥾 Irish Trails Web Mapping Application

## 1. Project Overview
The Trails API and web mapping project is a Django + GeoDjango based web application
that provides RESTful and GeoJSON endpoints for Irish hiking trail data.
The project integrates PostGIS, Leaflet and Mapbox for spatial analysis radius and bounding box queries.
and visualization using Leaflet and Mapbox.


## 2. Features Implemented
### ✅ Core
- REST API for Trails (`/api/trails/`)
- GeoJSON endpoint (`/api/trails/geojson/`)
- Map view with Leaflet and Mapbox tiles
- Spatial queries:
  - `within-radius`
  - `in-bounding-box`
- Interactive Leaflet map (`/api/trails/map/`)
- API info endpoint (`/api/trails/info/`)

### 🧭 Additional
- Django admin for Trails
- Custom management command `create_sample_trails`
- Interactive Leaflet map (`/api/trails/map/`)
- Pagination, filtering, and search via Django REST Framework
- CORS support for external clients
- DRF Spectacular for auto-generated Swagger documentation

---

## 3. Technologies Used

 **Backend**  Django 4.2 , GeoDjango 
 **Database**  PostgreSQL , PostGIS 
 **Frontend**  Leaflet.js , Bootstrap 
 **API** Django REST Framework , drf_spectacular 
 **Spatial Tools**  Mapbox, django-geojson 
 **Dev Environment**  Homebrew GDAL/GEOS/PROJ setup 

---

## 4. Installation & Setup

# Clone project
git clone https://github.com/AaronTU856/hiking-trails-ireland.git
cd trails_api

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create and seed database
python manage.py migrate
python manage.py create_sample_trails

# Run server
python manage.py runserver


 (Endpoint)                      (Method)              (Description)                             

 `/api/trails/`                GET / POST          List or create trails                   
 `/api/trails/<id>/`           GET / PUT / DELETE  Retrieve, update or delete a trail      
 `/api/trails/geojson/`        GET                 Get all trails as GeoJSON               
 `/api/trails/within-radius/`  POST                Find trails near a coordinate           
 `/api/trails/bbox/`           POST                Find trails in bounding box             
 `/api/trails/stats/`          GET                 Trail summary statistics                
`/api/trails/info/`            GET                 API metadata                            
 `/api/trails/map/`            GET                 Map interface                           
 `/api/trails/test/`           GET                 Testing interface – not activated yet 
`/api/trails/towns/geojson/`   GET                 GeoJSON of towns with filters

URL                     Description                         

`/dashboard/`            Dashboard home page                  
`/dashboard/analytics/`  Data analytics and charts for trails 
`/maps/api/status/`          Health/status check endpoint



## 6. Tests & Validation

- Implemented but not activated yet

- Trails API Test Interface (Django view template)

- Unit tests planned for:

- Radius search (within-radius)

- GeoJSON response structure

- Database model constraints

### Debugging

- The town filters (type and population) were not working because two URL routes were defined for the same endpoint (/api/trails/towns/geojson/).

- The duplicate class-based view (TownGeoJSONView) was removed.

- The function-based view (towns_geojson) was kept, allowing proper filtering and debug logging.

- Confirmed working filters for town_type, min_population, and max_population.

### Proximity Search

- Trails and towns are now searchable by proximity using GeoDjango’s DistanceFunction.

- Clicking on the map triggers a radius search that:

- Returns trails ordered by distance.

- Displays results on the map and in the side panel.

- Each marker now uses a numbered icon for clarity.

### GeoJSON Fix

- Initially, trails did not appear on the map due to mismatched field names (location vs start_point).

- Serializer and Leaflet JS were updated to use the correct coordinate field.

## 7. Future Enhancements

- Add user accounts for trail submissions

- Enable Mapbox layer switching

- Connect frontend search UI for live queries

- Automate tests via Django’s TestCase class

## 8  Testing

All API routes tested using pytest and Django’s test client.

Tests for GeoJSON endpoints, proximity search, and radius queries all pass.



9. References

Mapbox Documentation – https://console.mapbox.com

Django GeoDjango – https://docs.djangoproject.com/en/4.2/ref/contrib/gis/

Django REST Framework – https://www.django-rest-framework.org/api-guide/metadata/

DRF Spectacular – https://drf-spectacular.readthedocs.io/en/latest/readme.html#testing

LeafletJS – https://leafletjs.com/examples/geojson/