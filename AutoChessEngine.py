import json
import math
import random
import pygame

class Arena:
    def __init__(self, width, height):
        self.width = width
        self.height = height

def recordable(method):
    def wrapper(self, *args, **kwargs):
        # Call the original method that updates the attribute
        result = method(self, *args, **kwargs)
        
        # Get the name of the attribute that is being set by convention
        attribute_name = method.__name__.replace("set_", "")
        
        # Generate the event
        value = getattr(self, attribute_name)
        event = {
            "type": "deltaSetter",
            "id": self.id,
            "attribute": attribute_name,
            "value": value
        }
        self.record_event(event)
        
        return result
    return wrapper

class BaseCreature:
    def __init__(self,id, health, position, speed, name, angle):
        self.game = None    
        self.id = id
        self.health = health
        self.position = position
        self.initial_position = position
        self.speed = speed
        self.name = name
        self.angle = angle
        self.initial_angle = angle  

    def set_game(self, game):
        self.game = game

    def record_event(self, event):
        # This base method does nothing, and is here to ensure that the decorated setters
        # do not cause errors when called on a PlaybackCreature instance.
        pass

    @recordable
    def set_position(self, x, y):
        self.position = (x, y)

    @recordable
    def set_angle(self, angle):
        self.angle = angle % 360  # Normalize the angle

    def draw(self, screen, convert_to_screen):
        point = convert_to_screen(self.position)
        radians = math.radians(self.angle)
        
        # Adjust points to make the creature visibly pointy in the direction of movement
        front_point = (point[0] + math.cos(radians) * 20, point[1] + math.sin(radians) * 20)  # Front of the triangle
        left_point = (point[0] + math.cos(radians + math.pi * 5/6) * 10, point[1] + math.sin(radians + math.pi * 5/6) * 10)  # Left back corner
        right_point = (point[0] + math.cos(radians - math.pi * 5/6) * 10, point[1] + math.sin(radians - math.pi * 5/6) * 10)  # Right back corner

        points = [front_point, left_point, right_point]
        color = (255, 0, 0) if self.id % 2 == 0 else (0, 0, 255)
        pygame.draw.polygon(screen, color, points)




class SimulationCreature(BaseCreature):
    def __init__(self, id, health, position, speed, name, angle, events=None):
        super().__init__(id, health, position, speed, name, angle)
        self.events = events if events else {}

    def record_event(self, event):
        # Only record the event if the game attribute is set
        if self.game is not None:
            time_index = self.game.turns_recorded
            if time_index not in self.events:
                self.events[time_index] = []
            self.events[time_index].append(event)

    def move(self, arena, time_index):
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        # Check for collision with the arena boundaries to reflect the creature's movement
        if new_x <= 0 or new_x >= arena.width:
            self.set_angle((360 - self.angle) % 360)
            dx = -dx  # Invert the x-direction of movement

        if new_y <= 0 or new_y >= arena.height:
            self.set_angle((180 - self.angle) % 360)
            dy = -dy  # Invert the y-direction of movement

        # Correct position if out of bounds and use the setter to update
        new_x = max(0, min(arena.width, new_x))
        new_y = max(0, min(arena.height, new_y))
        self.set_position(new_x, new_y)


class PlaybackCreature(BaseCreature):
    def __init__(self, id, health, position, speed, name, angle, events):
        super().__init__(id, health, position, speed, name, angle)
        self.events = events

    def move(self, time_index):
        # Use events to update position, angle, etc., based on the new event structure.
        if time_index in self.events:
            for event in self.events[time_index]:
                if event["type"] == "deltaSetter":
                    attribute = event["attribute"]
                    value = event["value"]
                    # Update the attribute based on the event information.
                    setattr(self, attribute, value)



    def reset_to_initial_state(self):
        # Reset to the initial position and angle
        self.position = self.initial_position
        self.angle = self.initial_angle


class Game:
    def __init__(self, arena):
        self.arena = arena
        self.creatures = []  # Initialized but can be populated by derived classes

    def set_game_for_creatures(self):
        for creature in self.creatures:
            creature.set_game(self)

class SimulationGame(Game):
    def __init__(self, arena, creatures):
        super().__init__(arena)
        self.creatures = creatures
        self.set_game_for_creatures()  # Call the set_game_for_creatures() method on self
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

