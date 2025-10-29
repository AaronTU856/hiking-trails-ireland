console.log("✅ trails_map.js loaded");
let map;
let trailMarkers;
let allTrailsData = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log("📍 DOM loaded, initializing map...");
    initializeMap();
    loadTrails();
    setupEventListeners();

    enableProximitySearch();


});
    // initialize proximity search after map exists
//     setTimeout(() => {
//         if (window.map) {
//             window.proximitySearch = new ProximitySearch(window.map);
//             console.log("✅ Proximity search ready");
//         } else {
//             console.error("⚠️ Map not found for proximity search");
//         }
//     }, 1000);
// });

function initializeMap() {
    console.log("🗺️ Map initializing...");

    // If already created, skip
    if (window.trailsMap instanceof L.Map) {
        console.warn("Map already exists — skipping reinitialization");
        return;
    }

    // ✅ Create and store globally (NO shadowing)
    window.trailsMap = L.map('map').setView([53.5, -7.7], 7);
    console.log("✅ Created trailsMap:", window.trailsMap instanceof L.Map, window.trailsMap);

    // ✅ Add tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href=\"https://carto.com/\">CartoDB</a> contributors',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(window.trailsMap);

    // ✅ Initialize marker layer
    window.trailMarkers = L.layerGroup().addTo(window.trailsMap);
    console.log("✅ Trail marker layer added to map");

    // ✅ Custom green icon
    const greenIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    L.Marker.prototype.options.icon = greenIcon;

    console.log("✅ Map and base layer ready!");
}
function loadTrails() {
    console.log("🚀 Loading trails...");
    showLoading(true);

    fetch("/api/trails/geojson/")
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Raw API response:", data);
            console.log("Data type:", typeof data);
            console.log("Data keys:", Object.keys(data || {}));

            let features = [];

            // ✅ Handle GeoJSON FeatureCollection
            if (data && data.type === "FeatureCollection" && Array.isArray(data.features)) {
                features = data.features;

            // ✅ Handle nested FeatureCollection (rare)
            } else if (data && data.features && Array.isArray(data.features.features)) {
                features = data.features.features;

            // ✅ Handle plain array (non-GeoJSON response)
            } else if (Array.isArray(data)) {
                console.warn("Converting non-GeoJSON array to GeoJSON format...");
                features = data.map(trail => ({
                    type: "Feature",
                    geometry: {
                        type: "Point",
                        coordinates: [
                            parseFloat(trail.longitude || 0),
                            parseFloat(trail.latitude || 0)
                        ]
                    },
                    properties: trail
                }));
            }

            // ✅ Handle results
            if (features.length > 0) {
                console.log(`✅ Loaded ${features.length} trail features`);
                allTrailsData = features;
                displayTrailsOnMap(features);
                updateTrailCount(features.length);
            } else {
                console.warn("⚠️ No valid features found in API response, trying fallback...");
                return loadTrailsFromRegularAPI();
            }
        })
        .catch(error => {
            console.error("❌ Error with geojson endpoint:", error);
            return loadTrailsFromRegularAPI();
        })
        .finally(() => {
            showLoading(false);
        });
}

 

