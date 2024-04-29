# No need to import Creature directly if it's not used here
import json
import sys
from AutoChessEngine import *
from moviepy.editor import ImageSequenceClip
from PIL import Image
import glob
import os
import pygame
import moviepy
import argparse


class SpriteManager:
    def __init__(self):
        self.loaded_sprites = {}

    def get_sprite(self, sprite_filename):
        if sprite_filename not in self.loaded_sprites:
            sprite_path = os.path.join('assets', sprite_filename)
            if os.path.exists(sprite_path):
                self.loaded_sprites[sprite_filename] = pygame.image.load(sprite_path).convert_alpha()
            else:
                self.loaded_sprites[sprite_filename] = None
        return self.loaded_sprites[sprite_filename]

class PlaybackGame(Game):
    def __init__(self, arena,battle_log=None):
        super().__init__(arena)
        self.set_game_for_creatures()
        self.show_bounding_boxes = True  # Start with bounding boxes
        self.draw_shooting_ranges = True  # Start with shooting ranges
        self.battle_log = battle_log
        

    def toggle_bounding_boxes(self):
        self.show_bounding_boxes = not self.show_bounding_boxes

    def toggle_shooting_ranges(self):
            self.draw_shooting_ranges = not self.draw_shooting_ranges
    
    # Now handling only all creatures, should handle all kinds of events later
    def update_from_events(self):
        current_events = self.global_events.get(str(Game.get_time()), [])

        for event in current_events:
            if event['type'] == 'creation':
                # Get the class for the object type
                class_name = "Playback" + event['object_type']
                object_class = globals().get(class_name)
                if object_class is not None:
                    # Extract the required details
                    details = event['details']
                    playback_id = event['id']
                    position = details.get('position')
                    angle = details.get('angle')
                    speed = details.get('speed')
                    size = details.get('size')
                    origin_id = event.get('origin_id')

                    # Extract all events for this playback_id, indexed by time
                    event_dict = {time: [event for event in self.battle_log['events'][time] if event['id'] == playback_id] 
                            for time in self.battle_log['events']}

                    # Filter out times with no events for this playback_id
                    event_dict = {time: events for time, events in event_dict.items() if events}

                    # Create a new object and add it to game_objects
                    collider = RectCollider(position, size, angle)
                    color = self.get_game_object_by_id(origin_id).color
                    new_object = object_class(playback_id,origin_id, position, angle, speed, event_dict, collider,color)
                    # self.game_objects.append(new_object)
                    self.add_game_object(new_object)
                    creature_of_origin = self.get_game_object_by_id(origin_id)
                    creature_of_origin.shoot_timer = 0 # Reset the shoot timer for the origin creature

            elif event['type'] == 'destruction':
                # Move the destroyed object to the cemetery
                destroyed_object = next((obj for obj in self.game_objects if obj.id == event['id']), None)
                if destroyed_object:
                    self.game_objects.remove(destroyed_object)
                    self.cemetery.append(destroyed_object)

        for game_object in self.game_objects:
            game_object.move()

        

    def reset_objects(self):

        # Reset each creature to its initial state at the start of the playback loop
        for creature in self.cemetery:
            if isinstance(creature, PlaybackCreature): # Check if the object is a PlaybackCreature
                creature.reset_to_initial_state()
                self.game_objects.append(creature)
        self.game_objects = [obj for obj in self.game_objects if isinstance(obj, PlaybackCreature)]
        # The game_objects now only contains PlaybackCreatures
        self.cemetery.clear()
        

