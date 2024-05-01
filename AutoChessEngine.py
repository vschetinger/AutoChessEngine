import json
import math
import random
import pygame
from collections import deque
import copy
import copy

class Arena:
    def __init__(self, width, height):
        self.width = width
        self.height = height


def recordable_field(method):
    def wrapper(self, *args, **kwargs):
        # Check if _internal_id is set before proceeding
        if (hasattr(self, '_internal_id') and self._internal_id and 
            Game.get_time() >= 0):
            result = method(self, *args, **kwargs)

            # Prepare the attribute name
            attribute_name = method.__name__.replace("set_", "")

            # Prepare the value to record
            value_to_record = kwargs.get('value', args[0] if args else None)

            # Generate the event
            event = {
                "type": "deltaSetter",
                "id": self.id, # Assuming self.id is correctly set
                "attribute": attribute_name,
                "value": value_to_record
            }

            # Record the event through the game object
            self.game.record_event(event)

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


    def get_vertices(self):
            # Calculate the four corners of the rotated rectangle
            rad = math.radians(self._angle)
            cos_rad = math.cos(rad)
            sin_rad = math.sin(rad)
            w, h = self._size
            cx, cy = self._center

            # Corners relative to the center
            corners = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]

            # Rotate and translate corners
            return [(cx + cos_rad * x - sin_rad * y, cy + sin_rad * x + cos_rad * y) for x, y in corners]

    def check_collision(self, other):
        Game.increment_collision_checks()
        if isinstance(other, RectCollider):
            return self._obb_collision(other)

    def _obb_collision(self, other):
        # Calculate the axes for the first OBB
        axes1 = self._get_obb_axes()
        # Calculate the axes for the second OBB
        axes2 = other._get_obb_axes()

        # Check for overlap on each axis
        for axis in axes1 + axes2:
            if not self._overlap_on_axis(other, axis):
                return False

        return True

    def _get_obb_axes(self):
        # Calculate the axes of the OBB based on its angle
        rad = math.radians(self.angle)
        cos_rad = math.cos(rad)
        sin_rad = math.sin(rad)
        return [(cos_rad, sin_rad), (-sin_rad, cos_rad)]

    def _overlap_on_axis(self, other, axis):
        # Project the OBBs onto the axis
        self_vertices = self.get_vertices()
        other_vertices = other.get_vertices()
        self_min, self_max = self._project_onto_axis(self_vertices, axis)
        other_min, other_max = self._project_onto_axis(other_vertices, axis)

        # Check for overlap
        if self_max < other_min or other_max < self_min:
            return False

        return True

    def _project_onto_axis(self, vertices, axis):
        min_projection = float('inf')
        max_projection = float('-inf')

        for vertex in vertices:
            projection = vertex[0] * axis[0] + vertex[1] * axis[1]
            min_projection = min(min_projection, projection)
            max_projection = max(max_projection, projection)

        return min_projection, max_projection
    
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
    def __init__(self, position, angle, game = None, collider=None, **kwargs):
        
        if collider is None:
            self.collider = Collider(position, angle)
        else:
            self.collider = collider
        self.position = position
        self.initial_position = position  # Use copy() if it's a mutable object like a list or dict
        self.angle = angle
        self.initial_angle = angle
        self.game = game

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

    @recordable_field
    def set_position(self, x, y):
        self.collider.position((x, y))

    @recordable_field
    def set_angle(self, angle):
        self.collider.angle = (angle % 360)  # Normalize the angle

    @property
    def id(self):
        return self._internal_id  # Return the id that was generated in __init__
    
    @property
    def position(self):
        return self.collider.center

    @position.setter
    @recordable_field
    def position(self, value):
        self.collider.center = value

    @property
    def angle(self):
        return self.collider.angle

    @angle.setter
    @recordable_field
    def angle(self, value):
        self.collider.angle = (value % 360)  # Normalize the angle

    def die(self):
        # print(f"{Game.get_time()} ====={self.id}=== has died! Class: {self.__class__.__name__}")
        event = {
            "type": "destruction",
            "id": self.id,
            "final_position": self.position
        }
        self.game.record_event(event)
        self.game.remove_game_object(self)

