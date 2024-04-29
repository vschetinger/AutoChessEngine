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
        self.n = experiment_config['num_creatures']
        self.game = None
        self.time_limit = experiment_config['time_limit']
        self.arena_sizes = experiment_config['arena_sizes']
        self.creature_config = experiment_config['creature_config']
        self.experiment_hash = self.generate_experiment_hash(experiment_config)

    def generate_experiment_hash(self, experiment_config):
        config_json = json.dumps(experiment_config, sort_keys=True)
        hash_object = hashlib.sha256(config_json.encode('utf-8'))
        return hash_object.hexdigest()

    def initialize_game(self):
        arena_size = random.choice(self.arena_sizes)
        arena = Arena(width=arena_size, height=arena_size)

        game = SimulationGame(arena, [])
        Game.reset_time()
        creatures = []
        creature_counts = {creature_type: 0 for creature_type in self.creature_types}

        for i in range(self.n):
            creature_type = random.choice(self.creature_types)
            creature = create_creature(creature_type, calculate_lattice_position_with_jitter(arena, self.n, i, jitter_range=self.jitter_range), i, self.creature_config)
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
            if Game.get_time() >= self.time_limit or len(alive_creatures) == 0:
                if alive_creatures:
                    creatures_by_score = sorted(alive_creatures, key=lambda creature: creature.score, reverse=True)
                    self.game.winner = creatures_by_score[0].name
                else:
                    self.game.winner = "Draw"
                break

        filename = generate_batch_filename(self.game.creature_counts, self.experiment_hash, simulation_number)
        self.game.record_game(f"playbacks/{filename}")
        print(f"Simulation saved to playbacks/{filename}")



    def run_batch_simulations(self, num_simulations):
        for i in range(num_simulations):
            print(f"Running simulation {i + 1} of {num_simulations}")
            self.run_simulation(i + 1)

    def save_batch_output(self, output_file):
        batch_output = {
            'experiment_config': self.experiment_config,
            'experiment_hash': self.experiment_hash
        }
        output_path = os.path.join("playbacks", output_file)
        with open(output_path, 'w') as file:
            json.dump(batch_output, file, indent=4)


def generate_batch_filename(creature_counts, experiment_hash, simulation_number):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    creature_counts_str = "_".join(f"{creature_type}_{count}" for creature_type, count in creature_counts.items())
    game_hash = f"{experiment_hash}_{simulation_number}"
    return f"AutoChessSimulationRun--{timestamp}--{game_hash}--{creature_counts_str}.json"

if __name__ == "__main__":
    experiment_config_file = 'experiment_config.json'
    experiment_config = load_experiment_config(experiment_config_file)

    simulator = AutoChessBatchedSimulator(experiment_config)
    simulator.run_batch_simulations(experiment_config['num_simulations'])

    batch_output_file = f"batch_output_{simulator.experiment_hash}.json"
    simulator.save_batch_output(batch_output_file)
    print(f"Batch output saved to playbacks/{batch_output_file}")