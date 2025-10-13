// City Mapper - Main JavaScript functionality

let map;

let cityMarkers = L.layerGroup();

let allCitiesData = [];

 

// Initialize map when page loads

document.addEventListener('DOMContentLoaded', function() {

    initializeMap();

    loadCities();

    setupEventListeners();

});

 

function initializeMap() {

    // Initialize the map - Center on Europe for better view

    map = L.map('map').setView([53.5, -7.7], 6); // Changed to Europe center

 

    // Add OpenStreetMap tiles

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {

        attribution: '© OpenStreetMap contributors',

        maxZoom: 18

    }).addTo(map);

 

    // Add the markers layer group to map

    cityMarkers.addTo(map);

 

    // Add map click event for adding new cities

    map.on('click', function(e) {

        const { lat, lng } = e.latlng;

        document.getElementById('city-lat').value = lat.toFixed(6);

        document.getElementById('city-lng').value = lng.toFixed(6);

       

        // Show add city modal

        const modal = new bootstrap.Modal(document.getElementById('addCityModal'));

        modal.show();

    });

}

 

function loadCities() {

    console.log('Loading cities...');

    showLoading(true);

   

    // Try the geojson endpoint first

    fetch('/api/cities/geojson/')

        .then(response => {

            console.log('Response status:', response.status);

            console.log('Response headers:', response.headers);

            if (!response.ok) {

                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);

            }

            return response.json();

        })

        .then(data => {

            console.log('Raw API response:', data);

            console.log('Data type:', typeof data);

            console.log('Data keys:', Object.keys(data || {}));

           

            // Handle different response formats

            if (data && data.features) {
                // Handle both normal and nested GeoJSON structures
                const features = Array.isArray(data.features)
                    ? data.features
                    : Array.isArray(data.features.features)
                        ? data.features.features
                        : [];
            
                console.log('Loaded', features.length, 'features (after flattening nested GeoJSON)');
            
                allCitiesData = features;
                displayCitiesOnMap(allCitiesData);
                updateCityCount(allCitiesData.length);
                console.log(`Successfully loaded ${allCitiesData.length} cities`);

            } else if (data && data.error) {

                // API returned an error

                throw new Error(`API Error: ${data.error}`);

            } else if (Array.isArray(data)) {

                // API returned array of cities, convert to GeoJSON

                console.log('Converting array to GeoJSON format');

                const geojsonFeatures = data.map(city => ({

                    type: "Feature",

                    geometry: {

                        type: "Point",

                        coordinates: [parseFloat(city.longitude || 0), parseFloat(city.latitude || 0)]

                    },

                    properties: city

                }));

                allCitiesData = geojsonFeatures;

                displayCitiesOnMap(allCitiesData);

                updateCityCount(allCitiesData.length);

                console.log(`Successfully converted and loaded ${allCitiesData.length} cities`);

            } else {

                // Unexpected format, try the regular API endpoint

                console.warn('Unexpected API response format, trying regular endpoint');

                return loadCitiesFromRegularAPI();

            }

        })

        .catch(error => {

            console.error('Error with geojson endpoint:', error);

            // Fallback to regular API

            return loadCitiesFromRegularAPI();

        })

        .finally(() => {

            showLoading(false);

        });

}

 

function loadCitiesFromRegularAPI() {

    console.log('Trying regular API endpoint...');

   

    return fetch('/api/cities/')

        .then(response => {

            console.log('Regular API response status:', response.status);

            if (!response.ok) {

                throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);

            }

            return response.json();

        })

        .then(data => {

            console.log('Regular API response:', data);

           

            let citiesArray;

           

            // Handle different response formats

            if (data && data.results && Array.isArray(data.results)) {

                // Paginated response

                citiesArray = data.results;

            } else if (Array.isArray(data)) {

                // Direct array response

                citiesArray = data;

            } else {

                throw new Error('Unexpected response format from regular API');

            }

           

            // Convert to GeoJSON format

            const geojsonFeatures = citiesArray.map(city => ({

                type: "Feature",

                geometry: {

                    type: "Point",

                    coordinates: [parseFloat(city.longitude || 0), parseFloat(city.latitude || 0)]

                },

                properties: city

            }));

           

            allCitiesData = geojsonFeatures;

            displayCitiesOnMap(allCitiesData);

            updateCityCount(allCitiesData.length);

            console.log(`Successfully loaded ${allCitiesData.length} cities from regular API`);

        })

        .catch(error => {

            console.error('Error loading cities from both endpoints:', error);

           

            // Show specific error messages

            if (error.message.includes('404')) {

                showAlert('API endpoints not found. Please check your URLs configuration.', 'danger');

            } else if (error.message.includes('500')) {

                showAlert('Server error. Please check your API views and database.', 'danger');

            } else if (error.message.includes('Failed to fetch')) {

                showAlert('Network error. Please check if the server is running.', 'danger');

            } else {

                showAlert(`Error loading cities: ${error.message}`, 'danger');

            }

        });

}

 

 

