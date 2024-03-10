import pygame
import json
import sys
import math
from AutoChessEngine import Creature

class AutoChessPlayer:
    def __init__(self, battle_log_path):
        with open(battle_log_path, 'r') as f:
            self.battle_log = json.load(f)
            # print("Loaded battle log:", self.battle_log)
        # Assuming 'header' is the correct key based on your JSON structure
            
        # Prepare deltas for each creature
        creature_deltas = {movement["id"]: movement["deltas"] for movement in self.battle_log["movements"]}
        

        self.creatures = [
            Creature(
                id=info['id'],
                health=info['health'],
                position=tuple(info['position']),
                speed=info['speed'],
                name=info['name'],
                angle=info['angle'],
                deltas=creature_deltas[info['id']]  # Get the corresponding deltas for this creature
            )
            for info in self.battle_log['header']['creatures']
        ]
        self.arena_width = self.battle_log['header']['arena']['width']
        self.arena_height = self.battle_log['header']['arena']['height']
        self.playing = False  # Start with replay paused
        self.current_event_index = 0

        # Assuming 'events' is the correct key based on your JSON structure
        self.events = self.battle_log["movements"]
        self.arena_rect = pygame.Rect(arena_rect)  # Define the arena area as a rectangle

            

        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        self.background = pygame.image.load('bg2.png')
        self.background = pygame.transform.scale(self.background, (800, 800))
        self.playing = False  # Start with replay paused
        self.current_event_index = 0
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
        pygame.draw.rect(self.screen, (255, 100, 100), self.arena_rect, 2)  # Draw the arena boundary


    def draw_creature(self, position, angle, color):
        # Calculate the points of the triangle for the creature
        point = self.virtual_to_screen(position)
        radians = math.radians(angle)
        points = [
            (point[0] + math.cos(radians) * 10, point[1] + math.sin(radians) * 10),
            (point[0] + math.cos(radians + 2.0944) * 10, point[1] + math.sin(radians + 2.0944) * 10),
            (point[0] + math.cos(radians - 2.0944) * 10, point[1] + math.sin(radians - 2.0944) * 10)
        ]
        pygame.draw.polygon(self.screen, color, points)

    def update_creature_positions(self):
        if not self.playing:
            return
        # Apply the next delta for each creature
        for creature in self.creatures:
            creature.apply_next_delta()


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

    def run(self):
        clock = pygame.time.Clock()
        convert_to_screen = lambda pos: self.virtual_to_screen(pos)  # Create a lambda that captures self.arena_rect

        while True:
            self.handle_events()
            self.screen.blit(self.background, (0, 0))
            self.draw_arena()
            self.draw_button()
            if self.playing:
                self.update_creature_positions()

            # Draw creatures whether playing or paused
            for creature in self.creatures:
                creature.draw(self.screen, convert_to_screen)

            pygame.display.flip()
            clock.tick(10)  # Adjust this to control the refresh rate of the simulation




if __name__ == "__main__":
    arena_rect = (150, 150, 500, 500)  # Example coordinates and size (x, y, width, height)

    player = AutoChessPlayer('simulation_record.json')
    player.run()
