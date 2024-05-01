import os
import json
import csv
from datetime import datetime
import statistics

def extract_creature_statistics(game_data):
    creatures_stats = []
    winner = game_data['header']['winner']

    for creature in game_data['header']['creatures']:
        creature_stats = {
            'game_filename': game_data['filename'],
            'creature_id': creature['id'],
            'winner': 1 if creature['name'] == winner else 0,  # Update the logic here
            'creature_type': creature['name'].split(' ')[0],
            'speed': creature['speed'],
            'max_turn_rate': creature['max_turn_rate'],
            'damage': creature['damage'],
            'bullet_speed': creature['bullet_speed'],
            'shoot_cooldown': creature['shoot_cooldown'],
            'bullet_range': creature['bullet_range'],
            'score': creature['score'],
            'brake_cooldown': creature['brake_cooldown'],
            'brake_power': creature['brake_power'],
            'experiment_hash': game_data['experiment_hash']
        }
        creatures_stats.append(creature_stats)

    return creatures_stats

def extract_game_statistics(game_data):
    header = game_data['header']
    winner = header['winner']
    creatures_stats = extract_creature_statistics(game_data)
    total_score = sum(creature['score'] for creature in creatures_stats)
    num_creatures = len(creatures_stats)

    # Calculate average score per player
    avg_score_per_player = total_score / num_creatures

    # Get the winner's score directly from the game data
    winner_score = header['winner_score']

    # Find the maximum score among all creatures
    max_score = max(creature['score'] for creature in creatures_stats)

    return {
        'filename': game_data['filename'],
        'num_creatures': num_creatures,
        'total_score': total_score,
        'avg_score_per_player': avg_score_per_player,
        'winner': winner,
        'winner_score': winner_score,
        'max_turns': header['max_turns'],
        'max_score': max_score,
        'experiment_hash': game_data['experiment_hash']  # Add experiment_hash to game stats
    }

def extract_experiment_statistics(experiment_data, game_stats, creature_stats):
    experiment_config = experiment_data['experiment_config']
    experiment_hash = experiment_data['experiment_hash']
    
    score_values = experiment_data['score_values']
    score_values_str = ', '.join(f"{key}: {value}" for key, value in score_values.items())

    # Calculate percentage of games that did not end by maximum turns
    num_simulations = experiment_data['num_simulations']
    num_games_ended_by_time = sum(1 for game in game_stats if game['max_turns'] >= experiment_config['time_limit'])
    pct_games_not_ended_by_time = (num_simulations - num_games_ended_by_time) / num_simulations * 100
 

    # Calculate average score and standard deviation for all creatures in the experiment
    all_creature_scores = [creature['score'] for creature in creature_stats if creature['experiment_hash'] == experiment_hash]
    avg_score = statistics.mean(all_creature_scores)
    std_score = statistics.stdev(all_creature_scores)

    # Calculate average score and standard deviation for winning creatures in the experiment
    winner_scores = [game['winner_score'] for game in game_stats if game['experiment_hash'] == experiment_hash and game['winner_score'] is not None]
    if winner_scores:
        avg_winner_score = statistics.mean(winner_scores)
        std_winner_score = statistics.stdev(winner_scores)
    else:
        avg_winner_score = None
        std_winner_score = None

    # Calculate average and standard deviation for each creature attribute
    attribute_stats = {}
    for attribute in ['speed', 'max_turn_rate', 'damage', 'bullet_speed', 'shoot_cooldown', 'bullet_range', 'brake_cooldown', 'brake_power', 'health']:
        attribute_values = [creature[attribute] for creature in creature_stats if creature['experiment_hash'] == experiment_hash and attribute in creature]
        if attribute_values:
            attribute_stats[f'avg_{attribute}'] = statistics.mean(attribute_values)
            attribute_stats[f'std_{attribute}'] = statistics.stdev(attribute_values)
        else:
            attribute_stats[f'avg_{attribute}'] = None
            attribute_stats[f'std_{attribute}'] = None

    return {
        'experiment_hash': experiment_hash,
        'score_values': score_values_str,
        'num_simulations': num_simulations,
        'num_creatures': sum(experiment_config['num_creatures']),
        'creature_types': ', '.join(experiment_config['creature_types']),
        'time_limit': experiment_config['time_limit'],
        'arena_sizes': ', '.join(map(str, experiment_config['arena_sizes'])),
        'jitter_range': experiment_config['jitter_range'],
        'pct_games_not_ended_by_time': pct_games_not_ended_by_time,
        'avg_score': avg_score,
        'std_score': std_score,
        'avg_winner_score': avg_winner_score,
        'std_winner_score': std_winner_score,
        **attribute_stats
    }