class SimulationGameObject(GameObject):
    def __init__(self, position, angle, game = None,collider=None,  **kwargs):
        super().__init__(position, angle,game=game, collider=collider, **kwargs)  # Now correctly forwards expected arguments
        # self._internal_id = id(self)  # Unique internal ID (using Python's built-in id())
        self.action_plan = deque()
        self.events = {}


    # Could be powerful, but its behaving crazy
    # def __deepcopy__(self, memo):
    #     # Create a new instance of the class without calling __init__
    #     cls = self.__class__
    #     copied_obj = cls.__new__(cls)
    #     memo[id(self)] = copied_obj

    #     # Copy all attributes except _internal_id
    #     for k, v in self.__dict__.items():
    #         if k != '_internal_id':
    #             setattr(copied_obj, k, copy.deepcopy(v, memo))

    #     # Generate a new unique identifier for the copied object
    #     copied_obj._internal_id = id(copied_obj)


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
        time_key = str(Game.get_time())
        if time_key in self.events:
            for event in self.events[time_key]:
                if event["type"] == "deltaSetter":
                    attribute = event["attribute"]
                    value = event["value"]
                    # Ensure 'position' is a tuple before setting it
                    if attribute == "position" or attribute == "target":
                        value = tuple(value)
                    # Update the score attribute
                    elif attribute == "score":
                        self.score = value
                    # Update the attribute based on the event information.
                    setattr(self, attribute, value)


    def draw(self, *args, **kwargs):
        # Placeholder for draw, to be overridden by subclasses
        pass


class BaseCreature:
    def __init__(self, health, speed, bullet_range, name, shoot_cooldown=0, brake_power=0.8, brake_cooldown=30):
        self.max_health = health 
        #TODO: will this be a problem for deltaSetters?   
        self._health = health
        self.speed = speed
        self.name = name
        self.bullet_range = bullet_range
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.shoot_timer = 0 
        self.shoot_cooldown = shoot_cooldown 
        self._score = 0
        self.brake_power = brake_power
        self.brake_cooldown = brake_cooldown

    @recordable_field
    def set_target(self, target):
        self.target = target

    @property
    def health(self):
        return self._health

    @health.setter
    @recordable_field
    def health(self, value):
        self._health = value

    @property
    def score(self):
        return self._score

    @score.setter
    @recordable_field
    def score(self, value):
        self._score = value


