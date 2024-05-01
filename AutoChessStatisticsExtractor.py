import os
import json
import csv
from datetime import datetime
import numpy as np

def extract_experiment_statistics(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    experiment_config = data['experiment_config']
    experiment_hash = data['experiment_hash']
    
    score_values = data['score_values']
    score_values_str = ', '.join(f"{key}: {value}" for key, value in score_values.items())

    # Calculate percentage of games that did not end by maximum turns
    num_simulations = data['num_simulations']
    num_games_ended_by_time = sum(1 for file in os.listdir('playbacks') if file.startswith(f"AutoChessSimulationRun--{experiment_hash}") and "time_limit_reached" in file)
    pct_games_not_ended_by_time = (num_simulations - num_games_ended_by_time) / num_simulations * 100

    # Calculate average score and standard deviation for all creatures in the experiment
    all_creature_scores = []
    winner_max_scores = []

    for file in os.listdir('playbacks'):
        if file.startswith(f"AutoChessSimulationRun--{experiment_hash}"):
            with open(os.path.join('playbacks', file), 'r') as playback_file:
                playback_data = json.load(playback_file)
                creatures = playback_data['header']['creatures']
                all_creature_scores.extend(float(creature['score']) for creature in creatures)

                winner_name = playback_data['header']['winner']
                winner_creature = next((creature for creature in creatures if creature['name'].startswith(winner_name)), None)
                if winner_creature:
                    winner_max_scores.append(float(winner_creature['score']))

    avg_score = np.mean(all_creature_scores) if all_creature_scores else 0.0
    std_score = np.std(all_creature_scores) if all_creature_scores else 0.0
    avg_winner_score = np.mean(winner_max_scores) if winner_max_scores else 0.0
    std_winner_score = np.std(winner_max_scores) if winner_max_scores else 0.0

    return {
        'experiment_hash': experiment_hash,
        'score_values': score_values_str,
        'num_simulations': num_simulations,
        'num_creatures': sum(experiment_config['num_creatures']),
        'creature_types': ', '.join(experiment_config['creature_types']),
        'arena_sizes': ', '.join(map(str, experiment_config['arena_sizes'])),
        'time_limit': experiment_config['time_limit'],
        'pct_games_not_ended_by_time': pct_games_not_ended_by_time,
        'avg_score': avg_score,
        'std_score': std_score,
        'avg_winner_score': avg_winner_score,
        'std_winner_score': std_winner_score
    }

def write_experiment_statistics_to_csv(folder_path):
    experiments_data = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json') and file.startswith('batch_output_'):
                experiment_stats = extract_experiment_statistics(os.path.join(root, file))
                experiments_data.append(experiment_stats)

    # Create the "statistics/" folder if it doesn't exist
    os.makedirs('statistics', exist_ok=True)

    # Use the experiment hash from the first experiment in the list
    if experiments_data:
        experiment_hash = experiments_data[0]['experiment_hash']
        output_csv_path = f'statistics/experiment_statistics_{experiment_hash}.csv'
        with open(output_csv_path, 'w', newline='') as csvfile:
            fieldnames = ['experiment_hash', 'score_values', 'num_simulations', 'num_creatures', 'creature_types', 'arena_sizes', 'time_limit', 'pct_games_not_ended_by_time', 'avg_score', 'std_score', 'avg_winner_score', 'std_winner_score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for experiment_data in experiments_data:
                writer.writerow(experiment_data)
    else:
        print("No experiment data found.")

def extract_all_statistics(folder_path):
    creature_data_extractor_path = 'AutoChessCreatureDataExtractor.py'
    game_data_extractor_path = 'AutoChessGameDataExtractor.py'

    # Run the creature data extractor
    os.system(f'python {creature_data_extractor_path}')

    # Run the game data extractor
    os.system(f'python {game_data_extractor_path}')

    # Run the experiment statistics extractor
    write_experiment_statistics_to_csv(folder_path)

folder_path = 'experiments/'
extract_all_statistics(folder_path)