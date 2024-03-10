import json
import math
import random
import pygame

class Arena:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Creature:
    def __init__(self, id, health, position, speed, name, angle, deltas):
        self.id = id
        self.health = health
        self.position = position  # (x, y) tuple
        self.initial_position = position
        self.speed = speed  # Movement speed
        self.name = name
        self.angle = angle  # Angle in degrees
        self.deltas = deltas  # List of movement deltas
        self.current_delta_index = 0  # To keep track of the current delta

    def apply_next_delta(self):
        if self.current_delta_index < len(self.deltas):
            dx, dy = self.deltas[self.current_delta_index]
            self.position = (self.position[0] + dx, self.position[1] + dy)
            print(len(self.deltas))
        else:
            # Reset to the beginning if we've reached the end of deltas
            print("Deveria ter Resetado " + self.current_delta_index)
            self.current_delta_index = 0
            self.position = self.initial_position
        
        # Always increment the index
        self.current_delta_index = (self.current_delta_index + 1) % len(self.deltas)

    def move(self, arena):
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        # Check for boundary collisions and adjust angle if necessary
        if new_x <= 0 or new_x >= arena.width:
            self.angle = (180 - self.angle) % 360
        if new_y <= 0 or new_y >= arena.height:
            self.angle = (-self.angle) % 360

        # Recalculate movement after adjusting the angle
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        self.position = (max(0, min(arena.width, self.position[0] + dx)),
                         max(0, min(arena.height, self.position[1] + dy)))
        self.delta.append((dx, dy))  # Record the adjusted delta

        print(f"Creature {self.id} moving. New angle: {self.angle}, Delta: {self.delta[-1]}")

    def draw(self, screen, convert_function):
        point = convert_function(self.position)  # Use the passed function to convert the position
        radians = math.radians(self.angle)
        points = [
            (point[0] + math.cos(radians) * 10, point[1] + math.sin(radians) * 10),
            (point[0] + math.cos(radians + 2.0944) * 10, point[1] + math.sin(radians + 2.0944) * 10),
            (point[0] + math.cos(radians - 2.0944) * 10, point[1] + math.sin(radians - 2.0944) * 10)
        ]
        color = (255, 0, 0) if self.id % 2 == 0 else (0, 0, 255)
        pygame.draw.polygon(screen, color, points)

    def virtual_to_screen(self, position):
        # Assuming an arena size of 1000x1000 mapped to an 800x800 screen
        virtual_x, virtual_y = position
        screen_x = (virtual_x / 1000) * 800
        screen_y = (virtual_y / 1000) * 800
        return int(screen_x), int(screen_y)


    def update(self, arena):
        self.move(arena)

class Game:
    def __init__(self, arena, creatures):
        self.arena = arena
        self.creatures = creatures  # List of Creature objects
        self.turns_recorded = 0

    def simulate_turn(self):
        for creature in self.creatures:
            creature.update(self.arena)
        print(f"Turn {self.turns_recorded} updated.")    
        self.turns_recorded += 1

    def is_game_over(self):
        # Placeholder for game over logic
        return self.turns_recorded >= 10  # Example condition

    def record_game(self, filename):
        # Record the game into a JSON file
        header = {
            "arena": {"width": self.arena.width, "height": self.arena.height},
            "creatures": [{
                "id": creature.id,
                "health": creature.health,
                "position": creature.position,
                "speed": creature.speed,
                "name": creature.name,
                "angle": creature.angle
            } for creature in self.creatures]
        }
        movements = [{"id": creature.id, "deltas": creature.delta} for creature in self.creatures]
        game_record = {"header": header, "movements": movements}
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=4)
