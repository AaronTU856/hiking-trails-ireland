# 🥾 Irish Trails Web Mapping Application

## 1. Project Overview
The Trails API and web mapping project is a Django + GeoDjango based web application
that provides RESTful and GeoJSON endpoints for Irish hiking trail data.
The project integrates spatial analysis (radius and bounding box queries)
and visualization using Leaflet and Mapbox.


## 2. Features Implemented
### ✅ Core
- REST API for Trails (`/api/trails/`)
- GeoJSON endpoint (`/api/trails/geojson/`)
- Map view with Leaflet and Mapbox tiles
- Spatial queries:
  - `within-radius`
  - `in-bounding-box`
- Trail statistics summary (`/api/trails/stats/`)
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
 Layer | Technology |

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
cd trails_mapping

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

## 6. Tests & Validation

- Implemented but not activated yet

- Trails API Test Interface (Django view template)

- Unit tests planned for:

- Radius search (within-radius)

- GeoJSON response structure

- Database model constraints

## 7. Future Enhancements

- Add user accounts for trail submissions

- Enable Mapbox layer switching

- Connect frontend search UI for live queries

- Automate tests via Django’s TestCase class

9. References

Mapbox Documentation – https://console.mapbox.com

Django GeoDjango – https://docs.djangoproject.com/en/4.2/ref/contrib/gis/

Django REST Framework – https://www.django-rest-framework.org/api-guide/metadata/

DRF Spectacular – https://drf-spectacular.readthedocs.io/en/latest/readme.html#testing

LeafletJS – https://leafletjs.com/examples/geojson/