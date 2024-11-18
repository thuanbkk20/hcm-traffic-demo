import pandas as pd
import glob
import plotly.graph_objects as go

RESULTS_PATH = 'resources/drive/results.csv'
POINTS_PATH = 'resources/drive/points.txt'

def read_points_and_results():
    points = {}
    with open(POINTS_PATH, 'r') as file:
        for line in file:
            lat, lon, point_id = line.strip().split(',')
            points[int(point_id)] = (float(lat), float(lon))
    result = pd.read_csv(RESULTS_PATH)
    return points, result

def create_figure(fig):
    points, result = read_points_and_results()
    # Define the coordinates
    longitudes = []
    latitudes = []
    road_names = []
    traffics = []
    prev_destination = None

    for i, row in result.iterrows():
        origin = points[int(row['origin'])]
        if prev_destination is not None and prev_destination != origin:
            # Add the previous trace when a discontinuity is detected
            des_lat, des_lon = prev_destination
            longitudes.append(des_lon)
            latitudes.append(des_lat)
            add_trace(fig, longitudes, latitudes, road_names, traffics)
            # Reset lists for the new segment
            longitudes = []
            latitudes = []
            road_names = []
            traffics = []
        lat, lon = origin
        longitudes.append(lon)
        latitudes.append(lat)
        road_names.append(row['name'])
        traffics.append(row['traffic'])
        prev_destination = points[int(row['destination'])]
    
    # Add the last edge as a trace after the loop ends
    if longitudes and latitudes:
        des_lat, des_lon = prev_destination
        longitudes.append(des_lon)
        latitudes.append(des_lat)
        add_trace(fig, longitudes, latitudes, road_names, traffics)

def add_trace(fig, longitudes, latitudes, road_names, traffics):
    min_traffic, max_traffic = min(traffics), max(traffics)
    widths = [(((t - min_traffic) / min_traffic) + 1) * 2 for t in traffics]

    for i in range(len(longitudes) - 1):
        # Add the line
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[longitudes[i], longitudes[i + 1]],
            lat=[latitudes[i], latitudes[i + 1]],
            line={
                'color': 'blue',
                'width': widths[i]
            },
            hoverinfo='text',  # Ensure hover works
            hovertext=f"Road: {road_names[i]}<br>Traffic: {traffics[i]}",
            name=road_names[i]
        ))

        # Add a small marker at the midpoint for hover on the line
        mid_lon = (longitudes[i] + longitudes[i + 1]) / 2
        mid_lat = (latitudes[i] + latitudes[i + 1]) / 2
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[mid_lon],
            lat=[mid_lat],
            marker={
                'size': 2,  # Small marker
                'color': 'rgba(0,0,0,0)'  # Transparent marker
            },
            hoverinfo='text',
            hovertext=f"Road: {road_names[i]}<br>Traffic: {traffics[i]}",
            showlegend=False  # Hide marker legend
        ))

    # Add points separately to display coordinates on hover
    for i in range(len(longitudes)):
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[longitudes[i]],
            lat=[latitudes[i]],
            marker={'size': 7, 'color': 'blue'},
            hoverinfo='text',
            hovertext=f"Coords: ({latitudes[i]}, {longitudes[i]})",
            name="Point"
        ))

def add_traffic_layer(fig, points, traffic_data):
    print("Adding traffic layer")
    for route in traffic_data:
        print(f"route: {route}")
        source = points.get(route['source'])
        destination = points.get(route['destination'])
        flow = route['flow']

        if source and destination:
            source_lat, source_lon = source
            dest_lat, dest_lon = destination

            line_width = (flow / 1200) + 1

            fig.add_trace(go.Scattermapbox(
                mode="lines+markers",
                lon=[source_lon, dest_lon],
                lat=[source_lat, dest_lat],
                marker={
                    'size': 2,  # Small marker
                    'color': 'rgba(0,0,0,0)'  # Transparent marker
                },
                line={
                    'color': 'red',
                    'width': line_width
                },
                hoverinfo='text',
                hovertext=f"Flow: {flow}",
                name=f"Flow: {flow}"
            ))