def write_statistics_to_csv(creatures_stats, game_stats, experiment_stats):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the "statistics/" folder if it doesn't exist
    os.makedirs('statistics', exist_ok=True)

    # Write creature statistics to CSV
    creature_csv_path = f'statistics/creature_statistics_{timestamp}.csv'
    with open(creature_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['game_filename', 'creature_id','winner', 'creature_type', 'speed', 'max_turn_rate', 'damage', 'bullet_speed', 'shoot_cooldown', 'bullet_range', 'score', 'brake_cooldown', 'brake_power', 'experiment_hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(creatures_stats)

    # Write game statistics to CSV
    game_csv_path = f'statistics/game_statistics_{timestamp}.csv'
    with open(game_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['filename', 'num_creatures', 'total_score', 'avg_score_per_player', 'winner', 'winner_score', 'max_score', 'experiment_hash', 'max_turns'] 
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(game_stats)

       # Write experiment statistics to CSV
    experiment_csv_path = f'statistics/experiment_statistics_{timestamp}.csv'
    #TODO: fix health stats to be shown
    with open(experiment_csv_path, 'w', newline='') as csvfile:
        fieldnames = [
            'experiment_hash', 'score_values', 'num_simulations', 'num_creatures', 'creature_types',
            'time_limit', 'arena_sizes', 'jitter_range', 'pct_games_not_ended_by_time', 'avg_score',
            'std_score', 'avg_winner_score', 'std_winner_score', 'avg_speed', 'std_speed',
            'avg_max_turn_rate', 'std_max_turn_rate', 'avg_damage', 'std_damage', 'avg_bullet_speed',
            'std_bullet_speed', 'avg_shoot_cooldown', 'std_shoot_cooldown', 'avg_bullet_range',
            'std_bullet_range', 'avg_brake_cooldown', 'std_brake_cooldown', 'avg_brake_power',
            'std_brake_power', 'avg_health', 'std_health'  # Add 'avg_health' and 'std_health' to fieldnames
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(experiment_stats)

def extract_all_statistics():
    all_creatures_stats = []
    all_game_stats = []
    all_experiment_stats = []

    # Extract creature and game statistics from playback files
    for root, dirs, files in os.walk('playbacks'):
        for file in files:
            if file.endswith('.json') and 'AutoChessSimulationRun' in file:
                with open(os.path.join(root, file), 'r') as f:
                    game_data = json.load(f)
                    game_data['filename'] = file
                    all_creatures_stats.extend(extract_creature_statistics(game_data))
                    all_game_stats.append(extract_game_statistics(game_data))

    # Extract experiment statistics from experiment files
    for root, dirs, files in os.walk('experiments'):
        for file in files:
            if file.endswith('.json') and file.startswith('batch_output_'):
                with open(os.path.join(root, file), 'r') as f:
                    batch_data = json.load(f)
                    experiment_hash = batch_data['experiment_hash']
                    experiment_creatures_stats = [creature for creature in all_creatures_stats if creature['experiment_hash'] == experiment_hash]
                    experiment_game_stats = [game for game in all_game_stats if game['experiment_hash'] == experiment_hash]
                    experiment_stats = extract_experiment_statistics(batch_data, experiment_game_stats, experiment_creatures_stats)
                    all_experiment_stats.append(experiment_stats)

    # Write statistics to CSV files
    write_statistics_to_csv(all_creatures_stats, all_game_stats, all_experiment_stats)

if __name__ == "__main__":
    extract_all_statistics()