class AutoChessPlayer:
    def __init__(self, battle_log_path, screen_size=(800, 800), offset=(80, 80), canvas_dimensions=(670, 670), output_image=False, render=True):
        with open(battle_log_path, 'r') as f:
            self.battle_log = json.load(f)

        # Original arena dimensions from the JSON file
        original_arena_dimensions = self.battle_log['header']['arena']
        # For clarity, storing original dimensions separately
        self.original_arena_width = original_arena_dimensions['width']
        self.original_arena_height = original_arena_dimensions['height']

        # Will the the generate_frame method spit images? T or F
        self.output_image = output_image
        self.frames = []  # List to store frames in memory
        # Will the game be rendered? T or F
        self.render = render

        
        self.sprite_manager = SpriteManager()  # Create an instance of the SpriteManager


        # Setting the canvas dimensions based on the input parameter
        self.canvas_dimensions = canvas_dimensions
        self.screen_size = screen_size
        self.offset = offset
        self.scale_ratio = self.calculate_scale_ratio()

        # Pygame and screen setup
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)

        self.game = PlaybackGame(Arena(*canvas_dimensions), self.battle_log)
        self.initialize_creatures_for_playback()
        self.initialize_global_events()

        # Setup playback control
        self.playing = True

        # self.background = pygame.image.load('assets/bg5.png')
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((130, 130, 124))

        self.background = pygame.transform.scale(self.background, (800, 800))

        # Define arena_rect here
        self.arena_rect = pygame.Rect(self.offset[0], self.offset[1], self.canvas_dimensions[0], self.canvas_dimensions[1])

        # UI Controls
        self.button_color = (0, 200, 0)
        self.button_hover_color = (0, 255, 0)
        self.button_rect = pygame.Rect(650, 700, 120, 50)
        self.font = pygame.font.Font(None, 36)

    def calculate_scale_ratio(self):
        # Calculate scale ratio based on original arena dime    nsions and canvas dimensions
        scale_width = self.canvas_dimensions[0] / self.original_arena_width
        scale_height = self.canvas_dimensions[1] / self.original_arena_height
        return min(scale_width, scale_height)

    def initialize_creatures_for_playback(self):
        creatures = []

        for info in self.battle_log['header']['creatures']:
            # Extract position and size from the JSON record, scale them, and initialize creatures
            position = tuple(info['position'])
            size = tuple(info['size'])

            scaled_position = self.scale_position(position)
            scaled_size = self.scale_size(size)

            collider = RectCollider(center=position, size=scaled_size, angle=info['angle'])
            creature_events = {str(time): [event for event in events if event['id'] == info['id']]
                            for time, events in self.battle_log['events'].items()}

            creature_name = info['name']
            creature_type = creature_name.split()[0]  # Extract the creature type from the name

            sprite_filename = info['sprite_filename']
            sprite = self.sprite_manager.get_sprite(sprite_filename)


            creature = PlaybackCreature(
                playback_id=info['id'],
                health=info['health'],
                position=position,
                speed=info['speed'],
                name=creature_name,
                sprite=sprite,
                angle=info['angle'],
                bullet_range=info['bullet_range'],
                events=creature_events,
                collider=collider,
                scale_size=self.scale_size,
                scale_position=self.scale_position,
                shoot_cooldown=info['shoot_cooldown'],
                score=info['score'],
            )
            self.game.add_game_object(creature)  # This method should set the game for the creature
            creatures.append(creature)
        self.game.game_objects = creatures
        self.game.winner = self.battle_log['header']['winner']

    def initialize_global_events(self):
        for time, events in self.battle_log['events'].items():
            self.game.global_events[time] = [event for event in events if event['type'] in ['creation', 'destruction']]


    def scale_size(self, size):
        """Scales the size from arena to screen dimensions based on the calculated scale ratio."""
        scaled_width = size[0] * self.scale_ratio
        scaled_height = size[1] * self.scale_ratio
        return (scaled_width, scaled_height)


    def scale_position(self, position):
        """Scales the position from arena to screen coordinates based on the calculated scale ratio."""
        x, y = position
        return x * self.scale_ratio, y * self.scale_ratio


    def virtual_to_screen(self, position):
        virtual_x, virtual_y = position
        screen_x = self.arena_rect.x + (virtual_x / self.battle_log['header']['arena']['width']) * self.arena_rect.width
        screen_y = self.arena_rect.y + (virtual_y / self.battle_log['header']['arena']['height']) * self.arena_rect.height
        return screen_x, screen_y
    
    def draw_arena(self):
        pygame.draw.rect(self.screen, (255, 100, 100), self.arena_rect, 2)  # Draw the arena boundar


    def play_pause(self):
        self.playing = not self.playing



    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rect.collidepoint(pygame.mouse.get_pos()):
                    self.play_pause()
            elif event.type == pygame.KEYDOWN:  # Check for key presses
                if event.key == pygame.K_SPACE:  # If the spacebar is pressed
                    self.play_pause()  # Toggle the play/pause state
                elif event.key == pygame.K_z:  # If the 'z' key is pressed
                    self.game.toggle_bounding_boxes()  # Toggle the bounding boxes
                elif event.key == pygame.K_r: # If the 'r' key is pressed
                    self.game.toggle_shooting_ranges()
                    


    def draw_GUI(self):
        # mouse_pos = pygame.mouse.get_pos()
        # button_color = self.button_hover_color if self.button_rect.collidepoint(mouse_pos) else self.button_color
        # pygame.draw.rect(self.screen, button_color, self.button_rect)
        # text_surface = self.font.render('Play/Pause', True, (255, 255, 255))
        # text_rect = text_surface.get_rect(center=self.button_rect.center)
        # self.screen.blit(text_surface, text_rect)

        # Display current event_index at the top-right of the screen
        total_turns = len(self.battle_log['events'])
        current_turn = Game.get_time()
        event_index_text = f'Turn: {current_turn}/{total_turns}'
        event_index_surface = self.font.render(event_index_text, True, (255, 255, 255))
        event_index_rect = event_index_surface.get_rect(topright=(self.screen.get_width() - 10, 10))
        self.screen.blit(event_index_surface, event_index_rect)


    def generate_frame(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw the background
        self.screen.blit(self.background, (0, 0))

        # Draw the arena
        pygame.draw.rect(self.screen, (255, 100, 100), self.arena_rect, 2)

        # Draw the game objects
        for game_object in self.game.game_objects:
            game_object.draw(self.screen, self.virtual_to_screen)

        # Draw the GUI
        self.draw_GUI()

        # If output_image is True, return the current screen as a PIL image
        if self.output_image:
            frame_copy = self.screen.copy()
            # Resize the frame to the desired dimensions
            frame_copy = pygame.transform.scale(frame_copy, self.screen.get_size())
            pil_image = Image.frombytes("RGBA", frame_copy.get_size(), pygame.image.tostring(frame_copy, "RGBA"))
            self.frames.append(pil_image)

    def capture_last_frame(self):
        # Capture the last frame of the game
        last_frame = self.screen.copy()
        return last_frame

    def run(self):
        clock = pygame.time.Clock()
        # Manually call update_from_events to simulate the first update without rendering
        if str(Game.get_time()) in self.battle_log['events']:
            self.game.update_from_events()
            Game.update_time()
        else:
            # Reset time and creatures' states to loop the playback
            Game.reset_time()
            self.game.reset_objects()

        while True:
            self.handle_events()

            if self.playing:
                if str(Game.get_time()) in self.battle_log['events']:
                    self.game.update_from_events()
                    Game.update_time()
                else:
                    # Reset time and creatures' states to loop the playback
                    Game.reset_time()
                    self.game.reset_objects()

            # Start rendering at time 0
            if Game.get_time() >= 0:
                self.generate_frame()

                if self.render:
                    pygame.display.flip()

                if not self.playing or Game.get_time() >= len(self.battle_log['events']):
                    break

            clock.tick(10) # Control playback speed
        

        # last_frame = self.capture_last_frame()

        if self.game.winner == "Draw":
            winner_text = "It's a draw!"
            # Add an extra frame with the winner's name
        else:
            winner_text = f"{self.game.winner} wins!"

        # Render the winner's name text
        text_surface = self.font.render(winner_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip() # Update the display

        # Capture the last frame with the winner's name
        last_frame = self.screen.copy()
        # Resize the last frame to match the dimensions of the other frames
        last_frame = pygame.transform.scale(last_frame, self.screen.get_size())
        # Convert the last frame to a PIL Image object in RGBA mode
        last_frame_pil = Image.frombytes("RGBA", last_frame.get_size(), pygame.image.tostring(last_frame, "RGBA"))
        self.frames.append(last_frame_pil)

        # Wait for 3 seconds before ending the video
        pygame.time.wait(3000)


if __name__ == "__main__":
    # Get a list of all JSON files in the directory
    json_files = glob.glob('playbacks/*.json')

    # Find the most recent file
    latest_file = max(json_files, key=os.path.getctime)

    # Initialize and run the player with the most recent file
    player = AutoChessPlayer(latest_file)
    player.run()
