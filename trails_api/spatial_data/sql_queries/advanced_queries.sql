-- 1. Hard trails longer than 10 km
SELECT trail_name, county, distance_km, difficulty
FROM trails_api_trail
WHERE difficulty = 'Hard' AND distance_km > 10
ORDER BY distance_km DESC;

-- 2. Urban towns with population over 3000
SELECT name, town_type, population
FROM trails_api_town
WHERE town_type = 'Urban' AND population > 3000
ORDER BY population DESC;

-- 3. Average distance per county
SELECT county, ROUND(AVG(distance_km),2) AS avg_distance_km
FROM trails_api_trail
GROUP BY county
ORDER BY avg_distance_km DESC;

-- 4. Trails with dogs allowed and parking available
SELECT trail_name, county, difficulty, dogs_allowed, parking_available
FROM trails_api_trail
WHERE dogs_allowed = 'yes' AND parking_available = 'yes';


-- 5. Find longest trail in each county
SELECT DISTINCT ON (county)
    county, trail_name, distance_km
FROM trails_api_trail
ORDER BY county, distance_km DESC;

-- 6. Compare average trail length by difficulty
SELECT difficulty, ROUND(AVG(distance_km), 2) AS avg_length_km
FROM trails_api_trail
GROUP BY difficulty
ORDER BY avg_length_km DESC;

-- 7. Join trails and towns by nearest town name
SELECT t.trail_name, t.distance_km, tw.name AS town_name, tw.population
FROM trails_api_trail t
JOIN trails_api_town tw ON t.nearest_town = tw.name
ORDER BY tw.population DESC
LIMIT 15;