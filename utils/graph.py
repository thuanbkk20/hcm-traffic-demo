import networkx as nx
import pandas as pd
import glob
import plotly.graph_objects as go

# Merge multiple CSV files
csv_files = glob.glob('resources/results/*.csv')
data_list = [pd.read_csv(file) for file in csv_files]
data = pd.concat(data_list, ignore_index=True)

# Create a graph, Add edges to the graph based on the CSV data
G = nx.Graph()
for i, row in data.iterrows():
    origin = tuple(map(float, row['origin'].strip("()").split(",")))  
    destination = tuple(map(float, row['destination'].strip("()").split(","))) 
    distance = row['distance']
    road_name = row['name']
    traffic = row['traffic']
    G.add_edge(origin, destination, distance=distance, road_name=road_name, traffic=traffic)

pos = {node: (node[1], node[0]) for node in G.nodes()} 

# Normalize traffic data to scale edge widths
traffic_values = [G[u][v]['traffic'] for u, v in G.edges()]
min_traffic, max_traffic = min(traffic_values), max(traffic_values)
scaled_traffic = [(t - min_traffic) / (max_traffic - 0) * 2 + 0.5 for t in traffic_values]  # Scale between 0.5 and 5

# Set custom line widths for edges by adding separate edge traces
edge_traces = []
for (u, v), width in zip(G.edges(), scaled_traffic):
    edge_trace = go.Scatter(
        x=[pos[u][0], pos[v][0]],
        y=[pos[u][1], pos[v][1]],
        line=dict(width=width, color='#888'),
        mode='lines',
        hoverinfo='none'
    )
    edge_traces.append(edge_trace)

# Create a node trace
node_x = []
node_y = []
edge_labels = [d['road_name'] for _, _, d in G.edges(data=True)]
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x = node_x, 
    y = node_y,
    mode = 'markers',
    text = edge_labels,
    textposition = "top center",
    marker = dict( size = 5,color = 'blue', line_width = 2),
    hoverinfo = 'text'
)

fig = go.Figure(
    data = edge_traces + [node_trace],
    layout = go.Layout (
        title = "Interactive Graph of Locations with Traffic-Based Edge Width",
        titlefont_size = 16,
        showlegend = False,
        hovermode = 'closest',
        margin = dict(b=0, l=0, r=0, t=40),
        xaxis = dict(showgrid = False, zeroline = False),
        yaxis = dict(showgrid = False, zeroline = False)
    )
)

fig.show()

