import json

class Creature:
    def __init__(self, health, attack, name):
        self.initial_health = health
        self.health = health
        self.attack = attack
        self.is_alive = True
        self.name = name

    def to_dict(self):
        return {
            "name": self.name,
            "initial_health": self.initial_health,
            "attack": self.attack
        }

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False

class Player:
    def __init__(self, creatures):
        self.creatures = creatures

    def has_alive_creatures(self):
        return any(creature.is_alive for creature in self.creatures)

    def get_first_alive_creature(self):
        for creature in self.creatures:
            if creature.is_alive:
                return creature
        return None

class Game:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.turn = 0
        self.battle_log = {"header": {"creatures": []}, "events": []}

    def simulate_battle(self):
        # Populate the header with creatures' initial states
        for player_index, player in enumerate(self.players, start=1):
            for creature in player.creatures:
                creature_info = creature.to_dict()
                creature_info.update({"player": f"Player {player_index}"})
                self.battle_log["header"]["creatures"].append(creature_info)

        while all(player.has_alive_creatures() for player in self.players):
            attacker_player = self.players[self.turn % 2]
            defender_player = self.players[(self.turn + 1) % 2]
            attacker = attacker_player.get_first_alive_creature()
            defender = defender_player.get_first_alive_creature()

            if attacker and defender:  # Both are alive
                defender.take_damage(attacker.attack)
                event = {
                    "turn": self.turn + 1,
                    "attacker": attacker.name,
                    "defender": defender.name,
                    "damage": attacker.attack,
                    "defender_remaining_health": max(0, defender.health)
                }
                self.battle_log["events"].append(event)

            self.turn += 1

            if not attacker.is_alive or not defender.is_alive:
                winner = "Player 1" if defender_player.has_alive_creatures() else "Player 2"
                self.battle_log["events"].append({"winner": winner, "turn": self.turn})
                break

        return self.battle_log

# Instantiate multiple creatures for both players
creatures_player1 = [Creature(health=4, attack=1, name=f"Creature {i}P1") for i in range(1, 4)]
creatures_player2 = [Creature(health=4, attack=1, name=f"Creature {i}P2") for i in range(1, 4)]

# Instantiate players with multiple creatures
player1 = Player(creatures_player1)
player2 = Player(creatures_player2)

# Start the game
game = Game(player1, player2)
battle_log_with_header = game.simulate_battle()

# Save the battle log to a JSON file
with open('battle_log_with_header.json', 'w') as f:
    json.dump(battle_log_with_header, f, indent=4)

battle_log_with_header_path = 'battle_log_with_header.json'
print(battle_log_with_header_path)
