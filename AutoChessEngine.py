import json
import math
import random
import pygame

class Arena:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class BaseCreature:
    def __init__(self, id, health, position, speed, name, angle):
        self.id = id
        self.health = health
        self.position = position
        self.initial_position = position
        self.speed = speed
        self.name = name
        self.angle = angle

    def draw(self, screen, convert_to_screen):
        point = convert_to_screen(self.position)
        radians = math.radians(self.angle)
        points = [
            (point[0] + math.cos(radians) * 10, point[1] + math.sin(radians) * 10),
            (point[0] + math.cos(radians + 2.0944) * 10, point[1] + math.sin(radians + 2.0944) * 10),
            (point[0] + math.cos(radians - 2.0944) * 10, point[1] + math.sin(radians - 2.0944) * 10),
        ]
        color = (255, 0, 0) if self.id % 2 == 0 else (0, 0, 255)
        pygame.draw.polygon(screen, color, points)


class SimulationCreature(BaseCreature):
    def __init__(self, id, health, position, speed, name, angle, events=None):
        super().__init__(id, health, position, speed, name, angle)
        self.events = events if events else {}

    def move(self, arena, time_index):
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        new_x, new_y = self.position[0] + dx, self.position[1] + dy

        angle_changed = False
        if new_x <= 0 or new_x >= arena.width or new_y <= 0 or new_y >= arena.height:
            self.angle = (180 - self.angle) % 360 if new_x <= 0 or new_x >= arena.width else (-self.angle) % 360
            angle_changed = True

        # Record events
        if time_index not in self.events:
            self.events[time_index] = []
        self.events[time_index].append({"type": "delta", "id": self.id, "value": {"dx": dx, "dy": dy}})
        if angle_changed:
            self.events[time_index].append({"type": "angle", "id": self.id, "value": self.angle})

        self.position = (max(0, min(arena.width, new_x)), max(0, min(arena.height, new_y)))

class PlaybackCreature(BaseCreature):
    def __init__(self, id, health, position, speed, name, angle, events):
        super().__init__(id, health, position, speed, name, angle)
        self.events = events

    def move(self, arena, time_index):
        # Use events to update position, angle, etc.
        if time_index in self.events:
            for event in self.events[time_index]:
                if event["type"] == "delta":
                    self.position = (self.position[0] + event["value"]["dx"], self.position[1] + event["value"]["dy"])


class Game:
    def __init__(self, arena, creatures):
        self.arena = arena
        self.creatures = creatures

class SimulationGame(Game):
    def __init__(self, arena, creatures):
        super().__init__(arena, creatures)
        self.turns_recorded = 0
        self.events = {}

    def simulate_turn(self):
        for creature in self.creatures:
            creature.move(self.arena, self.turns_recorded)
        self.turns_recorded += 1

    def record_game(self, filename):
        header = {
            "arena": {"width": self.arena.width, "height": self.arena.height},
            "creatures": [
                {"id": creature.id, "health": creature.health, "position": creature.initial_position, "speed": creature.speed, "name": creature.name, "angle": creature.angle} for creature in self.creatures
            ],
            "metadata": {
                "playerNames": ["Player 1", "Player 2"],
            }
        }
        # Collect events from all turns; each creature manages its own events
        events = {}
        for creature in self.creatures:
            for time_index, event_list in creature.events.items():
                if time_index not in events:
                    events[time_index] = []
                events[time_index].extend(event_list)

        game_record = {"header": header, "events": events}
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=4)

