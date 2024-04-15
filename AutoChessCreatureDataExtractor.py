import os
import json
import csv

def get_filename_without_extension(file_path):
    # Extract the base name (file name with extension)
    base_name = os.path.basename(file_path)
    # Remove the extension
    filename_without_extension = os.path.splitext(base_name)[0]
    # Check if the filename starts with the specified prefix and remove it
    #if filename_without_extension.startswith('AutoChessSimulationRun--'):
    #    filename_without_extension = filename_without_extension[len('AutoChessSimulationRun--'):]
    return filename_without_extension

def extract_creature_statistics(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    header = data['header']
    winner = header['winner']
    arena_size = header['arena']['width'] # or height, since they are the same
    turns = max(map(int, data['events'].keys())) if data['events'] else 0

    creatures_stats = []
    
    for creature in header['creatures']:
        creature_type = 'unknown'
        if "Sniper" in creature['name']:
            creature_type = 'sniper'
        elif "Machine_Gun" in creature['name']:
            creature_type = 'machine_gun'
        elif "Mine_Layer" in creature['name']:
            creature_type = 'mine_layer'
        # Determine if the creature was the winner
        is_winner = 1 if winner in creature['name'] else 0

        creature_stats = {
            'type': creature_type,
            'speed': creature['speed'],
            'max_turn_rate': creature['max_turn_rate'],
            'damage': creature['damage'],
            'bullet_speed': creature['bullet_speed'],
            'shoot_cooldown': creature['shoot_cooldown'],
            'bullet_range': creature['bullet_range'],
            'score': creature['score'], 
            'winner': is_winner,
            'arena_size': arena_size,
            'max_turns': turns + 1, # Adding 1 because turn indexing starts at 0
            # 'replay_path': json_file_path # Adding the replay path
            'replay_path': get_filename_without_extension(json_file_path)
        }
        creatures_stats.append(creature_stats)

    return creatures_stats

def write_creatures_to_csv(folder_path, output_csv_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    all_creatures_data = []
    for file in files:
        creatures_stats = extract_creature_statistics(os.path.join(folder_path, file))
        all_creatures_data.extend(creatures_stats)

    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['type', 'speed', 'max_turn_rate', 'damage', 'bullet_speed', 'shoot_cooldown', 'bullet_range','score', 'winner', 'arena_size', 'max_turns', 'replay_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        writer.writeheader()
        for creature_data in all_creatures_data:
            writer.writerow(creature_data)

folder_path = 'playbacks/'
output_csv_path = 'creatures_statistics.csv'
write_creatures_to_csv(folder_path, output_csv_path)