class SimulationCreature(SimulationGameObject, BaseCreature):
    def __init__(self, position, angle, health, speed, name, max_turn_rate, shoot_cooldown, bounding_box_size, damage, bullet_speed, bullet_range, brake_power, brake_cooldown, sprite_filename, events=None, **kwargs):
            # Adjust bounding_rect initialization as needed to fit the game's logic
            collider = RectCollider(center=position, size=bounding_box_size, angle=angle)
            super().__init__(position, angle, collider=collider, **kwargs)
            BaseCreature.__init__(self, health, speed,bullet_range, name,shoot_cooldown,brake_power,brake_cooldown, **kwargs)

            # Assign the id before any other operations
            self._internal_id = self.game.generate_id() if self.game else None

            self.sprite_filename = sprite_filename

            self.max_turn_rate = max_turn_rate
            self.shoot_cooldown = shoot_cooldown
            self.damage = damage
            self.bullet_speed = bullet_speed
            self.original_speed = speed
            self.brake_timer = 0
            self._is_braking = False  # Initialize _is_braking attribute to False


            self.events = events or {}

            self.target = None

    @property
    def is_braking(self):
        return self._is_braking

    @is_braking.setter
    @recordable_field
    def is_braking(self, value):
        self._is_braking = value


    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'angle': self.angle,
            'health': self.health,
            'speed': self.speed,
            'name': self.name,
            'max_turn_rate': self.max_turn_rate,
            'shoot_cooldown': self.shoot_cooldown,
            'size': (self.collider.rect.width, self.collider.rect.height),
            'damage': self.damage,
            'bullet_speed': self.bullet_speed,
            'bullet_range': self.bullet_range,
            'score': self.score,
            'brake_power': self.brake_power,
            'brake_cooldown': self.brake_cooldown,
            'sprite_filename': self.sprite_filename,
            'score_values': self.game.score_values,  # Include the score_values from the game
        }

    def take_damage(self, damage, attacker_id):
        self.health -= damage
        self.score += self.game.score_values["hit_taken"]  # Deduct points for getting hit

        attacker = self.game.get_game_object_by_id(attacker_id)
        if attacker:
            attacker.score += self.game.score_values["hit_given"]  # Add points for hitting someone

        if self.health <= 0:
            self.die()
            self.score += self.game.score_values["death"]  # Deduct points for dying

            if attacker:
                attacker.score += self.game.score_values["kill"]  # Add points for killing someone

    def find_nearest_creature(self):
        nearest_distance = float('inf')
        nearest_creature = None
        for game_object in self.game.game_objects:
            if isinstance(game_object, SimulationCreature) and game_object != self:
                distance = math.hypot(game_object.position[0] - self.position[0], game_object.position[1] - self.position[1])
                if distance < nearest_distance:
                    nearest_creature = game_object
                    nearest_distance = distance
        return nearest_creature
    

    def think(self):
        nearest = self.find_nearest_creature()
        if nearest:
            self.set_target(nearest.position)
            distance_to_target = math.hypot(nearest.position[0] - self.position[0], nearest.position[1] - self.position[1])
            if distance_to_target <= self.bullet_range and self.brake_timer == 0 and self.is_braking == False:
                self.action_plan.append(('brake', None))  # Add brake action to the queue
        else:
            arena_center = (self.game.arena.width / 2, self.game.arena.height / 2)
            self.set_target(arena_center)
        if ('blocked', None) in self.action_plan:
            self.action_plan.remove(('blocked', None))
            self.action_plan.append(('reverse', None))
        # Example logic to add 'turn' action every turn and 'shoot' action if cooldown allows
        if self.target is not None:
            self.action_plan.append(('turn', self.calculate_turn(self.target)))
        if self.shoot_timer <= 0 and distance_to_target <= self.bullet_range:  # Can shoot if shoot_timer is 0 or less
            self.action_plan.append(('shoot', None))
            # print(f"{self.id} aiming!")
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

    def shoot(self):
        # Create a new bullet instance each time it's called
        bullet_body = RectCollider(self.position,(2, 2), self.angle)
        new_bullet = SimulationProjectile(self.position, self.angle, self.bullet_speed, self.id,self.damage, self.bullet_range,self.game, bullet_body)
        # Record the creation event explicitly
        
        self.game.add_game_object(new_bullet) # Add the new bullet to the game
        event = {
                    "type": "creation",
                    "id": new_bullet.id,
                    "object_type": new_bullet.type_identifier,
                    "origin_id": new_bullet.origin_id,
                    "details": {
                        "position": new_bullet.position,
                        "angle": new_bullet.angle,
                        "speed": new_bullet.speed,
                        "size": new_bullet.collider.size
                    }
                }

        self.game.record_event(event)
        # print(f"===T:{Game.get_time()}==={self.id} shots fired!")

    def move(self):
        temp_collider = copy.deepcopy(self.collider)

        while self.action_plan:
            action, value = self.action_plan.popleft()  # Pop the first action
            if action == 'reverse':
                self.angle += 180
            elif action == 'turn':
                self.angle += value
            elif action == 'shoot':
                # print(f"{self.id} gun cocked!")
                self.shoot()
            elif action == 'brake':
                self.is_braking = True
                # print(f"Creature {self.id} started braking")


        if self.is_braking:
            self.speed *= self.brake_power
            # print(f"Creature {self.id} is braking. Current speed: {self.speed}")
            if abs(self.speed) < 5:  # Adjust the threshold as needed
                self.speed = 0
                self.brake_timer = self.brake_cooldown
                self.is_braking = False  # Set the braking state to False when speed is close to 0
                # print(f"Creature {self.id} finished braking. Speed set to 0. Brake timer set to {self.brake_cooldown}")
        else:
            self.speed = self.original_speed
            # print(f"Creature {self.id} is not braking. Speed set to {self.original_speed}")
    


        # Calculate the potential new position
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        new_position = (new_x, new_y)

        # Create a copy of the collider for collision checking
        temp_collider.center = new_position

        # Check for collisions with other creatures
        will_collide = False
        for other in self.game.game_objects:
            if other is not self and temp_collider.check_collision(other.collider):
                if isinstance(other, SimulationProjectile) and other.origin_id != self.id:
                    will_collide = True
                    self.take_damage(other.damage, other.origin_id)  # Pass the origin_id to take_damage
                    other.die()
                    # print(f"Collision detected between {self.id} and {other.id}")
                    break
                elif isinstance(other, SimulationCreature) and other.id != self.id:
                    will_collide = True
                    # print(f"Collision detected between {self.id} and {other.id}")
                    break

        # Check for collisions with arena walls
        arena_bounds = pygame.Rect(0, 0, self.game.arena.width, self.game.arena.height)
        if not arena_bounds.contains(temp_collider.rect):
            will_collide = True  # Set collision flag for arena boundary collision

        # If no collision is detected, update the actual position and collider
        if not will_collide:
            if self.action_plan:
                self.action_plan.popleft()  # Remove the action after processing
            self.position = new_position  # Update position if no collision
        else:
            # Handle collision (e.g., stop movement, bounce back, etc.)
            # For now, we just clear the action plan to simulate stopping
            self.action_plan.clear()
            self.action_plan.append(('blocked', None))

        # Decrement the shoot timer if it's greater than 0
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

            # Decrement the shoot timer if it's greater than 0
 
        if self.brake_timer > 0:
            self.brake_timer -= 1


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
    def __init__(self, playback_id, health, position, speed, name,sprite, angle,bullet_range, events, collider, scale_size, scale_position, shoot_cooldown, score):
        self.scale_size = scale_size
        self.scale_position = scale_position
        PlaybackGameObject.__init__(self, playback_id, position, angle, events)
        BaseCreature.__init__(self, health, speed,bullet_range, name, shoot_cooldown)
        self.collider = collider  # Use the provided collider
        # Load the image only once in the constructor

        #self.image = pygame.image.load('assets/car1.png').convert_alpha()
        self.sprite = sprite
        self.sprite = pygame.transform.scale(self.sprite, self.collider.size)  # Scale to match the collider size

        self._is_braking = False  # Initialize _is_braking attribute to False

    @property
    def is_braking(self):
        return self._is_braking

    @is_braking.setter
    def is_braking(self, value):
        self._is_braking = value


    def draw(self, screen, convert_to_screen):
        # Convert the collider's center to screen coordinates
        screen_center = convert_to_screen(self.collider.center)

        # Draw the sprite
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.angle + 90)
        new_rect = rotated_sprite.get_rect(center=screen_center)
        screen.blit(rotated_sprite, new_rect.topleft)
        

        # Draw the triangle pointer
        radians = math.radians(self.angle)
        base_length = 10  # Smaller size for the triangle pointer
        triangle_height = (math.sqrt(3) / 2) * base_length
        front_point = (screen_center[0] + math.cos(radians) * triangle_height, screen_center[1] + math.sin(radians) * triangle_height)
        back_center_point = (screen_center[0] - math.cos(radians) * triangle_height / 2, screen_center[1] - math.sin(radians) * triangle_height / 2)
        left_point = (back_center_point[0] + math.cos(radians + math.pi / 2) * (base_length / 2), back_center_point[1] + math.sin(radians + math.pi / 2) * (base_length / 2))
        right_point = (back_center_point[0] + math.cos(radians - math.pi / 2) * (base_length / 2), back_center_point[1] + math.sin(radians - math.pi / 2) * (base_length / 2))
        triangle_points = [front_point, left_point, right_point]
        pygame.draw.polygon(screen, self.color, triangle_points)

        if self.game.show_bounding_boxes:
            # Create a surface for the bounding box with the same size as the collider
            bbox_surface = pygame.Surface(self.collider.size, pygame.SRCALPHA)
            bbox_surface.fill((0, 0, 0, 0))  # Fill with transparent color
            pygame.draw.rect(bbox_surface, self.color, bbox_surface.get_rect(), 1)
            # Apply the same transformations as the sprite: scale and rotate
            #scaled_bbox_surface = pygame.transform.scale(bbox_surface, self.scale_size(self.collider.size))
            rotated_bbox_surface = pygame.transform.rotate(bbox_surface, -self.angle + 90)

            # Use the same center as the sprite for positioning
            bbox_rect = rotated_bbox_surface.get_rect(center=screen_center)
            screen.blit(rotated_bbox_surface, bbox_rect.topleft)

        if self.game.draw_shooting_ranges:
            screen_center = convert_to_screen(self.collider.center)
            scaled_size = self.scale_size((self.bullet_range, self.bullet_range)) # Convert the bullet range to screen coordinates
            screen_bullet_range = scaled_size[0] # Use the scaled width as the radius

            # Calculate the angle of the arc based on the cooldown timer
            cooldown_ratio = self.shoot_timer / self.shoot_cooldown if self.shoot_cooldown else 0
            arc_angle = 360 * cooldown_ratio

            # print(f"Creature ID: {self.id}, shoot_timer: {self.shoot_timer}, shoot_cooldown: {self.shoot_cooldown}, cooldown_ratio: {cooldown_ratio}, arc_angle: {arc_angle}")


            # Draw the arc representing the shooting cooldown
            pygame.draw.arc(screen, self.color, pygame.Rect(screen_center[0] - screen_bullet_range, screen_center[1] - screen_bullet_range, screen_bullet_range * 2, screen_bullet_range * 2), 0, math.radians(arc_angle), width=1)

        
        health_bar_height = 3 # Height of the health bar
        health_bar_width = self.collider.size[0] # Width of the health bar
        if self.max_health != 0:
            health_ratio = self.health / self.max_health
        else:
            health_ratio = 0
        health_bar_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.25 else (255, 0, 0) # Change color based on health

        pygame.draw.rect(screen, health_bar_color, (screen_center[0] - health_bar_width / 2, screen_center[1] - health_bar_height - 10, health_bar_width * health_ratio, health_bar_height))
                
        # Draw the score above the creature's head
        score_text = str(self.score)
        score_font = pygame.font.Font(None, 24)  # Adjust the font size as needed
        score_surface = score_font.render(score_text, True, (255, 255, 255))  # White color
        score_rect = score_surface.get_rect(center=(screen_center[0], screen_center[1] - 30))  # Adjust the vertical position as needed
        screen.blit(score_surface, score_rect)

        # Draw the "brake!" text under the creature when braking
        if self.is_braking:
            brake_text = "brake!"
            brake_font = pygame.font.Font(None, 18)  # Adjust the font size as needed (smaller than score)
            brake_color = (255, 0, 0)  # Red color
            brake_surface = brake_font.render(brake_text, True, brake_color)
            brake_rect = brake_surface.get_rect(center=(screen_center[0], screen_center[1] + 30))  # Adjust the vertical position as needed
            screen.blit(brake_surface, brake_rect)


        # Because this timer is only used for drawing, it doesn't need to be updated in the move method
        if self.shoot_timer < self.shoot_cooldown:
            self.shoot_timer += 1



