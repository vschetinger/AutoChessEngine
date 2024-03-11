from AutoChessEngine import Arena, SimulationCreature, SimulationGame
import random
def initialize_game():
    arena = Arena(width=2000, height=2000)

    # Create a list of Creature objects
    creatures = [SimulationCreature(
                id=i, 
                health=100, 
                position=(random.randint(100, 900), random.randint(100, 900)), 
                speed=random.randint(5, 50), 
                name=f"Creature {i}", 
                angle=random.randint(0, 360),  # Random starting angle
                max_turn_rate=random.randint(2, 10)  # Random max turn rate
             ) for i in range(5)]  # Adjust the range as needed

    return SimulationGame(arena, creatures)

def main():
    game = initialize_game()
    for _ in range(200):  
        game.simulate_turn()
    game.record_game("simulation_record5.json")

if __name__ == "__main__":
    main()
