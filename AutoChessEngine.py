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
    def __init__(self, center=(0, 0), angle=0, **kwargs):
        self._center = center
        self._angle = angle

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._center = value
        else:
            raise ValueError("Center must be a tuple with two numeric values.")

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def check_collision(self, other):
        raise NotImplementedError("This method should be implemented by subclasses.")



class RectCollider(Collider):
    def __init__(self, center=(0, 0), size=(1, 1), angle=0, **kwargs):
        super().__init__(center, angle, **kwargs)  # Call the base class constructor first
        self._size = size  # Set the size attribute
        self.rect = pygame.Rect(0, 0, *size)  # Initialize the rect attribute
        self.rect.center = center  # Set the center of the rect

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            self._size = value
            self.rect.size = value  # Update the size of the rect
        else:
            raise ValueError("Size must be a tuple with two numeric values.")


    @Collider.center.setter
    def center(self, value):
        Collider.center.fset(self, value)  # Set the center in the base class
        self.rect.center = value  # Update the pygame.Rect object





class CircleCollider(Collider):
    def __init__(self, center=(0, 0), radius=1, **kwargs):
        super().__init__(center, **kwargs)
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
        return self.collider.center

    @position.setter
    @recordable
    def position(self, value):
        self.collider.center = value

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
    
    def move(self):
        # Use events to update position, angle, etc., based on the new event structure.
        time_key = str(self.game.time)
        if time_key in self.events:
            for event in self.events[time_key]:
                if event["type"] == "deltaSetter":
                    attribute = event["attribute"]
                    value = event["value"]
                    # Ensure 'position' is a tuple before setting it
                    if attribute == "position":
                        value = tuple(value)
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
        bounding_box_size = (200, 400)  # Example size
        # Adjust bounding_rect initialization as needed to fit the game's logic
        bounding_rect = pygame.Rect(position[0] - bounding_box_size[0] / 2,
                                    position[1] - bounding_box_size[1] / 2,
                                    *bounding_box_size)
        collider = RectCollider(center=position, size=bounding_box_size, angle=angle)
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

def draw_rotated_box(screen, rect, angle, color):
        # Calculate the angle in radians
        radians = math.radians(angle)
        
        # Calculate the four corners of the rotated rectangle
        corners = [
            (rect.centerx + math.cos(radians) * rect.width / 2 - math.sin(radians) * rect.height / 2,
            rect.centery + math.sin(radians) * rect.width / 2 + math.cos(radians) * rect.height / 2),
            (rect.centerx - math.cos(radians) * rect.width / 2 - math.sin(radians) * rect.height / 2,
            rect.centery - math.sin(radians) * rect.width / 2 + math.cos(radians) * rect.height / 2),
            (rect.centerx - math.cos(radians) * rect.width / 2 + math.sin(radians) * rect.height / 2,
            rect.centery - math.sin(radians) * rect.width / 2 - math.cos(radians) * rect.height / 2),
            (rect.centerx + math.cos(radians) * rect.width / 2 + math.sin(radians) * rect.height / 2,
            rect.centery + math.sin(radians) * rect.width / 2 - math.cos(radians) * rect.height / 2)
        ]
        
        # Draw the polygon on the screen
        pygame.draw.polygon(screen, color, corners)