function displayCitiesOnMap(cities) {

    // Clear existing markers

    cityMarkers.clearLayers();

   

    cities.forEach(city => {

        try {

            // Fix: Access coordinates from geometry.coordinates

            const { geometry, properties } = city;

           

            if (!geometry || !geometry.coordinates || !Array.isArray(geometry.coordinates)) {

                console.warn('Invalid geometry for city:', properties?.name || 'Unknown');

                return;

            }

           

            const [lng, lat] = geometry.coordinates;

           

            // Validate coordinates

            if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {

                console.warn('Invalid coordinates for city:', properties?.name, lat, lng);

                return;

            }

           

            // Create custom icon based on population

            const populationSize = getMarkerSize(properties.population || 0);

            const customIcon = L.divIcon({

                className: 'custom-marker',

                html: `<div style="background-color: #007bff; border-radius: 50%; width: ${populationSize}px; height: ${populationSize}px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,

                iconSize: [populationSize, populationSize],

                iconAnchor: [populationSize/2, populationSize/2]

            });

           

            // Create marker

            const marker = L.marker([lat, lng], { icon: customIcon })

                .bindPopup(createPopupContent(properties), {

                    maxWidth: 300,

                    className: 'custom-popup'

                });

           

            // Add click event to show detailed info

            marker.on('click', function() {

                showCityInfo(properties);

            });

           

            // Store city data with marker for reference

            marker.cityData = properties;

           

            cityMarkers.addLayer(marker);

           

        } catch (error) {

            console.error('Error creating marker for city:', city, error);

        }

    });

   

    // Fit map to show all markers if cities exist

    if (cities.length > 0) {

        try {

            const group = new L.featureGroup(cityMarkers.getLayers());

            if (group.getLayers().length > 0) {

                map.fitBounds(group.getBounds().pad(0.1));

            }

        } catch (error) {

            console.error('Error fitting bounds:', error);

        }

    }

}

 

function createPopupContent(city) {

    // Safely handle missing properties

    const name = city.name || 'Unknown City';

    const country = city.country || 'Unknown Country';

    const population = city.population ? city.population.toLocaleString() : 'Unknown';

    const latitude = city.latitude || 'Unknown';

    const longitude = city.longitude || 'Unknown';

   

    return `

        <div class="city-popup">

            <h6>${name}, ${country}</h6>

            <div class="city-popup-info">

                <span class="population">👥 Population: ${population}</span>

                ${city.founded_year ? `<span>📅 Founded: ${city.founded_year}</span>` : ''}

                ${city.area_km2 ? `<span>📏 Area: ${city.area_km2} km²</span>` : ''}

                <span class="coordinates">📍 ${latitude}, ${longitude}</span>

                ${city.description ? `<div style="margin-top: 8px; font-style: italic;">${city.description}</div>` : ''}

            </div>

            <div class="popup-buttons">

                <button class="btn btn-sm btn-primary" onclick="zoomToCity(${city.id})">Zoom</button>

                <button class="btn btn-sm btn-info" onclick="showCityDetails(${city.id})">Details</button>

            </div>

        </div>

    `;

}

 

function performSearch() {

    const query = document.getElementById('city-search').value.trim();

    if (!query) {

        displayCitiesOnMap(allCitiesData);

        updateCityCount(allCitiesData.length);

        return;

    }

   

    showLoading(true);

   

    fetch(`/api/cities/search/?q=${encodeURIComponent(query)}`)

        .then(response => {

            if (!response.ok) {

                throw new Error(`HTTP error! status: ${response.status}`);

            }

            return response.json();

        })

        .then(data => {

            console.log('Search response:', data);

           

            let filteredCities;

           

            if (Array.isArray(data)) {

                // If search returns array of city objects, convert to GeoJSON

                filteredCities = data.map(city => ({

                    type: "Feature",

                    geometry: {

                        type: "Point",

                        coordinates: [parseFloat(city.longitude || 0), parseFloat(city.latitude || 0)]

                    },

                    properties: city

                }));

            } else if (data.features && Array.isArray(data.features)) {

                // If search returns GeoJSON

                filteredCities = data.features;

            } else {

                // Filter from existing data as fallback

                filteredCities = allCitiesData.filter(city =>

                    city.properties.name.toLowerCase().includes(query.toLowerCase()) ||

                    city.properties.country.toLowerCase().includes(query.toLowerCase())

                );

            }

           

            displayCitiesOnMap(filteredCities);

            updateCityCount(filteredCities.length);

           

            if (filteredCities.length === 0) {

                showAlert('No cities found matching your search.', 'info');

            }

        })

        .catch(error => {

            console.error('Error searching cities:', error);

           

            // Fallback to client-side search

            const filteredCities = allCitiesData.filter(city =>

                city.properties.name.toLowerCase().includes(query.toLowerCase()) ||

                city.properties.country.toLowerCase().includes(query.toLowerCase())

            );

           

            displayCitiesOnMap(filteredCities);

            updateCityCount(filteredCities.length);

           

            if (filteredCities.length === 0) {

                showAlert('No cities found matching your search.', 'info');

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

 

function showCityInfo(city) {

    const infoPanel = document.getElementById('city-info');

    const infoContent = document.getElementById('city-info-content');

   

    if (!infoPanel || !infoContent) {

        console.warn('City info panel elements not found');

        return;

    }

   

    // Safely handle missing properties

    const name = city.name || 'Unknown City';

    const country = city.country || 'Unknown Country';

    const population = city.population ? city.population.toLocaleString() : 'Unknown';

    const latitude = city.latitude || 0;

    const longitude = city.longitude || 0;

   

    infoContent.innerHTML = `

        <div class="row">

            <div class="col-12">

                <h5 class="text-primary">${name}, ${country}</h5>

            </div>

        </div>

        <div class="city-info-grid">

            <div class="info-item">

                <label>Population</label>

                <div class="value">${population}</div>

            </div>

            ${city.founded_year ? `

                <div class="info-item">

                    <label>Founded</label>

                    <div class="value">${city.founded_year}</div>

                </div>

            ` : ''}

            ${city.area_km2 ? `

                <div class="info-item">

                    <label>Area</label>

                    <div class="value">${city.area_km2} km²</div>

                </div>

            ` : ''}

            ${city.timezone ? `

                <div class="info-item">

                    <label>Timezone</label>

                    <div class="value">${city.timezone}</div>

                </div>

            ` : ''}

            <div class="info-item">

                <label>Coordinates</label>

                <div class="value">${parseFloat(latitude).toFixed(6)}, ${parseFloat(longitude).toFixed(6)}</div>

            </div>

        </div>

        ${city.description ? `

            <div class="mt-3">

                <label><strong>Description</strong></label>

                <div class="value">${city.description}</div>

            </div>

        ` : ''}

        <div class="mt-3">

            <button class="btn btn-primary btn-sm me-2" onclick="zoomToCity(${city.id})">Zoom to City</button>

            <button class="btn btn-outline-secondary btn-sm" onclick="copyCoordinates('${latitude}', '${longitude}')">Copy Coordinates</button>

        </div>

    `;

   

    infoPanel.style.display = 'block';

    infoPanel.scrollIntoView({ behavior: 'smooth' });

}

 

function setupEventListeners() {

    // Search functionality

    const searchBtn = document.getElementById('search-btn');

    const searchInput = document.getElementById('city-search');

    const clearSearchBtn = document.getElementById('clear-search');

    const refreshBtn = document.getElementById('refresh-map');

    const closeInfoBtn = document.getElementById('close-info');

    const addCityBtn = document.getElementById('add-city-btn');

    const saveCityBtn = document.getElementById('save-city');

   

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

            displayCitiesOnMap(allCitiesData);

            updateCityCount(allCitiesData.length);

        });

    }

   

    if (refreshBtn) {

        refreshBtn.addEventListener('click', loadCities);

    }

   

    if (closeInfoBtn) {

        closeInfoBtn.addEventListener('click', function() {

            const infoPanel = document.getElementById('city-info');

            if (infoPanel) {

                infoPanel.style.display = 'none';

            }

        });

    }

   

    if (addCityBtn) {

        addCityBtn.addEventListener('click', function() {

            const modalElement = document.getElementById('addCityModal');

            if (modalElement) {

                const modal = new bootstrap.Modal(modalElement);

                modal.show();

            }

        });

    }

   

    if (saveCityBtn) {

        saveCityBtn.addEventListener('click', saveNewCity);

    }

}

 

function saveNewCity() {

    const nameInput = document.getElementById('city-name');

    const countryInput = document.getElementById('city-country');

    const latInput = document.getElementById('city-lat');

    const lngInput = document.getElementById('city-lng');

    const populationInput = document.getElementById('city-population');

    const foundedInput = document.getElementById('city-founded');

    const descriptionInput = document.getElementById('city-description');

   

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

   

    fetch('/api/cities/', {

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

        showAlert('City added successfully!', 'success');

       

        // Close modal

        const modalElement = document.getElementById('addCityModal');

        if (modalElement) {

            const modal = bootstrap.Modal.getInstance(modalElement);

            if (modal) {

                modal.hide();

            }

        }

       

        // Reset form

        const form = document.getElementById('add-city-form');

        if (form) {

            form.reset();

        }

       

        // Reload cities

        loadCities();

    })

    .catch(error => {

        console.error('Error saving city:', error);

        showAlert('Error saving city. Please try again.', 'danger');

    });

}

 

// Utility functions

function zoomToCity(cityId) {

    const city = allCitiesData.find(c => c.properties.id === parseInt(cityId));

    if (city && city.geometry && city.geometry.coordinates) {

        const [lng, lat] = city.geometry.coordinates;

        if (!isNaN(lat) && !isNaN(lng)) {

            map.setView([lat, lng], 12);

        }

    }

}

 

function showCityDetails(cityId) {

    const city = allCitiesData.find(c => c.properties.id === parseInt(cityId));

    if (city) {

        showCityInfo(city.properties);

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

 

function updateCityCount(count) {

    const countElement = document.getElementById('city-count');

    if (countElement) {

        countElement.textContent = `${count} cities loaded`;

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