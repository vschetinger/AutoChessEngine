# No need to import Creature directly if it's not used here
import pygame
import json
import sys
from AutoChessEngine import PlaybackCreature, Game, Arena, RectCollider


class PlaybackGame(Game):
    def __init__(self, arena):
        super().__init__(arena)
        self.set_game_for_creatures()
        self.show_bounding_boxes = True  # Start with bounding boxes

    def toggle_bounding_boxes(self):
        self.show_bounding_boxes = not self.show_bounding_boxes
    
    # Now handling only all creatures, should handle all kinds of events later
    def update_from_events(self):
        for game_object in self.game_objects:
            game_object.move()

    def reset_creatures(self):
        # Reset each creature to its initial state at the start of the playback loop
        for game_object in self.game_objects:
            game_object.reset_to_initial_state()


class AutoChessPlayer:
    def __init__(self, battle_log_path, screen_size=(800, 800), offset=(80, 80), canvas_dimensions=(670, 670)):
        with open(battle_log_path, 'r') as f:
            self.battle_log = json.load(f)

        # Original arena dimensions from the JSON file
        original_arena_dimensions = self.battle_log['header']['arena']
        # For clarity, storing original dimensions separately
        self.original_arena_width = original_arena_dimensions['width']
        self.original_arena_height = original_arena_dimensions['height']

        # Setting the canvas dimensions based on the input parameter
        self.canvas_dimensions = canvas_dimensions
        self.screen_size = screen_size
        self.offset = offset
        self.scale_ratio = self.calculate_scale_ratio()

        # Pygame and screen setup
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)

        self.game = PlaybackGame(Arena(*canvas_dimensions))
        self.initialize_creatures_for_playback()
        

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
        # Calculate scale ratio based on original arena dimensions and canvas dimensions
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

            collider = RectCollider(center=scaled_position, size=scaled_size)
            creature_events = {str(time): [event for event in events if event['id'] == info['id']]
                            for time, events in self.battle_log['events'].items()}

            creature = PlaybackCreature(
                playback_id=info['id'],
                health=info['health'],
                position=scaled_position,
                speed=info['speed'],
                name=info['name'],
                angle=info['angle'],
                events=creature_events,
                collider=collider,
                scale_size=self.scale_size,
                scale_position=self.scale_position
            )
            self.game.add_game_object(creature)  # This method should set the game for the creature
            creatures.append(creature)
        self.game.creatures = creatures




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


    def draw_GUI(self):
        # mouse_pos = pygame.mouse.get_pos()
        # button_color = self.button_hover_color if self.button_rect.collidepoint(mouse_pos) else self.button_color
        # pygame.draw.rect(self.screen, button_color, self.button_rect)
        # text_surface = self.font.render('Play/Pause', True, (255, 255, 255))
        # text_rect = text_surface.get_rect(center=self.button_rect.center)
        # self.screen.blit(text_surface, text_rect)

        # Display current event_index at the top-right of the screen
        event_index_text = f'Event Index: {self.game.time}'
        event_index_surface = self.font.render(event_index_text, True, (255, 255, 255))
        event_index_rect = event_index_surface.get_rect(topright=(self.screen.get_width() - 10, 10))
        self.screen.blit(event_index_surface, event_index_rect)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            self.screen.blit(self.background, (0, 0))
            self.draw_arena()
            self.draw_GUI()

            if self.playing:
                if str(self.game.time) in self.battle_log['events']:
                    self.game.update_from_events()
                    self.game.time += 1
                else:
                    # Reset time and creatures' states to loop the playback
                    self.game.time = 0
                    self.game.reset_creatures()

            # Draw creatures
            for creature in self.game.creatures:
                screen_position = self.virtual_to_screen(creature.position)  # Correctly call virtual_to_screen here
                creature.draw(self.screen, self.virtual_to_screen)
                
            pygame.display.flip()
            clock.tick(10)  # Control playback speed



if __name__ == "__main__":
    # arena_rect = (50, 50, 700, 700)  # Example coordinates and size (x, y, width, height)

    player = AutoChessPlayer('simulation_record5.json')
    player.run()
