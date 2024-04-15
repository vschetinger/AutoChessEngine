import os
import json
from AutoChessGameSimulation import initialize_game, generate_filename,calculate_lattice_position_with_jitter
from AutoChessEngine  import Game, SimulationCreature, Arena, SimulationGame
import random

# def get_sniper_creature_b(position, i):
#     return SimulationCreature(
#         position=position,
#         angle=random.randint(0, 360),
#         health=100,
#         speed=random.randint(5, 40),
#         name=f"Sniper {i}",
#         max_turn_rate=random.randint(8, 16),
#         shoot_cooldown=random.randint(15, 30),
#         bounding_box_size=(50, 100),
#         damage=random.randint(50, 150), # Sniper damage range
#         bullet_speed=random.randint(50, 100), # Sniper bullet speed range
#         bullet_range=random.randint(500, 900), # Sniper bullet range
#     )

# def get_machine_gun_creature_b(position, i):
#     return SimulationCreature(
#         position=position,
#         angle=random.randint(0, 360),
#         health=100,
#         speed=random.randint(5, 40),
#         name=f"Machine_Gun {i}",
#         max_turn_rate=random.randint(5, 15),
#         shoot_cooldown=random.randint(2, 5),
#         bounding_box_size=(50, 100),
#         damage=random.randint(15, 25), # Machine Gun damage range
#         bullet_speed=random.randint(10, 50), # Machine Gun bullet speed range
#         bullet_range=random.randint(200, 500), # Machine Gun bullet range
#     )

# def get_mine_laying_creature_b(position, i):
#     return SimulationCreature(
#         position=position,
#         angle=random.randint(0, 360),
#         health=100,
#         speed=random.randint(4, 30),
#         name=f"Mine_Layer {i}",
#         max_turn_rate=random.randint(1, 8),
#         shoot_cooldown=random.randint(5, 30),
#         bounding_box_size=(50, 100),
#         damage=random.randint(20, 40), # Mine Layer damage range
#         bullet_speed=0,
#         bullet_range=random.randint(500, 700), # Mine Layer bullet range
#     )



def get_sniper_creature_b(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Sniper {i}",
        max_turn_rate=random.randint(5, 20),
        shoot_cooldown=random.randint(15, 50),
        bounding_box_size=(50, 100),
        damage=random.randint(40, 140), # Sniper damage range
        bullet_speed=random.randint(40, 100), # Sniper bullet speed range
        bullet_range=random.randint(400, 1200), # Sniper bullet range
    )

def get_machine_gun_creature_b(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(10, 75),
        name=f"Machine_Gun {i}",
        max_turn_rate=random.randint(1, 30),
        shoot_cooldown=random.randint(1, 10),
        bounding_box_size=(50, 100),
        damage=random.randint(5, 50), # Machine Gun damage range
        bullet_speed=random.randint(10, 80), # Machine Gun bullet speed range
        bullet_range=random.randint(50, 800), # Machine Gun bullet range
        brake_power=random.uniform(0.5, 0.9),  # Adjust the range as needed
        brake_cooldown=random.randint(50, 100),  # Adjust the range as needed
    )

def get_mine_laying_creature_b(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(4, 40),
        name=f"Mine_Layer {i}",
        max_turn_rate=random.randint(1, 15),
        shoot_cooldown=random.randint(5, 30),
        bounding_box_size=(50, 100),
        damage=random.randint(15, 60), # Mine Layer damage range
        bullet_speed=0,
        bullet_range=random.randint(400, 800), # Mine Layer bullet range
    )

class AutoChessBatchedSimulator:
    def __init__(self, arena_sizes, creature_types,n,time_limit, jitter_range=150):
        self.creature_types = creature_types
        self.jitter_range = jitter_range
        self.n = n # Number of creatures
        self.game = None
        self.time_limit = time_limit
        self.arena_sizes = arena_sizes # List of arena sizes

