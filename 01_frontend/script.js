
// Initialize the map
const map = L.map('map').setView([42.396680895764796, -71.03147400302397], 14); // Adjust coordinates for your starting position

// Add a base layer (MapTiler)
const key = 'emvkvAlKexCOOCAdiVE9';
L.tileLayer(`https://api.maptiler.com/tiles/cdf1b0ea-4162-4a6d-bbad-95d66f6163bd/{z}/{x}/{y}.png?key=${key}`, {
    tileSize: 512,
    zoomOffset: -1,
    minZoom: 14,
    attribution: '© <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>',
    crossOrigin: true
}).addTo(map);


// Initialize the feature group to store drawn layers
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Add Leaflet Draw control
const drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
    },
    draw: {
        polyline: false,
        polygon: true,
        circle: false,
        rectangle: false,
        marker: false,
    }
});
map.addControl(drawControl);

// Initialize the feature collection
let featureCollection = {
    type: "FeatureCollection",
    features: []
};

// Event listener for when a new feature is created
map.on('draw:created', function (event) {
    const layer = event.layer; // The drawn layer (marker, polygon, etc.)
    const geojsonData = layer.toGeoJSON(); // Convert the layer to GeoJSON

    // Add the drawn layer to the feature group
    drawnItems.addLayer(layer);

    // Add the GeoJSON data to the feature collection
    featureCollection.features.push(geojsonData);

    console.log("Current Feature Collection:", featureCollection);
});

// Handle the submit button click event
document.getElementById('submit-btn').addEventListener('click', function () {
    // Get the comment from the text box
    const comment = document.getElementById('comment-box').value.trim();
    
    if (featureCollection.features.length === 0) {
        alert("No data to submit! Please draw something on the map.");
        return;
    }
    
    if (!comment) {
        alert("Please enter a comment before submitting.");
        return;
    }

    // Attach the comment to each feature in the feature collection
    featureCollection.features.forEach(feature => {
        feature.properties = feature.properties || {};
        feature.properties.comment = comment; // Add the comment as a property
    });

    // Send the feature collection to the backend
    fetch('http://localhost:5000/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(featureCollection)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Submission response:", data);
        alert("Data submitted successfully!");

        // Clear the feature collection and comment box after submission
        featureCollection = {
            type: "FeatureCollection",
            features: []
        };
        document.getElementById('comment-box').value = ""; // Clear the text box
    })
    .catch(error => {
        console.error("Error during submission:", error);
        alert("An error occurred while submitting data.");
    });
});

