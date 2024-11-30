from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import geopandas as gpd
from shapely.geometry import shape
import os
import pandas as pd
import sqlite3
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Path to store data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SUBMISSIONS_FILE = os.path.join(DATA_DIR, 'submissions.geojson')
PROCESSED_FILE = os.path.join(DATA_DIR, 'processed_data.geojson')
MBTILES_FILE = os.path.join(DATA_DIR, "ChelseaMentalMap_v4.mbtiles")  # Path to MBTiles file


# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/<int:z>/<int:x>/<int:y>.png')
def serve_tile(z, x, y):
    try:
        conn = sqlite3.connect(MBTILES_FILE)
        cursor = conn.cursor()
        query = f"""
            SELECT tile_data FROM tiles 
            WHERE zoom_level = {z} 
              AND tile_column = {x} 
              AND tile_row = {(2 ** z - 1) - y}  -- Flip Y-coordinate if needed
        """
        cursor.execute(query)
        tile_data = cursor.fetchone()
        conn.close()

        if tile_data:
            # Wrap the bytes data in a BytesIO object
            tile_stream = BytesIO(tile_data[0])
            return send_file(tile_stream, mimetype="image/png")
        else:
            return "Tile not found", 404
    except Exception as e:
        return f"Error serving tile: {str(e)}", 500


# Route to receive user-drawn features
"""
Submits GeoJSON data and saves it to a GeoJSON file.
This function handles POST requests to the '/submit' endpoint, processes the incoming GeoJSON data, and appends it to an existing GeoJSON file if it exists. It returns a success message or an error response based on the outcome of the operation.
Args:
    None
Returns:
    flask.Response: A JSON response indicating success or error.
Raises:
    Exception: If an error occurs during data processing or file operations.
Examples:
    >>> response = submit_data()
    >>> response.status_code
    200
"""
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        # Get GeoJSON from the POST request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Convert GeoJSON to a GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")

        # Save to GeoJSON file (append mode)
        if os.path.exists(SUBMISSIONS_FILE):
            existing_gdf = gpd.read_file(SUBMISSIONS_FILE)
            gdf = gpd.GeoDataFrame(pd.concat([existing_gdf, gdf], ignore_index=True))

        gdf.to_file(SUBMISSIONS_FILE, driver="GeoJSON")

        return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to process data (example: clean geometries)
@app.route('/process', methods=['POST'])
def process_data():
    try:
        # Read submitted data
        if not os.path.exists(SUBMISSIONS_FILE):
            return jsonify({"error": "No submissions found"}), 400

        gdf = gpd.read_file(SUBMISSIONS_FILE)

        # Example processing: fix invalid geometries
        gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.buffer(0) if geom.is_valid else geom)

        # Save processed data
        gdf.to_file(PROCESSED_FILE, driver="GeoJSON")

        return jsonify({"message": "Data processed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
