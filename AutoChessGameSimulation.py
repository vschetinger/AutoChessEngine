from AutoChessEngine import Arena, RectCollider, SimulationCreature, SimulationGame, SimulationProjectile
import random



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
    n = 3

    creatures = [SimulationCreature(
        position=calculate_lattice_position_with_jitter(arena, n, i, jitter_range=150),
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Creature {i}",
        max_turn_rate=random.randint(1, 6),
        shoot_cooldown=random.randint(5, 30),
        bounding_box_size=(50, 100),
        damage=random.randint(10, 100), # Random damage value between 10 and 50
        bullet_speed=random.randint(10, 50), # Random bullet speed value between 10 and 50
        bullet_range=random.randint(200, 500), # Random bullet range between 100 and 500
        # ... any other new attributes you want to initialize ...
    ) for i in range(n)]

    for creature in creatures:
        game.add_game_object(creature) # Add the creature to the game

    return game

def main():
    game = initialize_game()
    for _ in range(300):  
        game.simulate_turn()

    game.record_game("simulation_record5.json")

if __name__ == "__main__":
    main()