function loadTrailsFromRegularAPI() {

    console.log('Trying regular API endpoint...');

   

    return fetch('/api/trails/')

        .then(response => {

            console.log('Regular API response status:', response.status);

            if (!response.ok) {

                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);

            }

            return response.json();

        })

        .then(data => {

            console.log('Regular API response:', data);

           

            let trailsArray;

           

            // Handle different response formats

            if (data && data.results && Array.isArray(data.results)) {

                // Paginated response

                trailsArray = data.results;

            } else if (Array.isArray(data)) {

                // Direct array response

                trailsArray = data;

            } else {

                throw new Error('Unexpected response format from regular API');

            }

           

            // Convert to GeoJSON format

            const geojsonFeatures = trailsArray.map(trail => ({

                type: "Feature",

                geometry: {

                    type: "Point",

                    coordinates: [parseFloat(trail.longitude || 0), parseFloat(trail.latitude || 0)]

                },

                properties: trail

            }));

           

            allTrailsData = geojsonFeatures;

            displayTrailsOnMap(allTrailsData);

            updateTrailCount(allTrailsData.length);

            console.log(`Successfully loaded ${allTrailsData.length} trails from regular API`);

        })

        .catch(error => {

            console.error('Error loading trails from both endpoints:', error);

           

            // Show specific error messages

            if (error.message.includes('404')) {

                showAlert('API endpoints not found. Please check your URLs configuration.', 'danger');

            } else if (error.message.includes('500')) {

                showAlert('Server error. Please check your API views and database.', 'danger');

            } else if (error.message.includes('Failed to fetch')) {

                showAlert('Network error. Please check if the server is running.', 'danger');

            } else {

                showAlert(`Error loading trails: ${error.message}`, 'danger');

            }

        });

}

function displayTrailsOnMap(trails) {
    if (!window.trailsMap) {
        console.error("❌ trailsMap not initialized before displaying trails");
        return;
    }

    // ✅ Ensure layer group exists
    if (!window.trailMarkers || !(window.trailMarkers instanceof L.LayerGroup)) {
        console.log("🧭 Creating new trailMarkers LayerGroup...");
        window.trailMarkers = L.layerGroup().addTo(window.trailsMap);
    } else {
        console.log("🧹 Clearing existing trail markers...");
        window.trailMarkers.clearLayers();
    }

    let validMarkers = 0;

    // ✅ Accept GeoJSON or plain objects
    const trailArray = Array.isArray(trails)
        ? trails
        : trails.features || [];

    trailArray.forEach(trail => {
        try {
            // Accept both GeoJSON + plain API trails
            const geometry = trail.geometry || null;
            const properties = trail.properties || trail;

            let lat, lng;
            if (geometry?.coordinates && Array.isArray(geometry.coordinates)) {
                [lng, lat] = geometry.coordinates;
            } else {
                lat = parseFloat(properties.latitude);
                lng = parseFloat(properties.longitude);
            }

            if (isNaN(lat) || isNaN(lng)) {
                console.warn(`⚠️ Invalid coordinates for ${properties?.trail_name || 'Unnamed Trail'}`);
                return;
            }

            // ✅ Unified marker icon
            const marker = L.marker([lat, lng]).bindPopup(`
                <strong>${properties.trail_name || 'Unnamed Trail'}</strong><br>
                County: ${properties.county || 'Unknown'}<br>
                Distance: ${properties.distance_km || '?'} km<br>
                Difficulty: ${properties.difficulty || 'Unknown'}
            `);

            window.trailMarkers.addLayer(marker);
            validMarkers++;
        } catch (err) {
            console.error("❌ Error creating marker:", err);
        }
    });

    if (validMarkers > 0 && typeof window.trailMarkers.getBounds === "function") {
        const bounds = window.trailMarkers.getBounds();
        window.trailsMap.fitBounds(bounds, { padding: [30, 30] });
        console.log(`✅ Displayed ${validMarkers} valid trail markers`);
    } else {
        console.warn("⚠️ No valid markers to display or invalid trailMarkers type");
    }
}