class BaseProjectile:
    def __init__(self, speed, origin_id, **kwargs):
        self.speed = speed
        # Store the origin (id of creator game_object) of the projectile
        self.origin_id = origin_id

    def move(self):
        # Logic to move the projectile forward
        pass

    def think(self):
        # Additional logic if needed
        pass

    @property
    def type_identifier(self):
        return "Projectile"

    @classmethod
    def from_existing(cls, existing_projectile):
        # Create a new instance by copying the existing one
        new_projectile = copy.deepcopy(existing_projectile)
        # Assign the id after the object is fully initialized
        new_projectile._internal_id = existing_projectile.game.generate_id() # Use the game's generate_id method
        new_projectile.id = new_projectile._internal_id # Ensure the id property is updated
        return new_projectile



class SimulationProjectile(SimulationGameObject, BaseProjectile):
    def __init__(self, position, angle, speed, origin_id,damage,range, game, collider=None, **kwargs):
        # Assign the id before any other operations
        #self._internal_id = game.generate_id() if game else None
        # If a collider is provided, deep copy it to ensure each projectile has its own
        self.damage = damage
        self.range = range
        if collider is not None:
            self.collider = copy.deepcopy(collider)
        else:
            # Create a new collider if none is provided
            self.collider = RectCollider(center=position, angle=angle, size=(10, 10))

        # Set the game attribute before calling the super constructor
        self.game = game

        super().__init__(position, angle, game, collider=self.collider, **kwargs)
        BaseProjectile.__init__(self, speed, origin_id, **kwargs)
        # Move the print statement after the id has been assigned
        # print(f"Projectile {self.id} created!")
        self.start_position = position
    
    def set_color_from_origin(self, game):
        # Retrieve the origin creature using the game's get_game_object_by_id method
        origin_creature = game.get_game_object_by_id(self.origin_id)
        if origin_creature:
            # Set the color of the projectile to the color of the origin creature
            self.color = origin_creature.color
        else:
            # Handle the case where the origin creature is not found
            # You can set a default color or raise an error
            self.color = (255, 255, 255) # Default color (white)

    def think(self):
        # Placeholder for think, to be overridden by subclasses
        pass

    def move(self):
        radians = math.radians(self.angle)
        dx = math.cos(radians) * self.speed
        dy = math.sin(radians) * self.speed
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        new_position = (new_x, new_y)

        # Check if the distance between start_position and new_position is larger than the bullet's range
        distance_run = math.sqrt((new_position[0] - self.start_position[0])**2 + (new_position[1] - self.start_position[1])**2)
        
        if distance_run > self.range:
            self.die()

        # Check for collisions with the arena walls
        arena_bounds = pygame.Rect(0, 0, self.game.arena.width, self.game.arena.height)
        if not arena_bounds.contains(self.collider.rect):
            # If the projectile is outside the arena, it dies
            self.die()
            return

        # Update the position if no collision with the arena walls
        self.position = new_position

        # Check for collisions with other game objects
        for game_object in self.game.game_objects:
            if isinstance(game_object, SimulationProjectile):
                if self.collider.check_collision(game_object.collider) and self.origin_id != game_object.origin_id and self.id != game_object.id:
                    game_object.die()
                    self.die()
            elif isinstance(game_object, SimulationCreature):
                if self.collider.check_collision(game_object.collider) and self.origin_id != game_object.id and self.id != game_object.id:
                    game_object.take_damage(self.damage, self.origin_id)  # Pass the origin_id as the attacker_id
                    self.die()

    
    @property
    def id(self):
        return self._internal_id # Return the id that was generated in __init__

    @id.setter
    def id(self, value):
        self._internal_id = value # Set the internal id to the new value


