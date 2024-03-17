import os
import json
from AutoChessGameSimulation import initialize_game, generate_filename,calculate_lattice_position_with_jitter
from AutoChessEngine  import Game, SimulationCreature, Arena, SimulationGame
import random

def get_sniper_creature_b(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Sniper {i}",
        max_turn_rate=random.randint(8, 16),
        shoot_cooldown=random.randint(15, 30),
        bounding_box_size=(50, 100),
        damage=random.randint(50, 150), # Sniper damage range
        bullet_speed=random.randint(50, 100), # Sniper bullet speed range
        bullet_range=random.randint(500, 900), # Sniper bullet range
    )

def get_machine_gun_creature_b(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Machine_Gun {i}",
        max_turn_rate=random.randint(5, 15),
        shoot_cooldown=random.randint(2, 5),
        bounding_box_size=(50, 100),
        damage=random.randint(15, 25), # Machine Gun damage range
        bullet_speed=random.randint(10, 50), # Machine Gun bullet speed range
        bullet_range=random.randint(200, 500), # Machine Gun bullet range
    )

def get_mine_laying_creature_b(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Mine_Layer {i}",
        max_turn_rate=random.randint(1, 8),
        shoot_cooldown=random.randint(5, 30),
        bounding_box_size=(50, 100),
        damage=random.randint(80, 120), # Mine Layer damage range
        bullet_speed=0,
        bullet_range=random.randint(500, 700), # Mine Layer bullet range
    )

class AutoChessBatchedSimulator:
    def __init__(self, arena, creature_types,n,time_limit, jitter_range=150):
        self.arena = arena
        self.creature_types = creature_types
        self.jitter_range = jitter_range
        self.n = n # Number of creatures
        self.game = None
        self.time_limit = time_limit



    def initialize_game(self):
        game = SimulationGame(self.arena, [])
        Game.reset_time()
        creatures = []
        # Initialize a dictionary to keep track of creature counts
        creature_counts = {
            'S': 0,
            'ML': 0,
            'MG': 0
            # Add more creature types and their counts as needed
        }
        for i in range(self.n):
            creature_type = random.choice(self.creature_types)
            creature = creature_type(calculate_lattice_position_with_jitter(self.arena, self.n, i, jitter_range=self.jitter_range),i)
            creatures.append(creature)
            game.add_game_object(creature) # Add the creature to the game
            
            # Update the creature counts based on the creature type
            if creature_type == get_sniper_creature_b:
                creature_counts['S'] += 1
            elif creature_type == get_machine_gun_creature_b:
                creature_counts['MG'] += 1
            elif creature_type == get_mine_laying_creature_b:
                creature_counts['ML'] += 1

        game.creature_counts = creature_counts
        return game

    # Function to run a single simulation and save the results
    def run_simulation(self):
        self.game = self.initialize_game()
        while True:
            self.game.simulate_turn()
            alive_creatures = [creature for creature in self.game.game_objects if isinstance(creature, SimulationCreature) and creature.health > 0]
            if len(alive_creatures) == 1:
                self.game.winner = alive_creatures[0].name
                break
            if Game.get_time() >= self.time_limit or len(alive_creatures) == 0:
                self.game.winner = "Draw"
                break

        # Generate the filename based on the simulation parameters
        filename = generate_filename(self.game.creature_counts)

        # Save the simulation record with the generated filename
        self.game.record_game(f"playbacks/{filename}")
        print(f"Simulation saved to playbacks/{filename}")

    # Function to run multiple simulations
    def run_batch_simulations(self, num_simulations):
        for i in range(num_simulations):
            print(f"Running simulation {i + 1} of {num_simulations}")
            self.run_simulation()

# Call the function to run the batch of simulations
if __name__ == "__main__":
    num_simulations = 20 # Set the number of simulations you want to run  
    creature_types = [get_sniper_creature_b, get_machine_gun_creature_b, get_mine_laying_creature_b]
    arena = Arena(width=2000, height=2000) # Create an arena object with desired width and height
    
    simulator = AutoChessBatchedSimulator(arena, creature_types,4,1000) # Instantiate AutoChessBatchedSimulator object
    simulator.run_batch_simulations(num_simulations) # Run the batch of simulations
   
