console.log("✅ dashboard_map.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    const map = L.map('map').setView([53.4, -8.2], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // ✅ Load trails
    fetch("/api/trails/geojson/")
        .then(res => res.json())
        .then(data => {
            L.geoJSON(data, {
                pointToLayer: (feature, latlng) =>
                    L.marker(latlng, { icon: L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    }) }),
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(`<b>${feature.properties.trail_name}</b><br>${feature.properties.county}`);
                }
            }).addTo(map);
        });

    // ✅ Load towns
    fetch("/api/trails/towns/geojson/")
        .then(res => res.json())
        .then(data => {
            L.geoJSON(data, {
                pointToLayer: (feature, latlng) =>
                    L.marker(latlng, { icon: L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    }) }),
                    onEachFeature: (feature, layer) => {
                        const props = feature.properties;
                        layer.bindPopup(`
                            <b>${props.name}</b><br>
                            Latitude: ${feature.geometry.coordinates[1].toFixed(4)}<br>
                            Longitude: ${feature.geometry.coordinates[0].toFixed(4)}
                        `);
                    }      
            }).addTo(map);
        });
});
