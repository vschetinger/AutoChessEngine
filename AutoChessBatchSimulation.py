from datetime import datetime
import os
import json
import random
from AutoChessGameSimulation import initialize_game, generate_filename, calculate_lattice_position_with_jitter
from AutoChessEngine import Game, SimulationCreature, Arena, SimulationGame
import hashlib

def load_experiment_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def create_creature(creature_type, position, i, creature_config):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=creature_config[creature_type]['health'],
        speed=random.randint(*creature_config[creature_type]['speed_range']),
        name=f"{creature_type} {i}",
        max_turn_rate=random.randint(*creature_config[creature_type]['max_turn_rate_range']),
        shoot_cooldown=random.randint(*creature_config[creature_type]['shoot_cooldown_range']),
        bounding_box_size=tuple(creature_config[creature_type]['bounding_box_size']),
        damage=random.randint(*creature_config[creature_type]['damage_range']),
        bullet_speed=random.randint(*creature_config[creature_type]['bullet_speed_range']),
        bullet_range=random.randint(*creature_config[creature_type]['bullet_range_range']),
        brake_power=random.uniform(*creature_config[creature_type]['brake_power_range']),
        brake_cooldown=random.randint(*creature_config[creature_type]['brake_cooldown_range']),
        sprite_filename=creature_config[creature_type]['sprite_filename'],  
    )

class AutoChessBatchedSimulator:
    def __init__(self, experiment_config):
        self.experiment_config = experiment_config
        self.creature_types = experiment_config['creature_types']
        self.jitter_range = experiment_config['jitter_range']
        self.n = experiment_config['num_creatures']  # Assign self.n as a list
        self.game = None
        self.time_limit = experiment_config['time_limit']
        self.arena_sizes = experiment_config['arena_sizes']
        self.creature_config = experiment_config['creature_config']
        self.experiment_hash = self.generate_experiment_hash(experiment_config)

    def generate_experiment_hash(self, experiment_config):
        config_json = json.dumps(experiment_config, sort_keys=True)
        config_hash_object = hashlib.sha256(config_json.encode('utf-8'))
        config_hash = config_hash_object.hexdigest()[:6]  # Use the first 6 characters of the config hash

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Generate a timestamp with milliseconds
        timestamp_hash_object = hashlib.sha256(timestamp.encode('utf-8'))
        timestamp_hash = timestamp_hash_object.hexdigest()[:5]  # Use the first 5 characters of the timestamp hash

        combined_hash = f"{config_hash}.{timestamp_hash}"
        return combined_hash

    def initialize_game(self):
        arena_size = random.choice(self.arena_sizes)
        arena = Arena(width=arena_size, height=arena_size)

        game = SimulationGame(arena, [], experiment_hash=self.experiment_hash)
        Game.reset_time()
        creatures = []
        creature_counts = {creature_type: 0 for creature_type in self.creature_types}

        for creature_type, count in zip(self.creature_types, self.n):
            for i in range(count):
                creature = create_creature(creature_type, calculate_lattice_position_with_jitter(arena, sum(self.n), len(creatures), jitter_range=self.jitter_range), len(creatures), self.creature_config)
                creatures.append(creature)
                game.add_game_object(creature)
                creature_counts[creature_type] += 1

        game.creature_counts = creature_counts
        return game

    def run_simulation(self, simulation_number):
        self.game = self.initialize_game()
        while True:
            self.game.simulate_turn()
            alive_creatures = [creature for creature in self.game.game_objects if isinstance(creature, SimulationCreature) and creature.health > 0]
            if len(alive_creatures) == 1:
                self.game.winner = alive_creatures[0].name
                break
            if Game.get_time() >= self.time_limit:
                creatures_by_score = sorted(self.game.game_objects, key=lambda creature: creature.score if isinstance(creature, SimulationCreature) else float('-inf'), reverse=True)
                self.game.winner = creatures_by_score[0].name if creatures_by_score else None
                break

        filename = generate_batch_filename(self.game.creature_counts, self.experiment_hash, simulation_number)
        self.game.record_game(f"playbacks/{filename}")
        print(f"Simulation saved to playbacks/{filename}")



    def run_batch_simulations(self, num_simulations):
        for i in range(num_simulations):
            print(f"Running simulation {i + 1} of {num_simulations}")
            self.run_simulation(i + 1)

    def save_batch_output(self, output_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a timestamp
        batch_output = {
            'experiment_config': self.experiment_config,
            'experiment_hash': self.experiment_hash,
            'score_values': self.game.score_values,
            'num_simulations': self.experiment_config['num_simulations']
        }
        output_path = os.path.join("experiments", f"{output_file}_{timestamp}.json")  # Include timestamp in the file name
        with open(output_path, 'w') as file:
            json.dump(batch_output, file, indent=4)


def generate_batch_filename(creature_counts, experiment_hash, simulation_number):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a timestamp
    game_hash = f"{experiment_hash}_{simulation_number}"
    return f"AutoChessSimulationRun--{timestamp}--{game_hash}.json"  # Include timestamp in the file name

if __name__ == "__main__":
    experiment_config_file = 'experiment_config.json'
    experiment_config = load_experiment_config(experiment_config_file)

    simulator = AutoChessBatchedSimulator(experiment_config)
    simulator.run_batch_simulations(experiment_config['num_simulations'])

    batch_output_file = "batch_output"  # Remove the experiment hash from the file name
    simulator.save_batch_output(batch_output_file)
    print(f"Batch output saved to experiments/{batch_output_file}_<timestamp>.json")