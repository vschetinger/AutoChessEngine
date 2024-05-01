import os
import json
import csv
from datetime import datetime

def extract_creature_statistics(json_file_path, experiment_hash, score_hash):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    creatures_stats = []

    for creature in data['header']['creatures']:
        creature_stats = {
            'experiment_hash': experiment_hash,
            'score_hash': score_hash,
            'replay_path': json_file_path,
            'creature_id': creature['id'],
            'creature_type': creature['name'].split(' ')[0],
            'speed': creature['speed'],
            'max_turn_rate': creature['max_turn_rate'],
            'damage': creature['damage'],
            'bullet_speed': creature['bullet_speed'],
            'shoot_cooldown': creature['shoot_cooldown'],
            'bullet_range': creature['bullet_range'],
            'score': creature['score'],
        }
        creatures_stats.append(creature_stats)

    return creatures_stats

def write_creatures_to_csv(folder_path):

    all_creatures_data = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json') and 'AutoChessSimulationRun' in file:
                experiment_hash = file.split('--')[2]
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                    score_hash = json.dumps(data['header']['score_values'], sort_keys=True)
                creatures_stats = extract_creature_statistics(os.path.join(root, file), experiment_hash, score_hash)
                all_creatures_data.extend(creatures_stats)

    # Create the "statistics/" folder if it doesn't exist
    os.makedirs('statistics', exist_ok=True)

    output_csv_path = f'statistics/creatures_statistics_{experiment_hash}.csv'
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['experiment_hash', 'score_hash', 'replay_path', 'creature_id', 'creature_type', 'speed', 'max_turn_rate', 'damage', 'bullet_speed', 'shoot_cooldown', 'bullet_range', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for creature_data in all_creatures_data:
            writer.writerow(creature_data)

folder_path = 'playbacks/'
write_creatures_to_csv(folder_path)