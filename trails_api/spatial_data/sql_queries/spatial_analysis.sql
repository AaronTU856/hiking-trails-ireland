-- 1. Trails within 10km of any town
SELECT 
    t.trail_name,
    tn.name AS nearest_town,
    ST_Distance(t.start_point::geography, tn.location::geography) / 1000 AS distance_km
FROM trails_api_trail t
JOIN trails_api_town tn
  ON ST_DWithin(t.start_point::geography, tn.location::geography, 10000)
ORDER BY distance_km ASC;

-- 2. Closest town to each trail
SELECT 
    t.trail_name,
    tn.name AS nearest_town,
    ROUND(ST_Distance(t.start_point::geography, tn.location::geography) / 1000, 2) AS distance_km
FROM trails_api_trail t
JOIN LATERAL (
    SELECT name, location
    FROM trails_api_town
    ORDER BY t.start_point <-> location
    LIMIT 1
) tn ON TRUE;

-- 3. Total population within 20km of all trails combined
SELECT SUM(population) AS total_population_near_trails
FROM trails_api_town tn
WHERE EXISTS (
    SELECT 1 FROM trails_api_trail t
    WHERE ST_DWithin(t.start_point::geography, tn.location::geography, 20000)
);

-- 4. Find all trails within 50 km of Galway (approximate coords)
SELECT trail_name, distance_km
FROM trails_api_trail
WHERE ST_DWithin(
    start_point::geography,
    ST_SetSRID(ST_MakePoint(-9.05, 53.27), 4326)::geography,
    50000
);
