-- filepath: Week 2/spatial_data/sql_queries/advanced_queries.sql

-- 1. Calculate county centroids and compare with capitals
SELECT
    co.name_tag as countyname,
    ST_X(ST_Centroid(co.geom)) as centroid_lng,
    ST_Y(ST_Centroid(co.geom)) as centroid_lat,
    c.name as nearest_city,
    ST_Distance(
        ST_Centroid(co.geom)::geography,
        c.geom::geography
    ) / 1000 as distance_to_nearest_city_km
FROM irish_counties co
LEFT JOIN LATERAL (
    SELECT name, geom
    FROM european_cities
    ORDER BY co.geom <-> european_cities.geom
    LIMIT 1
) c ON true;

-- 2. Transportation route intersections with county boundaries
SELECT
    tr.route_name,
    co.name_tag as countyname,
    ST_Length(ST_Intersection(tr.geom, co.geom)::geography) / 1000 as intersection_length_km
FROM transportation_routes tr, irish_counties co
WHERE ST_Intersects(tr.geom, co.geom)
ORDER BY intersection_length_km DESC;

-- 3. Population density analysis by creating grid cells
WITH grid AS (
    SELECT
        row_number() OVER() as grid_id,
        geom as grid_cell
    FROM (
        SELECT ST_MakeEnvelope(
            -10 + (x * 2), -- longitude start + grid size
            50 + (y * 1),  -- latitude start + grid size
            -10 + ((x + 1) * 2),
            50 + ((y + 1) * 1),
            4326
        ) as geom
        FROM generate_series(0, 10) as x,
             generate_series(0, 8) as y
    ) sq
)
SELECT
    g.grid_id,
    COUNT(c.id) as cities_count,
    SUM(c.population) as total_population,
    ST_AsText(ST_Centroid(g.grid_cell)) as grid_center
FROM grid g
LEFT JOIN european_cities c ON ST_Within(c.geom, g.grid_cell)
GROUP BY g.grid_id, g.grid_cell
HAVING COUNT(c.id) > 0
ORDER BY total_population DESC;

-- 4. Find optimal location for a new distribution center
-- (Geographic center weighted by population)
SELECT
    ST_X(center_point) as optimal_longitude,
    ST_Y(center_point) as optimal_latitude,
    'Optimal Distribution Center Location' as description
FROM (
    SELECT ST_Centroid(
        ST_Collect(
            ST_MakePoint(
                ST_X(geom) * (population::float / 1000000), -- Weight by population
                ST_Y(geom) * (population::float / 1000000)
            )
        )
    ) as center_point
    FROM european_cities
    WHERE population > 500000
) sq;