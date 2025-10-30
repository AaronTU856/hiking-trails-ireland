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
