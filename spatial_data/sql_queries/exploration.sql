-- 1. Basic data exploration
-- Count features in each table
SELECT 'Irish Counties' as dataset, COUNT(*) as feature_count FROM irish_counties
UNION ALL
SELECT 'European Cities' as dataset, COUNT(*) as feature_count FROM european_cities
UNION ALL 
SELECT 'Transportation' as dataset, COUNT(*) as feature_count FROM transportation_routes;

-- 2. Examine county data structure
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'irish_counties';

-- 3. Show largest counties by area
SELECT
    name_tag AS countyname,
    ST_Area(geom::geography) / 1000000 as area_km2
FROM irish_counties
ORDER BY area_km2 DESC
LIMIT 5;

-- 4. Show cities by population
SELECT name, country, population,
    ST_X(geom) as longitude,
    ST_Y(geom) as latitude
FROM european_cities
ORDER BY population DESC;

-- 5. Transportation route lengths 
SELECT
    route_name,
    route_type,
    ST_Length(geom::geography) / 1000 as length_km
FROM transportation_routes
ORDER BY length_km DESC;

