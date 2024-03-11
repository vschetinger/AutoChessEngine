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
        # Check if _internal_id is set before proceeding
        if hasattr(self, '_internal_id') and self._internal_id and self.game.time >= 0:
            result = method(self, *args, **kwargs)

            # Prepare the attribute name
            attribute_name = method.__name__.replace("set_", "")

            # Prepare the value to record
            value_to_record = kwargs.get('value', args[0] if args else None)

            # Check if the attribute being updated is a tuple (e.g., 'position')
            if isinstance(value_to_record, tuple):
                # Here you can decide how to handle tuples; for this example, we're recording it directly
                event_value = value_to_record
            else:
                current_value = getattr(self, attribute_name)
                if isinstance(current_value, tuple):
                    # If the current attribute is a tuple but the update is not, this part needs adjustment
                    # For simplicity, let's assume the update is for the x coordinate
                    event_value = (value_to_record, current_value[1])
                else:
                    event_value = value_to_record

            # Generate the event
            event = {
                "type": "deltaSetter",
                "id": self.id,  # Assuming self.id is correctly set
                "attribute": attribute_name,
                "value": event_value
            }
            self.record_event(event)
            
            return result
    return wrapper


class Collider:
    def __init__(self, position=(0, 0), angle=0, **kwargs):
        self._position = position  # Use an internal variable to avoid recursion
        self._angle = angle

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    def rotate(self, angle):
        self._angle += angle

    def check_collision(self, other):
        raise NotImplementedError("This method should be implemented by subclasses.")



class RectCollider(Collider):
    def __init__(self, position=(0, 0), size=(0, 0), angle=0, **kwargs):
        super().__init__(position, angle, **kwargs)
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

    @property
    def position(self):
        return self.rect.topleft

    @position.setter
    def position(self, value):
        self.rect.topleft = value




class CircleCollider(Collider):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def check_collision(self, other):
        if isinstance(other, CircleCollider):
            return self._circle_circle_collision(other)
        elif isinstance(other, RectCollider):
            return self._circle_rect_collision(other)
        # Handle other collider types as necessary
        return False

    def _circle_circle_collision(self, other):
        dx = self.center[0] - other.center[0]
        dy = self.center[1] - other.center[1]
        distance = math.hypot(dx, dy)
        return distance < (self.radius + other.radius)

    def _circle_rect_collision(self, other):
        closest_x = max(other.rect.left, min(self.center[0], other.rect.right))
        closest_y = max(other.rect.top, min(self.center[1], other.rect.bottom))
        
        dx = self.center[0] - closest_x
        dy = self.center[1] - closest_y

        return dx**2 + dy**2 < self.radius**2


class GameObject:
    def __init__(self, position, angle, collider=None, **kwargs):
        
        if collider is None:
            self.collider = Collider(position, angle)
        else:
            self.collider = collider
        self.position = position
        self.initial_position = position  # Use copy() if it's a mutable object like a list or dict
        self.angle = angle
        self.initial_angle = angle
        self.game = None

        def check_collision_with(self, other):
            return self.collider.check_collision(other.collider)

    def set_game(self, game):
        self.game = game

    def think(self, *args, **kwargs):
        # Placeholder for think, to be overridden by subclasses
        pass

    def move(self, *args, **kwargs):
        # Placeholder for move, to be overridden by subclasses
        pass

    @recordable
    def set_position(self, x, y):
        self.collider.position((x, y))

    @recordable
    def set_angle(self, angle):
        self.collider.angle = (angle % 360)  # Normalize the angle

    @property
    def id(self):
        return self._internal_id  # Return the id that was generated in __init__
    
    @property
    def position(self):
        return self.collider.position

    @position.setter
    @recordable
    def position(self, value):
        self.collider.position = value

    @property
    def angle(self):
        return self.collider.angle

    @angle.setter
    @recordable
    def angle(self, value):
        self.collider.angle = (value % 360)  # Normalize the angle

class SimulationGameObject(GameObject):
    def __init__(self, position, angle, collider=None, **kwargs):
        super().__init__(position, angle, collider=collider, **kwargs)  # Now correctly forwards expected arguments
        self._internal_id = id(self)  # Unique internal ID (using Python's built-in id())
        self.action_plan = deque()
        self.events = {}
        
    def record_event(self, event):
        # Only record the event if the game attribute is set
        if self.game is not None:
            time_index = self.game.time
            if time_index not in self.events:
                self.events[time_index] = []
            self.events[time_index].append(event)

class PlaybackGameObject(GameObject):
    def __init__(self, playback_id, position, angle, events=None, **kwargs):
        super().__init__(position, angle, **kwargs)
        self._internal_id = playback_id  # Use the playback_id as the internal ID
        self.playback_id = playback_id  # This ID is from the JSON file for playback purposes
        self.events = events or {}


    def reset_to_initial_state(self):
        # Reset to the initial position and angle
        self.collider.position = self.initial_position
        self.collider.angle = self.initial_angle

    def record_event(self, event):
        # This base method does nothing, and is here to ensure that the decorated setters
        # do not cause errors when called on a PlaybackCreature instance.
        pass     
    
    def move(self, time_index):
        # Use events to update position, angle, etc., based on the new event structure.
        if time_index in self.events:
            for event in self.events[time_index]:
                if event["type"] == "deltaSetter":
                    attribute = event["attribute"]
                    value = event["value"]
                    # Update the attribute based on the event information.
                    setattr(self, attribute, value)

    def draw(self, *args, **kwargs):
        # Placeholder for draw, to be overridden by subclasses
        pass