function createPopupContent(trail) {
    // Safely handle missing properties
    const name = trail.trail_name || 'Unknown Trail';
    const county = trail.county || 'Unknown County';
    const distance = trail.distance_km ? `${trail.distance_km} km` : 'Unknown';
    const difficulty = trail.difficulty || 'Unknown';
    const description = trail.description || 'No description available';
    const latitude = trail.latitude || 0;
    const longitude = trail.longitude || 0;

    return `
        <div class="trail-popup">
            <h6>${name}</h6>
            <div class="trail-popup-info">
                <span>📍 <strong>County:</strong> ${county}</span><br>
                <span>📏 <strong>Distance:</strong> ${distance}</span><br>
                <span>🏔️ <strong>Difficulty:</strong> ${difficulty}</span><br>
                <span>🗺️ <strong>Coordinates:</strong> ${latitude.toFixed(4)}, ${longitude.toFixed(4)}</span>
                ${description ? `<div style="margin-top: 8px; font-style: italic;">${description}</div>` : ''}
            </div>
            <div class="popup-buttons" style="margin-top: 8px;">
                <button class="btn btn-sm btn-primary" onclick="zoomToTrail(${latitude}, ${longitude})">Zoom</button>
                <button class="btn btn-sm btn-info" onclick="showTrailDetails('${name}')">Details</button>
            </div>
        </div>
    `;
}

function performSearch() {

    const query = document.getElementById('trail-search').value.trim();

    if (!query) {

        displayTrailsOnMap(allTrailsData);

        updateTrailCount(allTrailsData.length);

        return;

    }

   

    showLoading(true);

   

    fetch(`/api/trails/search/?q=${encodeURIComponent(query)}`)

        .then(response => {

            if (!response.ok) {

                throw new Error(`HTTP error! status: ${response.status}`);

            }

            return response.json();

        })

        .then(data => {

            console.log('Search response:', data);

           

            let filteredTrails;

           

            if (Array.isArray(data)) {

                // If search returns array of trail objects, convert to GeoJSON

                filteredTrails = data.map(trail => ({

                    type: "Feature",

                    geometry: {

                        type: "Point",

                        coordinates: [parseFloat(trail.longitude || 0), parseFloat(trail.latitude || 0)]

                    },

                    properties: trail

                }));

            } else if (data.features && Array.isArray(data.features)) {

                // If search returns GeoJSON

                filteredTrails = data.features;

            } else {

                // Filter from existing data as fallback

                filteredTrails = allTrailsData.filter(trail =>

                    trail.properties.name.toLowerCase().includes(query.toLowerCase()) ||

                    trail.properties.country.toLowerCase().includes(query.toLowerCase())

                );

            }

           

            displayTrailsOnMap(filteredTrails);

            updateTrailCount(filteredTrails.length);

           

            if (filteredTrails.length === 0) {

                showAlert('No trails found matching your search.', 'info');

            }

        })

        .catch(error => {

            console.error('Error searching trails:', error);

           

            // Fallback to client-side search

            const filteredTrails = allTrailsData.filter(trail =>

                trail.properties.name.toLowerCase().includes(query.toLowerCase()) ||

                trail.properties.country.toLowerCase().includes(query.toLowerCase())

            );

           

            displayTrailsOnMap(filteredTrails);

            updateTrailCount(filteredTrails.length);

           

            if (filteredTrails.length === 0) {

                showAlert('No trails found matching your search.', 'info');

            } else {

                showAlert('Search performed offline due to connection issues.', 'warning');

            }

        })

        .finally(() => {

            showLoading(false);

        });

}

 

function getMarkerSize(population) {

    const pop = parseInt(population) || 0;

    if (pop < 100000) return 8;

    if (pop < 500000) return 12;

    if (pop < 1000000) return 16;

    if (pop < 5000000) return 20;

    return 24;

}

 

