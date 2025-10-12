-- paste the code you posted, then save (Ctrl+O, Enter, Ctrl+X)
-- filepath: Week 2/spatial_data/sql_queries/spatial_analysis.sql

-- 1. Find cities within Ireland (point-in-polygon)
SELECT c.name, c.population, co.name_tag AS countyname
FROM european_cities c, irish_counties co
WHERE ST_Within(c.geom, co.geom);

-- 2. Calculate distances between cities
SELECT
    c1.name as city1,
    c2.name as city2,
    ST_Distance(c1.geom::geography, c2.geom::geography) / 1000 as distance_km
FROM european_cities c1, european_cities c2
WHERE c1.id < c2.id  -- Avoid duplicates
ORDER BY distance_km
LIMIT 10;

-- 3. Find closest city to Dublin
SELECT
    name,
    country,
    ST_Distance(
        geom::geography,
        (SELECT geom::geography FROM european_cities WHERE name = 'Dublin')
    ) / 1000 as distance_from_dublin_km
FROM european_cities
WHERE name != 'Dublin'
ORDER BY distance_from_dublin_km
LIMIT 5;

-- 4. Cities within 500km of Paris
SELECT
    name,
    country,
    population,
    ST_Distance(
        geom::geography,
        (SELECT geom::geography FROM european_cities WHERE name = 'Paris')
    ) / 1000 as distance_km
FROM european_cities
WHERE ST_DWithin(
    geom::geography,
    (SELECT geom::geography FROM european_cities WHERE name = 'Paris'),
    500000  -- 500km in meters
)
ORDER BY distance_km;

-- 5. Create buffer zones around major cities (population > 2M)
SELECT
    name,
    population,
    ST_Area(ST_Buffer(geom::geography, 50000)) / 1000000 as buffer_50km_area_km2
FROM european_cities
WHERE population > 2000000;