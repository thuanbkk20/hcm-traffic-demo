import json
import flexpolyline as fp
import pandas as pd

from calculate_distance import haversine
import glob

# Load JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_to_txt(data, file_path='resources/finally/points.txt'):
    with open(file_path, 'w') as file:
        for item in data:
            file.write(f"{item}\n")

LOCALTIONS = [
    "bayhien_sanbay",
    "hangxanh_bayhien",
    "sanbay_hangxanh",
    
    "phunhuan_sanbay",
    "vtsau2batrung_phunhuan",
    
    "danchu_hangxanh",
    "danchu_bayhien",
    "danchu_sanbay",
    "danchu_phunhuan",

    "phunhuan_dienbienphu",
    "vtsau2batrung_danchu"
]

cur_point_idx = 0
points_map = {}
points_to_txt = []

for location in LOCALTIONS:
    # Example usage
    file_path = f'resources/routes/{location}.json'
    json_data = load_json(file_path)
    json_data = json_data["routes"][0]['sections']
    if len(json_data) == 0:
        json_data = json_data[0]
    else:
        for item in json_data:
            if item['type'] == 'vehicle':
                json_data = item
                break
    
    points = fp.decode(json_data['polyline'])
    ordered_points = json_data['turnByTurnActions']
    
    results = []
    
    for i in range(len(ordered_points)-1):
        offset = ordered_points[i]['offset']
        next_offset = ordered_points[i+1]['offset']

        if points[offset] not in points_map:
            points_map[points[offset]] = cur_point_idx
            points_to_txt.append(f"{points[offset][0]},{points[offset][1]},{cur_point_idx}")
            cur_point_idx += 1
        
        if points[next_offset] not in points_map:
            points_map[points[next_offset]] = cur_point_idx
            points_to_txt.append(f"{points[next_offset][0]},{points[next_offset][1]},{cur_point_idx}")
            cur_point_idx += 1
        
        origin_idx = points_map[points[offset]]
        destination_idx = points_map[points[next_offset]]

        results.append({
            # 'origin': points[turns[i]['offset']],
            # 'destination': points[turns[i+1]['offset']],
            'origin': origin_idx,
            'destination': destination_idx,
            'distance': haversine(points[offset], points[next_offset]),
            'name': ordered_points[i]['currentRoad']['name'][1]['value'] if 'currentRoad' in ordered_points[i] else ordered_points[i]['nextRoad']['name'][1]['value'],
            'traffic': 1
        })

    last_offset = ordered_points[-1]['offset']
    if points[last_offset] not in points_map:
        points_map[points[last_offset]] = cur_point_idx
        points_to_txt.append(f"{points[last_offset][0]},{points[last_offset][1]},{cur_point_idx}")
        cur_point_idx += 1
            
    # Convert the distance and attributes list to a DataFrame
    distance_df = pd.DataFrame(results)
    distance_df.to_csv(f'resources/results/{location}.csv', index=False, encoding='utf-8')
    print(f"Results saved to resources/results/{location}.csv")

    # Write points to txt file
    write_to_txt(points_to_txt)

# Merge all result.txt files into one
def merge_results_files(output_path='resources/finally'):
    csv_files = glob.glob('resources/results/*.csv')
    data_list = [pd.read_csv(file) for file in csv_files]
    data = pd.concat(data_list, ignore_index=True)
    data.to_csv(f'{output_path}/results.csv', index=False, encoding='utf-8')

merge_results_files()
