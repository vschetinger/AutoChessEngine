# No need to import Creature directly if it's not used here
import pygame
import json
import sys
from AutoChessEngine import PlaybackCreature, Game, Arena


class PlaybackGame(Game):
    def __init__(self, arena, creatures):
        super().__init__(arena)
        self.creatures = creatures  # Here creatures are specifically set for playback
        self.set_game_for_creatures()
    
    def update_from_events(self, time_index):
        for creature in self.creatures:
            creature.move(time_index)

    def reset_creatures(self):
        # Reset each creature to its initial state at the start of the playback loop
        for creature in self.creatures:
            creature.reset_to_initial_state()


class AutoChessPlayer:
    def __init__(self, battle_log_path):
        with open(battle_log_path, 'r') as f:
            self.battle_log = json.load(f)

        # Arena setup based on JSON data
        arena_dimensions = self.battle_log['header']['arena']
        self.arena = Arena(arena_dimensions['width'], arena_dimensions['height'])

        # Initialize creatures from JSON data
        # Assuming 'battle_log' is already loaded from JSON
        creatures = [
            PlaybackCreature(
                id=info['id'],
                health=info['health'],
                position=tuple(info['position']),
                speed=info['speed'],
                name=info['name'],
                angle=info['angle'],
                events={int(time): [event for event in events if event['id'] == info['id']]
                        for time, events in self.battle_log['events'].items()}
            ) for info in self.battle_log['header']['creatures']
        ]



        # Instantiate PlaybackGame with creatures
        self.game = PlaybackGame(self.arena, creatures)

        # Setup playback control
        self.playing = False
        self.current_event_index = 0

        # Pygame and screen setup
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))

        # self.background = pygame.image.load('assets/bg5.png')
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((130, 130, 124))

        self.background = pygame.transform.scale(self.background, (800, 800))

        # Define arena_rect here
        self.arena_rect = pygame.Rect(190, 185, 425, 425)  # Example dimensions and position

        # UI Controls
        self.button_color = (0, 200, 0)
        self.button_hover_color = (0, 255, 0)
        self.button_rect = pygame.Rect(650, 700, 120, 50)
        self.font = pygame.font.Font(None, 36)



    def virtual_to_screen(self, position):
        virtual_x, virtual_y = position
        screen_x = self.arena_rect.x + (virtual_x / self.battle_log['header']['arena']['width']) * self.arena_rect.width
        screen_y = self.arena_rect.y + (virtual_y / self.battle_log['header']['arena']['height']) * self.arena_rect.height
        return int(screen_x), int(screen_y)
    
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

    def draw_button(self):
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.button_hover_color if self.button_rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, button_color, self.button_rect)
        text_surface = self.font.render('Play/Pause', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)

        # Display current event_index at the top-right of the screen
        event_index_text = f'Event Index: {self.current_event_index}'
        event_index_surface = self.font.render(event_index_text, True, (255, 255, 255))
        event_index_rect = event_index_surface.get_rect(topright=(self.screen.get_width() - 10, 10))
        self.screen.blit(event_index_surface, event_index_rect)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            self.screen.blit(self.background, (0, 0))
            self.draw_arena()
            self.draw_button()

            if self.playing:
                if str(self.current_event_index) in self.battle_log['events']:
                    self.game.update_from_events(self.current_event_index)
                    self.current_event_index += 1
                else:
                    # Reset current_event_index and creatures' states to loop the playback
                    self.current_event_index = 0
                    self.game.reset_creatures()

            # Draw creatures
            for creature in self.game.creatures:
                creature.draw(self.screen, self.virtual_to_screen)

                
            pygame.display.flip()
            clock.tick(10)  # Control playback speed


if __name__ == "__main__":
    arena_rect = (150, 150, 500, 500)  # Example coordinates and size (x, y, width, height)

    player = AutoChessPlayer('simulation_record5.json')
    player.run()
