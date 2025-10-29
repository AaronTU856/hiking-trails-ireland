console.log("✅ dashboard_map.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Initializing dashboard map...");

    // ✅ Prevent multiple Leaflet initializations
    const existingMap = L.DomUtil.get('map');
    if (existingMap !== null) {
        existingMap._leaflet_id = null;
    }

    // ✅ Initialize map
    const map = L.map('map').setView([53.4, -8.2], 7);

    // 🗺️ Base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // 🟩 Custom icons
    const trailIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41]
    });

    const townIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41]
    });

    // ✅ Global layers
    let trailsLayer = null;
    let townsLayer = null;

    // ✅ Dashboard counters
    function updateDashboardSummary(trailsCount, townsCount, totalPopulation = 0) {
        const trailsEl = document.getElementById('trails-count');
        const townsEl = document.getElementById('towns-count');
        const popEl = document.getElementById('total-population');

        if (trailsEl) trailsEl.textContent = trailsCount.toLocaleString();
        if (townsEl) townsEl.textContent = townsCount.toLocaleString();
        if (popEl) popEl.textContent = totalPopulation.toLocaleString();

        console.log(`📊 Updated Summary → Trails: ${trailsCount}, Towns: ${townsCount}, Pop: ${totalPopulation}`);
    }

    // ✅ Load Trails
    function loadTrails() {
        const url = `/api/trails/geojson/`;
        console.log("🔗 Fetching trails:", url);

        fetch(url)
            .then(res => res.json())
            .then(data => {
                console.log("📦 Trails loaded:", data.features?.length || 0);

                // Remove previous trails layer
                if (trailsLayer) map.removeLayer(trailsLayer);

                trailsLayer = L.geoJSON(data, {
                    pointToLayer: (feature, latlng) => L.marker(latlng, { icon: trailIcon }),
                    onEachFeature: (feature, layer) => {
                        const p = feature.properties;
                        layer.bindPopup(`
                            <b>${p.trail_name}</b><br>
                            <b>County:</b> ${p.county || "Unknown"}<br>
                            <b>Distance:</b> ${p.distance_km || "?"} km<br>
                            <b>Difficulty:</b> ${p.difficulty || "N/A"}<br>
                            <b>Dogs Allowed:</b> ${p.dogs_allowed || "N/A"}<br>
                            <b>Parking:</b> ${p.parking_available || "N/A"}
                        `);
                    }
                }).addTo(map);

                updateDashboardSummary(data.features.length, townsLayer ? townsLayer.getLayers().length : 0);
            })
            .catch(err => console.error('❌ Error loading trails:', err));
    }

    // ✅ Load Towns
    function loadTowns() {
        const url = `/api/trails/towns/geojson/`;
        console.log("🔗 Fetching towns:", url);

        fetch(url)
            .then(res => res.json())
            .then(data => {
                console.log("🏘️ Towns loaded:", data.features?.length || 0);

                // Remove old towns
                if (townsLayer) map.removeLayer(townsLayer);

                townsLayer = L.geoJSON(data, {
                    pointToLayer: (feature, latlng) => L.marker(latlng, { icon: townIcon }),
                    onEachFeature: (feature, layer) => {
                        const p = feature.properties;
                        layer.bindPopup(`
                            <b>${p.name}</b><br>
                            <b>Type:</b> ${p.town_type || "N/A"}<br>
                            <b>Population:</b> ${p.population ? p.population.toLocaleString() : "N/A"}<br>
                            <b>Area:</b> ${p.area ? p.area + " km²" : "N/A"}<br>
                            <b>Latitude:</b> ${feature.geometry.coordinates[1].toFixed(4)}<br>
                            <b>Longitude:</b> ${feature.geometry.coordinates[0].toFixed(4)}
                        `);
                    }
                }).addTo(map);

                const totalPop = data.features.reduce((sum, f) => sum + (f.properties.population || 0), 0);
                updateDashboardSummary(trailsLayer ? trailsLayer.getLayers().length : 0, data.features.length, totalPop);
            })
            .catch(err => console.error('❌ Error loading towns:', err));
    }

    // ✅ Toggles
    const showTrails = document.getElementById('show-trails');
    const showTowns = document.getElementById('show-towns');

    if (showTrails) {
        showTrails.addEventListener('change', (e) => {
            if (trailsLayer) {
                if (e.target.checked) map.addLayer(trailsLayer);
                else map.removeLayer(trailsLayer);
            }
        });
    }

    if (showTowns) {
        showTowns.addEventListener('change', (e) => {
            if (townsLayer) {
                if (e.target.checked) map.addLayer(townsLayer);
                else map.removeLayer(townsLayer);
            }
        });
    }

    // ✅ Initial load
    loadTrails();
    loadTowns();
});
