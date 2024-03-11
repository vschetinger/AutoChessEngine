from AutoChessEngine import Arena, SimulationCreature, SimulationGame
import random
def initialize_game():
    arena = Arena(width=1000, height=1000)
    # Create a list of Creature objects
    creatures = [SimulationCreature(
                    id=i, 
                    health=100, 
                    position=(random.randint(100, 900), random.randint(100, 900)), 
                    speed=random.randint(5, 12), 
                    name=f"Creature {i}", 
                    angle=random.randint(0, 360)  # Add a random starting angle for each creature
                 ) for i in range(3)]  # Adjust the range as needed for the number of creatures
    return SimulationGame(arena, creatures)

def main():
    game = initialize_game()
    for _ in range(150):  # Replace 10 with the desired number of iterations
        game.simulate_turn()
    game.record_game("simulation_record5.json")

if __name__ == "__main__":
    main()