class BaseCreature:
    def __init__(self, health, speed, name,):    
        self.health = health
        self.speed = speed
        self.name = name
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


class SimulationCreature(SimulationGameObject, BaseCreature):
    def __init__(self, position, angle, health, speed, name, max_turn_rate, shoot_cooldown, events=None, **kwargs):
        bounding_box_size = (12, 30)  # Example size
        # Adjust bounding_rect initialization as needed to fit the game's logic
        bounding_rect = pygame.Rect(position[0] - bounding_box_size[0] / 2,
                                    position[1] - bounding_box_size[1] / 2,
                                    *bounding_box_size)
        collider = RectCollider(bounding_rect)
        super().__init__(position, angle, collider=collider, **kwargs)
        BaseCreature.__init__(self, health, speed, name, **kwargs)
        
        self.max_turn_rate = max_turn_rate
        self.shoot_cooldown = shoot_cooldown
        self.shoot_timer = 0
        self.events = events or {}



    def think(self, target):
        # Example logic to add 'turn' action every turn and 'shoot' action if cooldown allows
        self.action_plan.append(('turn', self.calculate_turn(target)))
        if self.shoot_timer <= 0:  # Can shoot if shoot_timer is 0 or less
            self.action_plan.append(('shoot', None))
            self.shoot_timer = self.shoot_cooldown  # Reset shoot cooldown timer
            
    def calculate_turn(self, target):
        # Same target angle calculation as before, returns angle adjustment
        # This method now only calculates the turn amount instead of directly setting the angle
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
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
                # Use the property setter for angle
                self.angle = self.angle + value
            # Implement other actions as necessary

        # Calculate the new position based on the current angle and speed
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        # Ensure the new position does not exceed the arena boundaries
        new_x = max(0, min(arena.width, new_x))
        new_y = max(0, min(arena.height, new_y))

        # Use the property setter for position
        self.position = (new_x, new_y)

        # Decrement the shoot timer if it's greater than 0
        if self.shoot_timer > 0:
            self.shoot_timer -= 1


class PlaybackCreature(PlaybackGameObject, BaseCreature):
    def __init__(self, playback_id, health, position, speed, name, angle, events, collider):
        PlaybackGameObject.__init__(self, playback_id, position, angle, events)
        BaseCreature.__init__(self, health, speed, name)
        self.collider = collider  # Use the provided collider

    def draw(self, screen, convert_to_screen):
        # Convert the collider's position to screen coordinates
        screen_position = convert_to_screen(self.collider.position)

        radians = math.radians(self.collider.angle)

        # Triangle points for visual representation
        base_length = 20
        front_point = (screen_position[0] + math.cos(radians) * base_length, screen_position[1] + math.sin(radians) * base_length)
        back_center_point = (screen_position[0] - math.cos(radians) * base_length / 2, screen_position[1] - math.sin(radians) * base_length / 2)
        left_point = (back_center_point[0] + math.cos(radians + math.pi / 2) * base_length / 2, back_center_point[1] + math.sin(radians + math.pi / 2) * base_length / 2)
        right_point = (back_center_point[0] + math.cos(radians - math.pi / 2) * base_length / 2, back_center_point[1] + math.sin(radians - math.pi / 2) * base_length / 2)
        points = [front_point, left_point, right_point]
        color = self.color

        pygame.draw.rect(screen, color, self.collider.rect, 1)  # Draw collider

        pygame.draw.polygon(screen, (255, 255, 255), points)





class Game:
    def __init__(self, arena):
        self.arena = arena
        self.creatures = []  # Initialized but can be populated by derived classes
        self.time = -1

    def add_creature(self, creature):
        self.creatures.append(creature)  # Add the creature to the game's list of creatures
        creature.set_game(self)  # Set this game instance as the creature's game

    def set_game_for_creatures(self):
        for creature in self.creatures:
            creature.set_game(self)



# Example of converting a complex object to a serializable format
def serialize_events(events):
    serialized_events = {}
    for time_index, event_list in events.items():
        serialized_events[time_index] = [
            {"type": event["type"], "id": event["id"], "attribute": event["attribute"], "value": event["value"]}
            for event in event_list
        ]
    return serialized_events


class SimulationGame(Game):
    def __init__(self, arena, creatures):
        super().__init__(arena)
        self.creatures = creatures
        self.set_game_for_creatures()  # Call the set_game_for_creatures() method on self
        
    

    def simulate_turn(self):
        if self.time == -1:
            self.time = 0  # Start the game
        arena_center = (self.arena.width / 2, self.arena.height / 2)
        for creature in self.creatures:
            creature.think(arena_center)  # Let each creature decide its move
            creature.move(self.arena, self.time)
        self.time += 1




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

        # Use the serialize_events function to prepare events for serialization
        events = serialize_events(events)

        game_record = {"header": header, "events": events}
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=4)

