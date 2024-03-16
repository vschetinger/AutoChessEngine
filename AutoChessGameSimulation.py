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

def initialize_game():
    arena = Arena(width=2000, height=2000)
    game = SimulationGame(arena, [])

    # Initialize a SimulationProjectile

    # Number of creatures in simulation
    n = 20

    creatures = [SimulationCreature(
        position=calculate_lattice_position(arena, n, i), 
        angle=random.randint(0, 360),
        health=100, 
        speed=random.randint(3, 5), 
        name=f"Creature {i}",
        max_turn_rate=random.randint(1, 5),
        shoot_cooldown=random.randint(10, 20),
        bounding_box_size=(50, 100)
    ) for i in range(n)]

    for creature in creatures:
        game.add_game_object(creature) # Add the creature to the game

    return game

def main():
    game = initialize_game()
    for _ in range(100):  
        game.simulate_turn()

    game.record_game("simulation_record5.json")

if __name__ == "__main__":
    main()