class PlaybackCreature(PlaybackGameObject, BaseCreature):
    def __init__(self, playback_id, health, position, speed, name, angle, events, collider, scale_size, scale_position):
        self.scale_size = scale_size
        self.scale_position = scale_position
        PlaybackGameObject.__init__(self, playback_id, position, angle, events)
        BaseCreature.__init__(self, health, speed, name)
        self.collider = collider  # Use the provided collider
        # Load the image only once in the constructor
        self.image = pygame.image.load('assets/car1.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, self.collider.size)  # Scale to match the collider size



    def draw(self, screen, convert_to_screen):
        # Convert the collider's center to screen coordinates
        screen_center = convert_to_screen(self.collider.center)

        # Draw the sprite
        rotated_image = pygame.transform.rotate(self.image, -self.angle + 90)
        new_rect = rotated_image.get_rect(center=screen_center)
        screen.blit(rotated_image, new_rect.topleft)

        # Draw the triangle pointer
        radians = math.radians(self.angle)
        base_length = 10  # Smaller size for the triangle pointer
        triangle_height = (math.sqrt(3) / 2) * base_length
        front_point = (screen_center[0] + math.cos(radians) * triangle_height, screen_center[1] + math.sin(radians) * triangle_height)
        back_center_point = (screen_center[0] - math.cos(radians) * triangle_height / 2, screen_center[1] - math.sin(radians) * triangle_height / 2)
        left_point = (back_center_point[0] + math.cos(radians + math.pi / 2) * (base_length / 2), back_center_point[1] + math.sin(radians + math.pi / 2) * (base_length / 2))
        right_point = (back_center_point[0] + math.cos(radians - math.pi / 2) * (base_length / 2), back_center_point[1] + math.sin(radians - math.pi / 2) * (base_length / 2))
        triangle_points = [front_point, left_point, right_point]
        pygame.draw.polygon(screen, (255, 255, 255), triangle_points)

        if self.game.show_bounding_boxes:
            # Scale size and scale position
            scaled_size = self.scale_size(self.collider.size)
            scaled_center = self.scale_position(self.collider.center)

            # Calculate the corners of the bounding box relative to its center
            corners = [
                (-scaled_size[0]/2, -scaled_size[1]/2),
                (scaled_size[0]/2, -scaled_size[1]/2),
                (scaled_size[0]/2, scaled_size[1]/2),
                (-scaled_size[0]/2, scaled_size[1]/2),
            ]
            
            # Rotate and translate corners
            rotated_corners = []
            for (x, y) in corners:
                # Rotate
                rotated_x = x * math.cos(math.radians(-self.angle)) - y * math.sin(math.radians(-self.angle))
                rotated_y = x * math.sin(math.radians(-self.angle)) + y * math.cos(math.radians(-self.angle))
                # Translate
                screen_x, screen_y = convert_to_screen((rotated_x + self.collider.center[0], rotated_y + self.collider.center[1]))
                rotated_corners.append((screen_x, screen_y))

            # Draw the bounding box
            pygame.draw.polygon(screen, self.color, rotated_corners, 1)






class Game:
    def __init__(self, arena):
        self.arena = arena
        self.game_objects = []  # Initialized but can be populated by derived classes
        self.time = -1

    def add_creature(self, creature):
        self.game_objects.append(creature)  # Add the creature to the game's list of creatures
        creature.set_game(self)  # Set this game instance as the creature's game

    def set_game_for_creatures(self):
        for game_objects in self.game_objects:
            game_objects.set_game(self)



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
    def __init__(self, arena, creatures = None):
        super().__init__(arena)
        self.game_objects = creatures
        if(creatures):
            self.set_game_for_creatures()  # Call the set_game_for_creatures() method on self
        
    

    def simulate_turn(self):
        if self.time == -1:
            self.time = 0  # Start the game
        arena_center = (self.arena.width / 2, self.arena.height / 2)
        for creature in self.game_objects:
            creature.think(arena_center)  # Let each creature decide its move
            creature.move(self.arena, self.time)
        self.time += 1




    def record_game(self, filename):

        header = {
        "arena": {"width": self.arena.width, "height": self.arena.height},
        "creatures": [
            {
                "id": creature.id,
                "health": creature.health,
                "position": creature.initial_position,
                "speed": creature.speed,
                "name": creature.name,
                "angle": creature.angle,
                "color": creature.color,
                "size": (creature.collider.rect.width, creature.collider.rect.height)
            } for creature in self.game_objects
        ],
    }

        # Collect events from all turns; each creature manages its own events
        events = {}
        for creature in self.game_objects:
            for time_index, event_list in creature.events.items():
                if time_index not in events:
                    events[time_index] = []
                events[time_index].extend(event_list)

        # Use the serialize_events function to prepare events for serialization
        events = serialize_events(events)

        game_record = {"header": header, "events": events}
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=4)