class PlaybackProjectile(PlaybackGameObject, BaseProjectile):
    def __init__(self, playback_id,origin_id, position, angle, speed,  events, collider=None,color = None, scale_size=None, scale_position=None):
        self.scale_size = scale_size
        self.scale_position = scale_position
        self.color = color
        PlaybackGameObject.__init__(self, playback_id, position, angle, events)
        BaseProjectile.__init__(self, speed,origin_id)
        if collider is not None:
            self.collider = collider
        self.start_position = position

    def draw(self, screen, convert_to_screen=None):

            # Convert the position to screen coordinates if necessary
            if convert_to_screen:
                screen_position = convert_to_screen(self.position)
            else:
                screen_position = self.position

            # Draw the trail
            if self.start_position: # Assuming start_position is a class attribute
                start_position_screen = convert_to_screen(self.start_position) if convert_to_screen else self.start_position
                pygame.draw.line(screen, (255, 255, 255), start_position_screen, screen_position, 1) # Draw a white line
            # Create the rectangle at origin, then rotate and move to the correct position
            unrotated_rect = pygame.Rect(0, 0, *self.collider.size)
            rotated_rect = pygame.transform.rotate(pygame.Surface(unrotated_rect.size), -self.angle).get_rect()
            rotated_rect.center = screen_position

            # Draw the rectangle
            pygame.draw.rect(screen, self.color, rotated_rect)

