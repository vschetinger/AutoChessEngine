import json
import math
import random

class Arena:
    def __init__(self, width, height):
        self.width = width
        self.height = height

# Arena dimensions
arena_width = 1000
arena_height = 1000


def calculate_collision_time(position, velocity, arena_bounds):
    times = []
    # Calculate time to hit each wall
    for dim in range(2):  # 0 for x-axis, 1 for y-axis
        if velocity[dim] == 0:
            times.append(float('inf'))  # Can't hit the wall in this dimension
        else:
            if velocity[dim] > 0:
                wall_pos = arena_bounds[dim][1]  # Right or Bottom wall
            else:
                wall_pos = arena_bounds[dim][0]  # Left or Top wall
            time = (wall_pos - position[dim]) / velocity[dim]
            times.append(time)
    return times

def reflect(velocity, normal):
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    reflected_velocity = (
        velocity[0] - 2 * dot_product * normal[0],
        velocity[1] - 2 * dot_product * normal[1],
    )
    return reflected_velocity



class Creature:
    def __init__(self, health, attack, name, turn_rate, move_vector,position):
        self.initial_health = health
        self.health = health
        self.attack = attack
        self.is_alive = True
        self.name = name
        self.turn_rate = turn_rate  # Degrees allowed to turn towards target each turn
        self.move_vector = move_vector  # Distance to move each turn
        self.angle = 0  # Initial angle of the creature
        self.target = None  # Target creature
        self.position = position

    def to_dict(self):
        return {
            "name": self.name,
            "initial_health": self.initial_health,
            "attack": self.attack
        }
    
    def calculate_movement(self, arena):
        path_segments = []
        position = self.position
        arena_bounds = [(0, arena.width), (0, arena.height)]
        
        dx = self.move_vector * math.cos(math.radians(self.angle))
        dy = self.move_vector * math.sin(math.radians(self.angle))
        velocity = (dx, dy)
        total_distance = self.move_vector

        while total_distance > 0:
            times = calculate_collision_time(position, velocity, arena_bounds)
            min_time = min(times)
            if min_time > total_distance or min_time == float('inf'):
                # No collision within the remaining distance
                new_position = (position[0] + velocity[0] * total_distance, position[1] + velocity[1] * total_distance)
                path_segments.append((velocity[0] * total_distance, velocity[1] * total_distance))
                break
            else:
                # Collision occurs
                collision_index = times.index(min_time)
                normal = [0, 0]
                normal[collision_index] = 1 if velocity[collision_index] > 0 else -1
                new_position = (position[0] + velocity[0] * min_time, position[1] + velocity[1] * min_time)
                path_segments.append((velocity[0] * min_time, velocity[1] * min_time))
                velocity = reflect(velocity, normal)
                total_distance -= min_time
                position = new_position

        self.position = new_position
        return path_segments


    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
    
    def select_target(self, enemies):
        if self.target is None or not self.target.is_alive:
            if enemies:
                self.target = min(enemies, key=lambda enemy: self.distance_to(enemy))
        # Update target selection logic if necessary
    
    def distance_to(self, enemy):
        # Placeholder for actual distance calculation
        return random.randint(1, 10)  # Simplified for illustration

    def move_towards_target(self):
        if self.target:
            # Simplified movement towards target, actual implementation would calculate new position
            self.angle = (self.angle + self.turn_rate) % 360  # Update angle towards target
            # Placeholder for movement towards target


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
    def __init__(self, player1, player2, arena):
        self.players = [player1, player2]
        self.turn = 0
        self.battle_log = {"header": {"creatures": []}, "events": []}
        self.arena = arena

    def simulate_battle(self):
        # Populate the header with creatures' initial states for reference
        for player in self.players:
            for creature in player.creatures:
                creature_info = creature.to_dict()
                creature_info.update({"player": "Player 1" if player == self.players[0] else "Player 2"})
                self.battle_log["header"]["creatures"].append(creature_info)

        # Simulate and log movements
        for turn in range(2):  # Simulate for 5 turns
            turn_events = []
            for player in self.players:
                for creature in player.creatures:
                    if creature.is_alive:
                        movement_path = creature.calculate_movement(self.arena)
                        turn_events.append({
                            "creature": creature.name,
                            "movement_path": movement_path,
                            "final_position": creature.position
                        })
            self.battle_log["events"].append({"turn": turn + 1, "movements": turn_events})

        return self.battle_log


def initialize_creatures_for_player(player_number, arena_width, arena_height):
    positions = [
        (arena_width / 4, arena_height * 0.1 if player_number == 1 else arena_height * 0.9),
        (arena_width / 2, arena_height * 0.1 if player_number == 1 else arena_height * 0.9),
        (arena_width * 3 / 4, arena_height * 0.1 if player_number == 1 else arena_height * 0.9),
    ]
    creatures = [
        Creature(health=10, attack=2, name=f"Creature {i+1} Player {player_number}", turn_rate=45, move_vector=100, position=pos)
        for i, pos in enumerate(positions)
    ]
    return creatures

# Initialize players with creatures in specified positions
player1_creatures = initialize_creatures_for_player(1, arena_width, arena_height)
player2_creatures = initialize_creatures_for_player(2, arena_width, arena_height)

player1 = Player(player1_creatures)
player2 = Player(player2_creatures)


# Start the game
arena = Arena(width=arena_width, height=arena_height)
game = Game(player1, player2, arena)
battle_log_with_header = game.simulate_battle()

# Save the battle log to a JSON file
with open('battle_log_with_header.json', 'w') as f:
    json.dump(battle_log_with_header, f, indent=4)

battle_log_with_header_path = 'battle_log_with_header.json'
print(battle_log_with_header_path)
