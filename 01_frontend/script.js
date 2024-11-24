// Initialize the map
const map = L.map('map').setView([40.7128, -74.0060], 13); // Default: New York City

// Add a base layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);