#TODO make Game proper singleton and remove the self.game references
class Game:
    _time = -1
    _collision_checks = 0 # Static counter for collision checks

    def __init__(self, arena):
        self.arena = arena
        self.game_objects = []  # Initialized but can be populated by derived classes
        self.cemetery = []
        self.global_events = {}
        self.winner = None

    @classmethod
    def update_time(cls):
        cls._time += 1

    @classmethod
    def get_time(cls):
        return cls._time
    
    @classmethod
    def reset_time(cls):
        cls._time = 0

    @classmethod
    def increment_collision_checks(cls):
        """Increment the static collision check counter."""
        cls._collision_checks += 1

    @classmethod
    def get_collision_checks(cls):
        """Get the current number of collision checks."""
        return cls._collision_checks

    @classmethod
    def reset_collision_checks(cls):
        """Reset the static collision check counter."""
        cls._collision_checks = 0

    def get_game_object_by_id(self, object_id):
        for game_object in self.game_objects:
            if game_object.id == object_id:
                return game_object
        return None


    def add_game_object(self, creature):
        """Add a game object and assign it a unique ID."""
        self.game_objects.append(creature)
        creature.set_game(self)

    def set_game_for_creatures(self):
        for game_objects in self.game_objects:
            game_objects.set_game(self)

    # Removed objects always go to the cemetery
    # However, Simulation and Playback games may handle them differently
    def remove_game_object(self, obj):
        if obj in self.game_objects:
            self.cemetery.append(obj)
            self.game_objects.remove(obj)

    def record_event(self, event):
        # This method will be called by all game objects to record their events
        time_index = Game.get_time()
        if time_index not in self.global_events:
            self.global_events[time_index] = []
        self.global_events[time_index].append(event)