function showTrailInfo(trail) {

    const infoPanel = document.getElementById('trail-info');

    const infoContent = document.getElementById('trail-info-content');

   

    if (!infoPanel || !infoContent) {

        console.warn('Trail info panel elements not found');

        return;

    }

   

    // Safely handle missing properties

    const name = trail.name || 'Unknown Trail';

    const country = trail.country || 'Unknown Country';

    const population = trail.population ? trail.population.toLocaleString() : 'Unknown';

    const latitude = trail.latitude || 0;

    const longitude = trail.longitude || 0;

   

    infoContent.innerHTML = `

        <div class="row">

            <div class="col-12">

                <h5 class="text-primary">${name}, ${country}</h5>

            </div>

        </div>

        <div class="trail-info-grid">

            <div class="info-item">

                <label>Population</label>

                <div class="value">${population}</div>

            </div>

            ${trail.founded_year ? `

                <div class="info-item">

                    <label>Founded</label>

                    <div class="value">${trail.founded_year}</div>

                </div>

            ` : ''}

            ${trail.area_km2 ? `

                <div class="info-item">

                    <label>Area</label>

                    <div class="value">${trail.area_km2} km²</div>

                </div>

            ` : ''}

            ${trail.timezone ? `

                <div class="info-item">

                    <label>Timezone</label>

                    <div class="value">${trail.timezone}</div>

                </div>

            ` : ''}

            <div class="info-item">

                <label>Coordinates</label>

                <div class="value">${parseFloat(latitude).toFixed(6)}, ${parseFloat(longitude).toFixed(6)}</div>

            </div>

        </div>

        ${trail.description ? `

            <div class="mt-3">

                <label><strong>Description</strong></label>

                <div class="value">${trail.description}</div>

            </div>

        ` : ''}

        <div class="mt-3">

            <button class="btn btn-primary btn-sm me-2" onclick="zoomToTrail(${trail.id})">Zoom to Trail</button>

            <button class="btn btn-outline-secondary btn-sm" onclick="copyCoordinates('${latitude}', '${longitude}')">Copy Coordinates</button>

        </div>

    `;

   

    infoPanel.style.display = 'block';

    infoPanel.scrollIntoView({ behavior: 'smooth' });

}

 

function setupEventListeners() {

    // Search functionality

    const searchBtn = document.getElementById('search-btn');

    const searchInput = document.getElementById('trail-search');

    const clearSearchBtn = document.getElementById('clear-search');

    const refreshBtn = document.getElementById('refresh-map');

    const closeInfoBtn = document.getElementById('close-info');

    const addTrailBtn = document.getElementById('add-trail-btn');

    const saveTrailBtn = document.getElementById('save-trail');

   

    if (searchBtn) {

        searchBtn.addEventListener('click', performSearch);

    }

   

    if (searchInput) {

        searchInput.addEventListener('keypress', function(e) {

            if (e.key === 'Enter') {

                performSearch();

            }

        });

    }

   

    if (clearSearchBtn) {

        clearSearchBtn.addEventListener('click', function() {

            if (searchInput) {

                searchInput.value = '';

            }

            displayTrailsOnMap(allTrailsData);

            updateTrailCount(allTrailsData.length);

        });

    }

   

    if (refreshBtn) {

        refreshBtn.addEventListener('click', loadTrails);

    }

   

    if (closeInfoBtn) {

        closeInfoBtn.addEventListener('click', function() {

            const infoPanel = document.getElementById('trail-info');

            if (infoPanel) {

                infoPanel.style.display = 'none';

            }

        });

    }

   

    if (addTrailBtn) {

        addTrailBtn.addEventListener('click', function() {

            const modalElement = document.getElementById('addTrailModal');

            if (modalElement) {

                const modal = new bootstrap.Modal(modalElement);

                modal.show();

            }

        });

    }

   

    if (saveTrailBtn) {

        saveTrailBtn.addEventListener('click', saveNewTrail);

    }

}

 