class AutoChessBatchedSimulator:
    def __init__(self, arena_sizes, creature_types,n,time_limit, jitter_range=150):
        self.creature_types = creature_types
        self.jitter_range = jitter_range
        self.n = n # Number of creatures
        self.game = None
        self.time_limit = time_limit
        self.arena_sizes = arena_sizes # List of arena sizes


    def initialize_balanced(self):
        # Randomly select an arena size from the list
        arena_size = random.choice(self.arena_sizes)
        arena = Arena(width=arena_size, height=arena_size) # Assuming the width and height are the same

        game = SimulationGame(arena, [])
        Game.reset_time()
        creatures = []
        # Initialize a dictionary to keep track of creature counts
        creature_counts = {
            'S': 0,
            'ML': 0,
            'MG': 0
            # Add more creature types and their counts as needed
        }
        
        # Calculate the number of each creature type to add
        num_creatures_per_type = self.n // len(self.creature_types)
        remaining_creatures = self.n % len(self.creature_types)
        
        for creature_type in self.creature_types:
            for i in range(num_creatures_per_type):
                creature = creature_type(calculate_lattice_position_with_jitter(arena, self.n, i, jitter_range=self.jitter_range), i)
                creatures.append(creature)
                game.add_game_object(creature) # Add the creature to the game
                
                # Update the creature counts based on the creature type
                if creature_type == get_sniper_creature_b:
                    creature_counts['S'] += 1
                elif creature_type == get_machine_gun_creature_b:
                    creature_counts['MG'] += 1
                elif creature_type == get_mine_laying_creature_b:
                    creature_counts['ML'] += 1
            
            # Distribute the remaining creatures evenly among the types
            if remaining_creatures > 0:
                creature = creature_type(calculate_lattice_position_with_jitter(arena, self.n, i, jitter_range=self.jitter_range), i)
                creatures.append(creature)
                game.add_game_object(creature) # Add the creature to the game
                
                # Update the creature counts based on the creature type
                if creature_type == get_sniper_creature_b:
                    creature_counts['S'] += 1
                elif creature_type == get_machine_gun_creature_b:
                    creature_counts['MG'] += 1
                elif creature_type == get_mine_laying_creature_b:
                    creature_counts['ML'] += 1
                remaining_creatures -= 1

        game.creature_counts = creature_counts
        return game

    def initialize_game(self):
        # Randomly select an arena size from the list
        arena_size = random.choice(self.arena_sizes)
        arena = Arena(width=arena_size, height=arena_size) # Assuming the width and height are the same

        game = SimulationGame(arena, [])
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
            # Randomly select a creature type from the list
            creature_type = random.choice(self.creature_types)


            creature = creature_type(calculate_lattice_position_with_jitter(arena, self.n, i, jitter_range=self.jitter_range),i)
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

    #TODO make a machine gun gauntlet later and its the second task
    def initialize_machine_gun_duel(self):
        # Randomly select an arena size from the list
        arena_size = random.choice(self.arena_sizes)
        arena = Arena(width=arena_size, height=arena_size)

        game = SimulationGame(arena, [])
        Game.reset_time()
        creatures = []

        # Create n machine gun creatures
        participants = random.randint(3, 6)
        for i in range(participants):
            creature = get_machine_gun_creature_b(calculate_lattice_position_with_jitter(arena, 2, i, jitter_range=self.jitter_range), i)
            creatures.append(creature)
            game.add_game_object(creature)

        # Set the creature counts to indicate two machine gun creatures
        game.creature_counts = {
            'S': 0,
            'ML': 0,
            'MG': participants
        }

        return game

    # Function to run a single simulation and save the results
    def run_simulation(self):
        self.game = self.initialize_machine_gun_duel()
        while True:
            self.game.simulate_turn()
            alive_creatures = [creature for creature in self.game.game_objects if isinstance(creature, SimulationCreature) and creature.health > 0]
            if len(alive_creatures) == 1:
                self.game.winner = alive_creatures[0].name
                break
            if Game.get_time() >= self.time_limit or len(alive_creatures) == 0:
                # Determine the winner based on the highest score among alive creatures
                if alive_creatures:
                    creatures_by_score = sorted(alive_creatures, key=lambda creature: creature.score, reverse=True)
                    self.game.winner = creatures_by_score[0].name
                else:
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
    num_simulations = 1 # Number of simulations to run
    creature_types = [get_sniper_creature_b, get_machine_gun_creature_b, get_mine_laying_creature_b]
    arena_sizes = [2000, 2500, 3000] # List of arena sizes

    simulator = AutoChessBatchedSimulator(arena_sizes, creature_types, 3, 500) # Initialize the simulator
    simulator.run_batch_simulations(num_simulations) 
   
