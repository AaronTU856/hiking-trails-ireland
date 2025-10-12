# filepath: Week 2/create_sample_data.py
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection details (update with your credentials)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'webmapping_db',   
    'user': 'webmapping',          
    'password': 'awm123'           
}


def create_cities_table():
    """Create and populate European cities table"""
   
    # Sample cities data (name, longitude, latitude, population, country)
    cities_data = [
        ('Dublin', -6.2603, 53.3498, 1400000, 'Ireland'),
        ('London', -0.1276, 51.5074, 9000000, 'United Kingdom'),
        ('Paris', 2.3522, 48.8566, 11000000, 'France'),
        ('Berlin', 13.4050, 52.5200, 3700000, 'Germany'),
        ('Madrid', -3.7038, 40.4168, 6600000, 'Spain'),
        ('Rome', 12.4964, 41.9028, 2800000, 'Italy'),
        ('Amsterdam', 4.9041, 52.3676, 900000, 'Netherlands'),
        ('Brussels', 4.3517, 50.8503, 1200000, 'Belgium'),
        ('Vienna', 16.3738, 48.2082, 1900000, 'Austria'),
        ('Stockholm', 18.0686, 59.3293, 1600000, 'Sweden'),
        ('Oslo', 10.7522, 59.9139, 700000, 'Norway'),
        ('Copenhagen', 12.5683, 55.6761, 800000, 'Denmark'),
        ('Helsinki', 24.9384, 60.1699, 650000, 'Finland'),
        ('Warsaw', 21.0122, 52.2297, 1800000, 'Poland'),
        ('Prague', 14.4378, 50.0755, 1300000, 'Czech Republic'),
    ]
   
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
       
        # Create the table
        cur.execute("""
            DROP TABLE IF EXISTS european_cities;
            CREATE TABLE european_cities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                population INTEGER,
                country VARCHAR(100),
                geom GEOMETRY(POINT, 4326)
            );
        """)
       
        # Insert city data
        for city_data in cities_data:
            name, lng, lat, population, country = city_data
            cur.execute("""
                INSERT INTO european_cities (name, population, country, geom)
                VALUES (%s, %s, %s, ST_GeomFromText('POINT(%s %s)', 4326))
            """, (name, population, country, lng, lat))
       
        # Create spatial index
        cur.execute("""
            CREATE INDEX idx_european_cities_geom
            ON european_cities USING GIST(geom);
        """)
       
        conn.commit()
        print(f"Successfully created european_cities table with {len(cities_data)} cities")
       
        # Verify the data
        cur.execute("SELECT COUNT(*) FROM european_cities;")
        count = cur.fetchone()['count']
        print(f"Verified: {count} cities in database")
       
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

def create_transportation_table():
    """Create sample transportation routes"""
   
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
       
        # Create transportation table
        cur.execute("""
            DROP TABLE IF EXISTS transportation_routes;
            CREATE TABLE transportation_routes (
                id SERIAL PRIMARY KEY,
                route_name VARCHAR(100),
                route_type VARCHAR(50),
                geom GEOMETRY(LINESTRING, 4326)
            );
        """)
       
        # Sample routes (simplified for demonstration)
        routes = [
            ('Dublin-Cork Highway', 'highway', 'LINESTRING(-6.2603 53.3498, -8.4861 51.8985)'),
            ('London-Birmingham', 'highway', 'LINESTRING(-0.1276 51.5074, -1.8904 52.4862)'),
            ('Paris-Lyon', 'railway', 'LINESTRING(2.3522 48.8566, 4.8357 45.7640)'),
            ('Berlin-Hamburg', 'highway', 'LINESTRING(13.4050 52.5200, 9.9937 53.5511)'),
            ('Madrid-Barcelona', 'railway', 'LINESTRING(-3.7038 40.4168, 2.1734 41.3851)'),
        ]
       
        for route_name, route_type, wkt_geom in routes:
            cur.execute("""
                INSERT INTO transportation_routes (route_name, route_type, geom)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            """, (route_name, route_type, wkt_geom))
       
        # Create spatial index
        cur.execute("""
            CREATE INDEX idx_transportation_geom
            ON transportation_routes USING GIST(geom);
        """)
       
        conn.commit()
        print(f"Successfully created transportation_routes table with {len(routes)} routes")
       
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Creating sample spatial data...")
    create_cities_table()
    create_transportation_table()
    print("Sample data creation complete!")