function saveNewTrail() {

    const nameInput = document.getElementById('trail-name');

    const countryInput = document.getElementById('trail-country');

    const latInput = document.getElementById('trail-lat');

    const lngInput = document.getElementById('trail-lng');

    const populationInput = document.getElementById('trail-population');

    const foundedInput = document.getElementById('trail-founded');

    const descriptionInput = document.getElementById('trail-description');

   

    if (!nameInput || !countryInput || !latInput || !lngInput || !populationInput) {

        showAlert('Required form elements not found.', 'danger');

        return;

    }

   

    const formData = {

        name: nameInput.value.trim(),

        country: countryInput.value.trim(),

        latitude: parseFloat(latInput.value),

        longitude: parseFloat(lngInput.value),

        population: parseInt(populationInput.value),

        founded_year: foundedInput?.value ? parseInt(foundedInput.value) : null,

        description: descriptionInput?.value?.trim() || ''

    };

   

    // Validation

    if (!formData.name || !formData.country || isNaN(formData.latitude) || isNaN(formData.longitude) || isNaN(formData.population)) {

        showAlert('Please fill in all required fields with valid values.', 'warning');

        return;

    }

   

    if (formData.latitude < -90 || formData.latitude > 90 || formData.longitude < -180 || formData.longitude > 180) {

        showAlert('Please enter valid coordinates (latitude: -90 to 90, longitude: -180 to 180).', 'warning');

        return;

    }

   

    fetch('/api/trails/', {

        method: 'POST',

        headers: {

            'Content-Type': 'application/json',

            'X-CSRFToken': getCsrfToken()

        },

        body: JSON.stringify(formData)

    })

    .then(response => {

        if (!response.ok) {

            throw new Error(`HTTP error! status: ${response.status}`);

        }

        return response.json();

    })

    .then(data => {

        showAlert('Trail added successfully!', 'success');

       

        // Close modal

        const modalElement = document.getElementById('addTrailModal');

        if (modalElement) {

            const modal = bootstrap.Modal.getInstance(modalElement);

            if (modal) {

                modal.hide();

            }

        }

       

        // Reset form

        const form = document.getElementById('add-trail-form');

        if (form) {

            form.reset();

        }

       

        // Reload trails

        loadTrails();

    })

    .catch(error => {

        console.error('Error saving trail:', error);

        showAlert('Error saving trail. Please try again.', 'danger');

    });

}

 

// Utility functions

function zoomToTrail(trailId) {

    const trail = allTrailsData.find(c => c.properties.id === parseInt(trailId));

    if (trail && trail.geometry && trail.geometry.coordinates) {

        const [lng, lat] = trail.geometry.coordinates;

        if (!isNaN(lat) && !isNaN(lng)) {

            map.setView([lat, lng], 12);

        }

    }

}

 

function showTrailDetails(trailId) {

    const trail = allTrailsData.find(c => c.properties.id === parseInt(trailId));

    if (trail) {

        showTrailInfo(trail.properties);

    }

}

 

function copyCoordinates(lat, lng) {

    const coords = `${lat}, ${lng}`;

    if (navigator.clipboard && navigator.clipboard.writeText) {

        navigator.clipboard.writeText(coords).then(() => {

            showAlert('Coordinates copied to clipboard!', 'info');

        }).catch(() => {

            showAlert('Failed to copy coordinates to clipboard.', 'warning');

        });

    } else {

        // Fallback for older browsers

        const textArea = document.createElement('textarea');

        textArea.value = coords;

        document.body.appendChild(textArea);

        textArea.select();

        try {

            document.execCommand('copy');

            showAlert('Coordinates copied to clipboard!', 'info');

        } catch (err) {

            showAlert('Failed to copy coordinates to clipboard.', 'warning');

        }

        document.body.removeChild(textArea);

    }

}

 

function updateTrailCount(count) {

    const countElement = document.getElementById('trail-count');

    if (countElement) {

        countElement.textContent = `${count} trails loaded`;

    }

}

 

function showLoading(show) {

    const searchBtn = document.getElementById('search-btn');

    if (searchBtn) {

        if (show) {

            searchBtn.innerHTML = '<span class="loading"></span> Loading...';

            searchBtn.disabled = true;

        } else {

            searchBtn.innerHTML = '🔍 Search';

            searchBtn.disabled = false;

        }

    }

}

 

