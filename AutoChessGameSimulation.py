from AutoChessEngine import Arena, Creature, Game
import random
def initialize_game():
    arena = Arena(width=1000, height=1000)
    creatures = [Creature(id=i, health=100, position=(random.randint(100, 900), random.randint(100, 900)), speed=random.randint(5, 15), name=f"Creature {i}") for i in range(3)]
    return Game(arena, creatures)

def main():
    game = initialize_game()
    while not game.is_game_over():
        game.simulate_turn()
    game.record_game("simulation_record.json")

if __name__ == "__main__":
    main()
