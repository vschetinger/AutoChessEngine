import pygame
import json
import sys
import math


class AutoChessPlayer:
    def __init__(self, battle_log_path):
        with open(battle_log_path, 'r') as f:
            self.battle_log = json.load(f)

        self.header = self.battle_log["header"]["creatures"]
        self.events = self.battle_log["events"]

        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()

        self.playing = True
        self.current_event_index = 0

        self.positions = {}
        self.creature_properties = {}
        creature_spacing = self.screen.get_width() / (len(self.header) / 2 + 1)
        for i, creature in enumerate(self.header):
            y_position = 50 if creature["player"] == "Player 1" else self.screen.get_height() - 50
            x_position = ((i % (len(self.header) // 2) + 1) * creature_spacing)
            self.positions[creature['name']] = (int(x_position), y_position)
            self.creature_properties[creature['name']] = {
                'color': (255, 0, 0) if creature["player"] == "Player 1" else (0, 255, 0),
                'size': 30,
                'health': creature['initial_health']
            }

    def draw_arrow(self, start, end, color, thickness=5):
        pygame.draw.line(self.screen, color, start, end, thickness)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)
        arrowhead_length = 20
        arrowhead_angle = math.pi / 6
        arrow_point1 = (end[0] - arrowhead_length * math.cos(angle - arrowhead_angle),
                        end[1] - arrowhead_length * math.sin(angle - arrowhead_angle))
        arrow_point2 = (end[0] - arrowhead_length * math.cos(angle + arrowhead_angle),
                        end[1] - arrowhead_length * math.sin(angle + arrowhead_angle))
        pygame.draw.polygon(self.screen, color, [end, arrow_point1, arrow_point2])

    def play(self):
        button_color = (0, 0, 255)
        button_rect = pygame.Rect(10, 10, 100, 50)

        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.current_event_index < len(self.events) - 1:
                        self.current_event_index += 1
                    pygame.time.delay(500)

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, button_color, button_rect)

            for name, props in self.creature_properties.items():
                if props['health'] > 0:
                    pygame.draw.circle(self.screen, props['color'], self.positions[name], props['size'])

            if self.current_event_index < len(self.events):
                event = self.events[self.current_event_index]
                if "attacker" in event and "defender" in event:  # Ensuring it's a battle event
                    attacker_pos = self.positions[event['attacker']]
                    defender_pos = self.positions[event['defender']]
                    self.draw_arrow(attacker_pos, defender_pos, (255, 255, 255), 5)
                    self.creature_properties[event['defender']]['health'] = event['defender_remaining_health']
                    # Print event summary
                    print(f"Turn {event['turn']}: {event['attacker']} attacked {event['defender']} for {event['damage']} damage. Remaining health: {event['defender_remaining_health']}")


            pygame.display.flip()

player = AutoChessPlayer('battle_log_with_header.json')
player.play()
