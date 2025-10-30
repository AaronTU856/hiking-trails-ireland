from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import django
from django.db import connection


def hello_map(request):
    """Main map view with environment information"""
    
    # Get version information
    django_version = django.get_version()
    
    # Get PostGIS version
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT PostGIS_Version();")
            postgis_version = cursor.fetchone()[0].split()[0]
    except:
        postgis_version = "Unknown"
    
    # Get location count
    location_count = Location.objects.count()
    
    context = {
        'django_version': django_version,
        'postgis_version': postgis_version,
        'location_count': location_count,
    }
    
    return render(request, 'maps/hello_map.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def add_location_api(request):
    """API endpoint to add new locations"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Validate coordinates
        lat = float(data['latitude'])
        lng = float(data['longitude'])
        
        if lat < -90 or lat > 90:
            return JsonResponse({
                'error': 'Latitude must be between -90 and 90'
            }, status=400)
        
        if lng < -180 or lng > 180:
            return JsonResponse({
                'error': 'Longitude must be between -180 and 180'
            }, status=400)
        
        # Create location
        location = Location.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            point=Point(lng, lat)
        )
        
        return JsonResponse({
            'success': True,
            'location': {
                'id': location.id,
                'name': location.name,
                'latitude': lat,
                'longitude': lng
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': f'Invalid coordinate values: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def api_status(request):
    """API health check endpoint"""
    
    # Test database connection
    try:
        location_count = Location.objects.count()
        test_area_count = TestArea.objects.count()
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)}"
        location_count = 0
        test_area_count = 0
    
    # Test PostGIS functionality
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ST_GeomFromText('POINT(0 0)');")
            postgis_status = "Working"
    except Exception as e:
        postgis_status = f"Error: {str(e)}"
    
    return JsonResponse({
        'status': 'healthy',
        'database': {
            'status': db_status,
            'locations': location_count,
            'test_areas': test_area_count
        },
        'postgis': {
            'status': postgis_status
        },
        'django': {
            'version': django.get_version(),
            'debug': django.conf.settings.DEBUG
        }
    })

def environment_test(request):
    """Comprehensive environment test page"""
    
    tests = []
    
    # Test 1: Database Connection
    try:
        Location.objects.count()
        tests.append({
            'name': 'Database Connection',
            'status': 'passed',
            'message': 'Successfully connected to PostgreSQL'
        })
    except Exception as e:
        tests.append({
            'name': 'Database Connection',
            'status': 'failed',
            'message': f'Database error: {str(e)}'
        })
    
    # Test 2: PostGIS Functionality
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ST_AsText(ST_GeomFromText('POINT(0 0)'));")
            result = cursor.fetchone()[0]
            tests.append({
                'name': 'PostGIS Functionality',
                'status': 'passed',
                'message': f'PostGIS working correctly. Test result: {result}'
            })
    except Exception as e:
        tests.append({
            'name': 'PostGIS Functionality',
            'status': 'failed',
            'message': f'PostGIS error: {str(e)}'
        })
    
    # Test 3: Model Creation
    try:
        test_point = Point(0, 0)
        test_location = Location(name="Test", point=test_point)
        test_location.full_clean()  # Validate without saving
        tests.append({
            'name': 'Model Validation',
            'status': 'passed',
            'message': 'Spatial models are correctly configured'
        })
    except Exception as e:
        tests.append({
            'name': 'Model Validation',
            'status': 'failed',
            'message': f'Model error: {str(e)}'
        })
    
    context = {
        'tests': tests,
        'overall_status': 'passed' if all(t['status'] == 'passed' for t in tests) else 'failed'
    }
    
    return render(request, 'maps/environment_test.html', context)
