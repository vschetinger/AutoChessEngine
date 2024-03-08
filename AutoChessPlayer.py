import pygame
import json
import sys
import math


class AutoChessPlayer:
    def __init__(self, battle_log_path):
        # Load the battle log
        with open(battle_log_path, 'r') as f:
            self.battle_log = json.load(f)

        # Extract the header and events
        self.header = self.battle_log["header"]["creatures"]
        self.events = self.battle_log["events"]

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()  # Add this to control the game speed

        # Initialize game state
        self.playing = True
        self.current_event_index = 0  # Corrected variable name for clarity

        # Initialize creature positions and properties based on the header
        self.positions = {}
        self.creature_properties = {}
        creature_spacing = self.screen.get_width() / (len(self.header) / 2 + 1)  # Spacing between creatures
        for i, creature in enumerate(self.header):
            if creature["player"] == "Player 1":
                y_position = 50  # Top row
                x_position = (i % (len(self.header) // 2) + 1) * creature_spacing
            elif creature["player"] == "Player 2":
                y_position = self.screen.get_height() - 50  # Bottom row
                x_position = ((i - len(self.header) // 2) % (len(self.header) // 2) + 1) * creature_spacing
            self.positions[creature['name']] = (int(x_position), y_position)
            self.creature_properties[creature['name']] = {
                'color': (255, 0, 0) if creature["player"] == "Player 1" else (0, 255, 0),
                'size': 30
            }


    def draw_arrow(self, start, end, color, thickness=5):
        # Draw the line
        pygame.draw.line(self.screen, color, start, end, thickness)
        
        # Calculate the angle of the line
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)
        
        # Calculate the points of the arrowhead
        arrowhead_length = 20
        arrowhead_angle = math.pi / 6
        arrow_point1 = (end[0] - arrowhead_length * math.cos(angle - arrowhead_angle),
                        end[1] - arrowhead_length * math.sin(angle - arrowhead_angle))
        arrow_point2 = (end[0] - arrowhead_length * math.cos(angle + arrowhead_angle),
                        end[1] - arrowhead_length * math.sin(angle + arrowhead_angle))
        
        # Draw the arrowhead
        pygame.draw.polygon(self.screen, color, [end, arrow_point1, arrow_point2])

    def play(self):
        # Define the button
        button_color = (0, 0, 255)  # Blue
        button_rect = pygame.Rect(10, 10, 100, 50)  # x, y, width, height

        # Main game loop
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse button down event
                    mouse_pos = pygame.mouse.get_pos()  # Get mouse position
                    if button_rect.collidepoint(mouse_pos):  # Check if the mouse position is within the button's rectangle
                        self.current_event_index += 1  # Advance the time step only when the button is pressed
                        pygame.time.delay(500)  # Add a delay of 500 milliseconds after each button press

            self.screen.fill((0, 0, 0))  # Clear screen

            # Draw the button
            pygame.draw.rect(self.screen, button_color, button_rect)

            # Draw the creatures
            for name, props in self.creature_properties.items():
                pygame.draw.circle(self.screen, props['color'], self.positions[name], props['size'])

            # Process events from the battle log
            if self.current_event_index < len(self.events):
                event = self.events[self.current_event_index]
                if 'winner' not in event:  # Check if it's a battle event
                    attacker_pos = self.positions[event['attacker']]
                    defender_pos = self.positions[event['defender']]
                    # Animate attack (for simplicity, we'll just draw a line here)
                    self.draw_arrow(attacker_pos, defender_pos, (255, 255, 255), 5)

                    
                    # Print the current event
                    print(f"Current event: {event}")  # Add this line to print the current event

            pygame.display.flip()  # Update the display
player = AutoChessPlayer('battle_log_with_header.json')
player.play()
