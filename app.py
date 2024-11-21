from flask import Flask, render_template, request, jsonify
import plotly.graph_objects as go
from plotly.io import to_json
import glob

from utils.graph_with_map import create_figure, read_points_and_results, add_traffic_layer
from resources.drive.dinicAlgorithm import get_dinic_result

app = Flask(__name__)

# Initial route to render the map
@app.route("/")
def home():
    fig = go.Figure()

    # Create the initial figure
    create_figure(fig)

    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        mapbox={
            'center': {'lon': 106.67879, 'lat': 10.80355},
            'style': "open-street-map",
            'zoom': 13
        })
    
    points, result = read_points_and_results()

    fig_json = to_json(fig)

    return render_template("index.html", fig_json=fig_json, points_json=points)

# POST route to handle flow data and update the map with the traffic layer
@app.route("/get_route", methods=["POST"])
def get_route():
    data = request.json
    points, result = read_points_and_results()
    origin = int(data.get("origin"))
    destination = int(data.get("destination"))

    print(f"{origin} -> {destination}")

    # Mock flow data based on the origin and destination points
    flow = get_dinic_result(origin, destination)


    if len(flow) > 0:
        # Create the figure and add traffic layer with the flow data
        fig = go.Figure()
        create_figure(fig)
        add_traffic_layer(fig, points, flow, origin, destination)  # Add the traffic layer with the mock flow data

        # Update layout for the map
        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox={
                'center': {'lon': 106.67879, 'lat': 10.80355},
                'style': "open-street-map",
                'zoom': 13
            })

        fig_json = to_json(fig)
        return jsonify({"route": flow, "fig_json": fig_json})  # Return the flow data and updated figure

    return jsonify({"error": "Invalid points"}), 400


if __name__ == "__main__":
    app.run(debug=True)
