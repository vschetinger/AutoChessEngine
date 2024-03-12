from AutoChessEngine import Arena, SimulationCreature, SimulationGame
import random

def initialize_game():
    arena = Arena(width=2000, height=2000)
    game = SimulationGame(arena, [])
    creatures = [SimulationCreature(
        position=(random.randint(100, 900), random.randint(100, 900)), 
        angle=random.randint(0, 360),
        health=100, 
        speed=random.randint(20, 100), 
        name=f"Creature {i}", 
        max_turn_rate=random.randint(2, 10),
        shoot_cooldown=random.randint(5, 20),
        bounding_box_size = (50, 100)
    ) for i in range(10)]

    for creature in creatures:
        creature.set_game(game)  # Associate each creature with the game
        game.add_game_object(creature)  # Assuming a method to add creatures to the game

    return game

def main():
    game = initialize_game()
    for _ in range(100):  
        game.simulate_turn()

    game.record_game("simulation_record5.json")

if __name__ == "__main__":
    main()
