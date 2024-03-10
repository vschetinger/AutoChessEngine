from AutoChessEngine import Arena, Creature, Game
import random
def initialize_game():
    arena = Arena(width=1000, height=1000)
    # Create a list of Creature objects
    creatures = [Creature(
                    id=i, 
                    health=100, 
                    position=(random.randint(100, 900), random.randint(100, 900)), 
                    speed=random.randint(5, 15), 
                    name=f"Creature {i}", 
                    angle=random.randint(0, 360)  # Add a random starting angle for each creature
                 ) for i in range(3)]  # Adjust the range as needed for the number of creatures
    return Game(arena, creatures)

def main():
    game = initialize_game()
    for _ in range(2):  # Replace 10 with the desired number of iterations
        game.simulate_turn()
    game.record_game("simulation_record2.json")

if __name__ == "__main__":
    main()
