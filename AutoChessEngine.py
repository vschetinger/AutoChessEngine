import json
import math
import random
import pygame
from collections import deque

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
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


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

    




class SimulationCreature(BaseCreature):
    def __init__(self, id, health, position, speed, name, angle, max_turn_rate, shoot_cooldown, events=None):
        super().__init__(id, health, position, speed, name, angle)
        self.max_turn_rate = max_turn_rate
        self.action_plan = deque()  # Queue of actions
        self.shoot_cooldown = shoot_cooldown
        self.shoot_timer = 0  # Tracks cooldowns for shooting
        self.events = events if events else {}


    def record_event(self, event):
        # Only record the event if the game attribute is set
        if self.game is not None:
            time_index = self.game.turns_recorded
            if time_index not in self.events:
                self.events[time_index] = []
            self.events[time_index].append(event)

    def think(self, target):
        # Example logic to add 'turn' action every turn and 'shoot' action if cooldown allows
        self.action_plan.append(('turn', self.calculate_turn(target)))
        if self.shoot_timer <= 0:  # Can shoot if shoot_timer is 0 or less
            self.action_plan.append(('shoot', None))
            self.shoot_timer = self.shoot_cooldown  # Reset shoot cooldown timer
            
    def calculate_turn(self, target):
        # Same target angle calculation as before, returns angle adjustment
        # This method now only calculates the turn amount instead of directly setting the angle
        target_x, target_y = target
        dx = target_x - self.position[0]
        dy = target_y - self.position[1]
        target_angle_rad = math.atan2(dy, dx)
        target_angle = math.degrees(target_angle_rad) % 360

        angle_diff = (target_angle - self.angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360

        return max(-self.max_turn_rate, min(angle_diff, self.max_turn_rate))


    def move(self, arena, time_index):

        while self.action_plan:
            action, value = self.action_plan.popleft()
            if action == 'turn':
                self.set_angle(self.angle + value)
            elif action == 'shoot':
                self.perform_shoot()        

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

        if self.shoot_timer > 0:
            self.shoot_timer -= 1




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

    def draw(self, screen, convert_to_screen):
        point = convert_to_screen(self.position)
        radians = math.radians(self.angle)

        # Triangle points
        base_length = 20
        front_point = (point[0] + math.cos(radians) * base_length, point[1] + math.sin(radians) * base_length)
        back_center_point = (point[0] - math.cos(radians) * base_length / 2, point[1] - math.sin(radians) * base_length / 2)
        left_point = (back_center_point[0] + math.cos(radians + math.pi / 2) * base_length / 2, back_center_point[1] + math.sin(radians + math.pi / 2) * base_length / 2)
        right_point = (back_center_point[0] + math.cos(radians - math.pi / 2) * base_length / 2, back_center_point[1] + math.sin(radians - math.pi / 2) * base_length / 2)

        points = [front_point, left_point, right_point]
        color = self.color
        pygame.draw.polygon(screen, color, points)

        # Wheels
        wheel_width = 20
        wheel_height = 8
        wheel_distance_from_center = base_length / 2  # Distance from the center of the back side to where wheels should be drawn
        wheel_distance_apart = base_length  # Distance between the centers of the two wheels

        # Calculate the centers of the wheels
        left_wheel_center = (back_center_point[0] + math.cos(radians + math.pi / 2) * (wheel_distance_apart / 2), 
                            back_center_point[1] + math.sin(radians + math.pi / 2) * (wheel_distance_apart / 2))
        right_wheel_center = (back_center_point[0] + math.cos(radians - math.pi / 2) * (wheel_distance_apart / 2), 
                            back_center_point[1] + math.sin(radians - math.pi / 2) * (wheel_distance_apart / 2))

        # Draw wheels as ellipses
        pygame.draw.ellipse(screen, color, pygame.Rect(left_wheel_center[0] - wheel_width / 2, left_wheel_center[1] - wheel_height / 2, wheel_width, wheel_height))
        pygame.draw.ellipse(screen, color, pygame.Rect(right_wheel_center[0] - wheel_width / 2, right_wheel_center[1] - wheel_height / 2, wheel_width, wheel_height))





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
        arena_center = (self.arena.width / 2, self.arena.height / 2)
        for creature in self.creatures:
            creature.think(arena_center)  # Let each creature decide its move
            creature.move(self.arena, self.turns_recorded)
        self.turns_recorded += 1

    def record_game(self, filename):
        header = {
            "arena": {"width": self.arena.width, "height": self.arena.height},
            "creatures": [
                {"id": creature.id, "health": creature.health, "position": creature.initial_position, "speed": creature.speed, "name": creature.name, "angle": creature.angle, "color": creature.color} for creature in self.creatures
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

