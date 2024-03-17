from AutoChessEngine import Arena, RectCollider, SimulationCreature, SimulationGame, SimulationProjectile, Game
import random
import math

def get_sniper_creature(position, i):
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
        # ... any other new attributes you want to initialize ...
    )

def get_machine_gun_creature(position, i):
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
        # ... any other new attributes you want to initialize ...
    )

def get_mine_laying_creature(position, i):
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
        # ... any other new attributes you want to initialize ...
    )


def calculate_lattice_position(arena, n, i):

    # Calculate the number of rows and columns for the grid
    rows = int(n ** 0.5)
    cols = n if rows == 0 else (n // rows) + (n % rows > 0)

    # Calculate the row and column for the current creature
    row = i // cols
    col = i % cols

    # Calculate the size of each cell in the grid
    cell_width = arena.width / cols
    cell_height = arena.height / rows

    # Calculate the position of the creature within its cell
    # The creature is placed in the center of the cell
    x = (col * cell_width) + (cell_width / 2)
    y = (row * cell_height) + (cell_height / 2)

    return x, y

def calculate_lattice_position_with_jitter(arena, n, i, jitter_range=100):
    # Calculate the number of rows and columns for the grid
    rows = int(n ** 0.5)
    cols = n if rows == 0 else (n // rows) + (n % rows > 0)

    # Calculate the row and column for the current creature
    row = i // cols
    col = i % cols

    # Calculate the size of each cell in the grid
    cell_width = arena.width / cols
    cell_height = arena.height / rows

    # Calculate the position of the creature within its cell
    # The creature is placed in the center of the cell
    x = (col * cell_width) + (cell_width / 2)
    y = (row * cell_height) + (cell_height / 2)

    # Add jittering to the position
    x += random.uniform(-jitter_range, jitter_range)
    y += random.uniform(-jitter_range, jitter_range)

    # Ensure the position stays within the arena bounds
    x = max(0, min(arena.width, x))
    y = max(0, min(arena.height, y))

    return x, y

def initialize_game():
    arena = Arena(width=2000, height=2000)
    game = SimulationGame(arena, [])

    # Initialize a SimulationProjectile

    # Number of creatures in simulation
    n = 4

    # Randomly choose the type of creature to instantiate
    creature_types = [get_sniper_creature, get_machine_gun_creature, get_mine_laying_creature]

    creatures = [
        random.choice(creature_types)(calculate_lattice_position_with_jitter(arena, n, i, jitter_range=150),i)
        for i in range(n)
    ]

    for creature in creatures:
        game.add_game_object(creature) # Add the creature to the game

    return game

def main():
    game = initialize_game()
    time_limit = 5000 # Set your desired time limit here
    while True:
        game.simulate_turn()
        alive_creatures = [creature for creature in game.game_objects if isinstance(creature, SimulationCreature) and creature.health > 0]
        if len(alive_creatures) <= 1 or Game.get_time() >= time_limit:
            break

    game.record_game("simulation_record5.json")

if __name__ == "__main__":
    main()
