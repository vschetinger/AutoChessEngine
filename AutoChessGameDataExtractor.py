import os
import json
import csv
from datetime import datetime

def extract_game_statistics(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    header = data['header']
    creatures = header['creatures']
    winner = header['winner']
    total_score = sum(creature['score'] for creature in creatures)
    num_creatures = len(creatures)

    hash_value = os.path.basename(json_file_path).split('--')[2]

    # Calculate average score per player
    avg_score_per_player = total_score / num_creatures

    # Find the score of the winner
    winner_score = next((creature['score'] for creature in creatures if creature['name'] == winner), None)

    # Find the maximum score among all creatures
    max_score = max(creature['score'] for creature in creatures)

    return {
        'filename': os.path.basename(json_file_path),
        'hash': hash_value,
        'num_creatures': num_creatures,
        'total_score': total_score,
        'avg_score_per_player': avg_score_per_player,
        'winner': winner,
        'winner_score': winner_score,
        'max_score': max_score
    }

def write_game_statistics_to_csv(folder_path):
    game_stats = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json') and 'AutoChessSimulationRun' in file:
                json_file_path = os.path.join(root, file)
                game_data = extract_game_statistics(json_file_path)
                game_stats.append(game_data)

    # Create the "statistics/" folder if it doesn't exist
    os.makedirs('statistics', exist_ok=True)

    if game_stats:
        # Use the hash from the first game in the list
        hash_value = game_stats[0]['hash']
        output_csv_path = f'statistics/game_statistics_{hash_value}.csv'
        with open(output_csv_path, 'w', newline='') as csvfile:
            fieldnames = ['filename', 'num_creatures', 'total_score', 'avg_score_per_player', 'winner', 'winner_score', 'max_score', 'hash']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for game_data in game_stats:
                writer.writerow(game_data)
        print(f"Game statistics saved to {output_csv_path}")
    else:
        print("No game data found.")

folder_path = 'playbacks/'
write_game_statistics_to_csv(folder_path)