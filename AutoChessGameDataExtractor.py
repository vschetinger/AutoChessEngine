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

def extract_game_statistics(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    header = data['header']
    raw_winner = header['winner']
    # Determine the winner's type
    if "Sniper" in raw_winner:
        winner_type = 'sniper'
    elif "Machine_Gun" in raw_winner:
        winner_type = 'machine_gun'
    elif "Mine_Layer" in raw_winner:
        winner_type = 'mine_layer'
    else:
        winner_type = 'draw'  # Assumes draw if the winner's name does not match expected types

    creatures_count = {'Sniper': 0, 'Machine_Gun': 0, 'Mine_Layer': 0}
    for creature in header['creatures']:
        if "Sniper" in creature['name']:
            creatures_count['Sniper'] += 1
        elif "Machine_Gun" in creature['name']:
            creatures_count['Machine_Gun'] += 1
        elif "Mine_Layer" in creature['name']:
            creatures_count['Mine_Layer'] += 1

    arena_size = header['arena']['width']  # or height, since they are the same
    turns = max(map(int, data['events'].keys())) if data['events'] else 0

    # Find the high score of the winner
    high_score = 0
    for creature in header['creatures']:
        if raw_winner in creature['name']:
            high_score = creature['score']
            break

    return {
        'winner_type': winner_type,
        'winner': raw_winner,
        'turns': turns + 1,  # Adding 1 because turn indexing starts at 0
        'snipers': creatures_count['Sniper'],
        'machine_guns': creatures_count['Machine_Gun'],
        'mine_layers': creatures_count['Mine_Layer'],
        'arena_size': arena_size,
        'high_score': high_score,  # Add the high score field
        'replay_path': get_filename_without_extension(json_file_path)
    }


def write_statistics_to_csv(folder_path, output_csv_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    games_data = []

    for file in files:
        file_path = os.path.join(folder_path, file)
        game_stats = extract_game_statistics(file_path)
        games_data.append(game_stats)

    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['winner_type', 'winner', 'turns', 'snipers', 'machine_guns', 'mine_layers', 'arena_size', 'high_score', 'replay_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for game_data in games_data:
            writer.writerow(game_data)


# Example usage
folder_path = 'playbacks/'
output_csv_path = 'game_statistics.csv'
write_statistics_to_csv(folder_path, output_csv_path)