function showAlert(message, type) {

    // Create alert element

    const alertDiv = document.createElement('div');

    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;

    alertDiv.style.top = '20px';

    alertDiv.style.right = '20px';

    alertDiv.style.zIndex = '9999';

    alertDiv.style.minWidth = '300px';

   

    alertDiv.innerHTML = `

        ${message}

        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>

    `;

   

    document.body.appendChild(alertDiv);

   

    // Auto remove after 5 seconds

    setTimeout(() => {

        if (alertDiv.parentNode) {

            alertDiv.remove();

        }

    }, 5000);

}

 

function getCsrfToken() {

    // Try multiple methods to get CSRF token

   

    // Method 1: From cookie

    const cookies = document.cookie.split(';');

    for (let cookie of cookies) {

        const [name, value] = cookie.trim().split('=');

        if (name === 'csrftoken') {

            return value;

        }

    }

   

    // Method 2: From meta tag

    const metaTag = document.querySelector('meta[name="csrf-token"]');

    if (metaTag) {

        return metaTag.getAttribute('content');

    }

   

    // Method 3: From form input

    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');

    if (csrfInput) {

        return csrfInput.value;

    }

    console.warn('CSRF token not found');
    return '';
}

console.log("✅ trails_map.js fully loaded");


function enableProximitySearch() {
    const toggleBtn = document.getElementById("toggle-search");
    const radiusInput = document.getElementById("radius-input");

    if (!toggleBtn || !radiusInput) {
        console.warn("⚠️ Proximity UI elements missing");
        return;
    }

    let searchEnabled = false;
    let searchMarker = null;
    let radiusCircle = null;

    toggleBtn.addEventListener("click", () => {
        searchEnabled = !searchEnabled;

        if (searchEnabled) {
            toggleBtn.textContent = "Disable Search";
            toggleBtn.classList.remove("btn-success");
            toggleBtn.classList.add("btn-danger");
            showAlert("🧭 Click the map to find trails near a point", "info");
        } else {
            toggleBtn.textContent = "Enable Search";
            toggleBtn.classList.remove("btn-danger");
            toggleBtn.classList.add("btn-success");

            if (searchMarker) window.trailsMap.removeLayer(searchMarker);
            if (radiusCircle) window.trailsMap.removeLayer(radiusCircle);
        }
    });

    // ✅ Handle map click
    window.trailsMap.on("click", async (e) => {
        if (!searchEnabled) return;

        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        const radiusKm = parseFloat(radiusInput.value) || 50;

        console.log(`📍 Proximity search at (${lat}, ${lng}) radius: ${radiusKm}km`);

        // Remove old marker/circle
        if (searchMarker) window.trailsMap.removeLayer(searchMarker);
        if (radiusCircle) window.trailsMap.removeLayer(radiusCircle);

        // Add marker & circle
        const blueIcon = L.icon({
            iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
            shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        searchMarker = L.marker([lat, lng], { icon: blueIcon }).addTo(window.trailsMap);
        
        radiusCircle = L.circle([lat, lng], {
            radius: radiusKm * 1000,
            color: "blue",
            fillOpacity: 0.15,
        }).addTo(window.trailsMap);

        showLoading(true);

        try {
            const response = await fetch("/api/trails/within-radius/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ latitude: lat, longitude: lng, radius_km: radiusKm }),
            });

            if (!response.ok) throw new Error(`HTTP error ${response.status}`);

            const data = await response.json();
            console.log("✅ Proximity search response:", data);

            if (data.nearest_trails?.length) {
                const formatted = data.nearest_trails.map(t => ({
                    type: "Feature",
                    geometry: {
                        type: "Point",
                        coordinates: [parseFloat(t.longitude), parseFloat(t.latitude)]
                    },
                    properties: t
                }));
            
                displayTrailsOnMap(formatted);
                showAlert(`✅ Found ${data.nearest_trails.length} trails within ${radiusKm} km`, "success");
            
                // ✅ Update results panel
                const resultsDiv = document.getElementById("trail-results");
                if (resultsDiv) {
                    resultsDiv.innerHTML = `
                        <h6 class="fw-bold mb-2">Trails Found (${data.nearest_trails.length})</h6>
                        <ul class="list-unstyled m-0" style="max-height:25vh; overflow-y:auto;">
                            ${data.nearest_trails
                                .map(t => `
                                    <li class="border-bottom py-1">
                                        <strong>${t.trail_name || "Unnamed Trail"}</strong><br>
                                        <small>${t.county || "Unknown"} • ${t.distance_km || "?"} km • ${t.difficulty || "?"}</small>
                                    </li>
                                `)
                                .join("")}
                        </ul>
                    `;
                }
            } else {
                showAlert("⚠️ No trails found nearby", "warning");
                const resultsDiv = document.getElementById("trail-results");
                if (resultsDiv) {
                    resultsDiv.innerHTML = `<small class="text-muted">No trails found within ${radiusKm} km.</small>`;
                }
            }
            
        } catch (err) {
            console.error("❌ Error performing proximity search:", err);
            showAlert("❌ Error performing proximity search", "danger");
        } finally {
            showLoading(false);
        }
    });
}





//         controlPanel.appendChild(proximityToggle);
       
//         // Add radius input
//         const radiusInput = document.createElement('input');
//         radiusInput.id = 'radius-input';
//         radiusInput.type = 'number';
//         radiusInput.value = '100';
//         radiusInput.placeholder = 'Radius (km)';
//         radiusInput.className = 'form-control d-none';
//         radiusInput.style.width = '120px';
//         radiusInput.style.display = 'inline-block';
//         radiusInput.style.marginLeft = '10px';
       
//         controlPanel.appendChild(radiusInput);
//     }
   
//     toggleProximityMode() {
//         this.isProximityMode = !this.isProximityMode;
//         const toggleBtn = document.getElementById('proximity-toggle');
//         const radiusInput = document.getElementById('radius-input');
       
//         if (this.isProximityMode) {
//             toggleBtn.innerHTML = 'Exit Proximity';
//             toggleBtn.className = 'btn btn-danger';
//             radiusInput.classList.remove('d-none');
//             this.map.getContainer().style.cursor = 'crosshair';
//             showAlert('Click anywhere on the map to find nearest trails', 'info');
//         } else {
//             toggleBtn.innerHTML = 'Proximity Search';
//             toggleBtn.className = 'btn btn-outline-primary';
//             radiusInput.classList.add('d-none');
//             this.map.getContainer().style.cursor = '';
//             this.clearProximityResults();
//         }
//     }
   
//     async performProximitySearch(lat, lng) {
//         this.clearProximityResults();
    
//         // Add search marker
//         this.searchMarker = L.marker([lat, lng], {
//             icon: L.icon({
//                 iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
//                 shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
//                 iconSize: [25, 41],
//                 iconAnchor: [12, 41],
//                 popupAnchor: [1, -34],
//                 shadowSize: [41, 41],
//                 className: 'search-marker-icon'
//             })
//         }).addTo(this.map);
    
//         this.searchMarker.bindPopup(`
//             <strong>Search Point</strong><br>
//             Lat: ${lat.toFixed(6)}<br>
//             Lng: ${lng.toFixed(6)}
//         `).openPopup();
    
//         showLoading(true);
    
//         try {
//             const response = await fetch('/api/trails/within-radius/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': getCsrfToken()
//                 },
//                 body: JSON.stringify({
//                     latitude: lat,
//                     longitude: lng,
//                     radius_km: parseFloat(document.getElementById('radius-input').value || 10)
//                 })
//             });
    
//             if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    
//             const data = await response.json();
    
//             // ✅ Your API returns data.nearest_trails (not data.trails)
//             this.displayNearestTrails(data.nearest_trails);
//             this.updateResultsPanel(data);
    
//         } catch (error) {
//             console.error('Error finding nearest trails:', error);
//             showAlert('Error performing proximity search. Please try again.', 'danger');
//         } finally {
//             showLoading(false);
//         }
//     }

//     displayNearestTrails(trails) {
//         this.nearestTrailsLayer.clearLayers();
    
//         trails.forEach((trail, index) => {
//             const { lat, lng } = trail.coordinates;
//             if (isNaN(lat) || isNaN(lng)) return;
    
//             const marker = L.marker([lat, lng], {
//                 icon: this.getNumberedIcon(index + 1)
//             });
    
//             const popupContent = `
//                 <strong>${trail.name}</strong><br>
//                 County: ${trail.county}<br>
//                 Difficulty: ${trail.difficulty}<br>
//                 Distance: ${trail.distance_km} km<br>
//                 From You: ${trail.distance_to_user} km
//             `;
//             marker.bindPopup(popupContent);
//             this.nearestTrailsLayer.addLayer(marker);
//         });
    
//         // Fit map to bounds
//         if (trails.length > 0) {
//             const group = new L.featureGroup([
//                 this.searchMarker,
//                 ...this.nearestTrailsLayer.getLayers()
//             ]);
//             this.window.map.fitBounds(group.getBounds().pad(0.1));
//         }
//     }
    
//     getNumberedIcon(number) {
//         return L.divIcon({
//             className: 'numbered-marker',
//             html: `<div class="marker-number">${number}</div>`,
//             iconSize: [30, 30],
//             iconAnchor: [15, 15]
//         });
//     }
   
//     updateResultsPanel(data) {
//         let resultsPanel = document.getElementById('proximity-results');
//         if (!resultsPanel) {
//             resultsPanel = document.createElement('div');
//             resultsPanel.id = 'proximity-results';
//             resultsPanel.className = 'proximity-results-panel';
//             document.body.appendChild(resultsPanel);
//         }
    
//         const trails = data.nearest_trails || [];
//         resultsPanel.innerHTML = `
//             <div class="card shadow">
//                 <div class="card-header bg-success text-white">
//                     <h5 class="mb-0">Nearest Trails</h5>
//                     <button type="button" class="btn-close btn-close-white" onclick="proximitySearch.clearProximityResults()"></button>
//                 </div>
//                 <div class="card-body" style="max-height:300px; overflow-y:auto;">
//                     <p><strong>Search Point:</strong> ${data.search_point.lat.toFixed(4)}, ${data.search_point.lng.toFixed(4)}</p>
//                     <p><strong>Trails Found:</strong> ${trails.length}</p>
//                     <div class="results-list">
//                         ${trails.map((trail, index) => `
//                             <div class="result-item border-bottom py-2" 
//                                  onclick="proximitySearch.zoomToTrail(${trail.coordinates.lat}, ${trail.coordinates.lng})">
//                                 <strong>#${index + 1} ${trail.name}</strong><br>
//                                 <small>${trail.county} • ${trail.difficulty} • ${trail.distance_to_user} km away</small>
//                             </div>
//                         `).join('')}
//                     </div>
//                 </div>
//             </div>
//         `;
//         resultsPanel.style.display = 'block';
//     }
//     zoomToTrail(lat, lng) {
//         this.map.setView([lat, lng], 12);
//     }
   
//     clearProximityResults() {
//         if (this.searchMarker) {
//             this.map.removeLayer(this.searchMarker);
//             this.searchMarker = null;
//         }
       
//         this.nearestTrailsLayer.clearLayers();
       
//         if (this.radiusCircle) {
//             this.map.removeLayer(this.radiusCircle);
//             this.radiusCircle = null;
//         }
       
//         const resultsPanel = document.getElementById('proximity-results');
//         if (resultsPanel) {
//             resultsPanel.style.display = 'none';
//        }



