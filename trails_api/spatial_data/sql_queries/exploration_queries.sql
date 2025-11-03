-- 1. Count of trails and towns
SELECT 'Trails' AS dataset, COUNT(*) AS feature_count FROM trails_api_trail
UNION ALL
SELECT 'Towns', COUNT(*) FROM trails_api_town;

-- 2. Average trail length and elevation
SELECT 
    AVG(distance_km)::NUMERIC(5,2) AS avg_distance_km,
    AVG(elevation_gain_m)::NUMERIC(5,2) AS avg_elevation_m
FROM trails_api_trails;

-- 3. Population by town type
SELECT town_type, SUM(population) AS total_population
FROM trails_api_town
GROUP BY town_type;

-- 4. Count of trails allowing dogs
SELECT dogs_allowed, COUNT(*) AS total
FROM trails_api_trail
GROUP BY dogs_allowed;

-- 5. List all trails with their nearest town
SELECT trail_name, nearest_town, distance_km, difficulty
FROM trails_api_trail
ORDER BY distance_km DESC
LIMIT 10;

-- 6. Show total number of trails by county
SELECT county, COUNT(*) AS trail_count
FROM trails_api_trail
GROUP BY county
ORDER BY trail_count DESC;

-- 7. Average population per town type
SELECT town_type, AVG(population)::INT AS avg_population
FROM trails_api_town
GROUP BY town_type
ORDER BY avg_population DESC;

-- 8. Trails that intersect or touch town boundaries
SELECT 
    t.trail_name,
    tw.name AS town_name,
    ST_AsText(ST_Intersection(t.start_point, tw.location)) AS intersection_geom
FROM trails_api_trail AS t
JOIN trails_api_town AS tw
ON ST_Intersects(t.start_point, tw.location)
LIMIT 10;

-- 9 Towns within 5 km of aTrail
SELECT 
    t.trail_name,
    tw.name AS nearest_town,
    ROUND((ST_Distance(t.start_point::geography, tw.location::geography) / 1000)::numeric, 2) AS distance_km
FROM trails_api_trail AS t
JOIN trails_api_town AS tw
ON ST_DWithin(t.start_point::geography, tw.location::geography, 5000)
ORDER BY distance_km ASC
LIMIT 20;