# Example of converting a complex object to a serializable format
def serialize_events(events):
    serialized_events = {}
    for time_index, event_list in events.items():
        serialized_events[time_index] = []
        for event in event_list:
            if event["type"] == "creation":
                serialized_event = {
                    'origin_id': event["origin_id"],  
                    "type": event["type"],
                    "id": event["id"],
                    "object_type": event["object_type"],
                    "details": event["details"]
                }
            elif event["type"] == "destruction":
                serialized_event = {
                    "type": event["type"],
                    "id": event["id"],
                    "final_position": event["final_position"]
                }
            else:
                serialized_event = {
                    "type": event["type"],
                    "id": event["id"],
                    "attribute": event["attribute"],
                    "value": event["value"]
                }
            serialized_events[time_index].append(serialized_event)
    return serialized_events


class SimulationGame(Game):
    def __init__(self, arena, creatures=None, experiment_hash=None):
        super().__init__(arena)
        self.game_objects = creatures
        self.creature_counts = {}
        self.id_counter = 1
        if creatures:
            self.set_game_for_creatures()
        self.score_values = {
            "hit_taken": -2,
            "hit_given": 5,
            "death": -20,
            "kill": 30,
        }
        self.experiment_hash = experiment_hash  # Store the experiment_hash
        
    def generate_id(self):
        """Generate a new unique ID."""
        new_id = self.id_counter
        self.id_counter += 1
        return new_id

    def remove_game_object(self, obj):
        if obj in self.game_objects:
            self.cemetery.append(obj)
            self.game_objects.remove(obj)

    def simulate_turn(self):
        if Game.get_time() == -1:
            Game.update_time() # Start the game
        # print(f"===T: {Game.get_time()} ========")
        # print(f"Collision checks: {Game._collision_checks}")
        Game.reset_collision_checks() 
        for game_object in self.game_objects:
            game_object.think()  # Let each creature decide its move
            game_object.move()
        Game.update_time()  # Increment the time after all creatures have moved

    def add_game_object(self, object):
        object._internal_id = self.generate_id()
        object = super().add_game_object(object)



    def record_game(self, filename):
        # Bring the cemetery back for recording
        self.game_objects.extend([obj for obj in self.cemetery if isinstance(obj, BaseCreature)])

        # Serialize the creatures
        creatures_data = [creature.to_dict() for creature in self.game_objects if isinstance(creature, SimulationCreature)]

        # Serialize the events
        events = serialize_events(self.global_events)

        winner_creature = None
        if self.winner:
            for creature in self.game_objects:
                if isinstance(creature, SimulationCreature) and creature.name == self.winner:
                    winner_creature = creature
                    break

        # Prepare the game record
        game_record = {
            "header": {
                "arena": {"width": self.arena.width, "height": self.arena.height},
                "winner": self.winner.split(' ')[0] if self.winner else None,
                "winner_score": winner_creature.score if winner_creature else None,
                "creatures": creatures_data,  # Include the serialized creatures
                "score_values": self.score_values,  # Include the score_values dictionary
            },
            "experiment_hash": self.experiment_hash,  # Include the experiment_hash
            "events": events,
        }

        # Save the game record to a JSON file
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=4)

        # Save the game record to a JSON file
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=4)


