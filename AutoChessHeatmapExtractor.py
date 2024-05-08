import json
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Specify the directory containing the JSON files
playbacks_dir = "playbacks"

# Specify the output directory for saving the heatmap images
output_dir = "statistics"

# Specify the number of bins for the heatmaps
num_bins = 50

# Initialize variables to store the accumulated data
accumulated_damage_grid = None
accumulated_position_grid = None

# Initialize variables to store the additional information
total_games = 0
total_creatures = 0
total_turns = 0

# Iterate through all JSON files in the playbacks directory
for filename in os.listdir(playbacks_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(playbacks_dir, filename)
        
        # Read the JSON file
        with open(file_path) as file:
            data = json.load(file)
        
        # Extract the arena dimensions
        arena_width = data['header']['arena']['width']
        arena_height = data['header']['arena']['height']
        
        # Create or update the accumulated grids
        if accumulated_damage_grid is None:
            accumulated_damage_grid = np.zeros((num_bins, num_bins))
            accumulated_position_grid = np.zeros((num_bins, num_bins))
        
        # Calculate the bin size based on the arena dimensions
        bin_width = arena_width / num_bins
        bin_height = arena_height / num_bins
        
        # Iterate through the events and update the accumulated grids
        for timestep, events in data['events'].items():
            for event in events:
                if event['type'] == 'deltaSetter':
                    creature_id = event['id']
                    creature = next((c for c in data['header']['creatures'] if c['id'] == creature_id), None)
                    if creature:
                        if event['attribute'] == 'health':
                            position = creature['position']
                            x_bin = int(position[0] / bin_width)
                            y_bin = int(position[1] / bin_height)
                            accumulated_damage_grid[y_bin, x_bin] += 1
                        elif event['attribute'] == 'position':
                            position = event['value']
                            x_bin = int(position[0] / bin_width)
                            y_bin = int(position[1] / bin_height)
                            accumulated_position_grid[y_bin, x_bin] += 1
        
        # Update the additional information
        total_games += 1
        total_creatures += len(data['header']['creatures'])
        total_turns += len(data['events'])  # Accumulate the total number of turns

# Apply Gaussian blur to the accumulated grids (optional)
from scipy.ndimage import gaussian_filter
accumulated_damage_grid = gaussian_filter(accumulated_damage_grid, sigma=1)
accumulated_position_grid = gaussian_filter(accumulated_position_grid, sigma=1)

# Normalize the accumulated position grid
accumulated_position_grid /= np.max(accumulated_position_grid)

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Generate a timestamp for the output file names
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save the heatmap of accumulated damage occurrences
damage_output_file = os.path.join(output_dir, f"damage_heatmap_{timestamp}.png")
fig, ax = plt.subplots(figsize=(10, 10))
im = ax.imshow(accumulated_damage_grid, cmap='hot', interpolation='nearest')
ax.set_title('Heatmap of Accumulated Damage Occurrences')
ax.set_xlabel('X')
ax.set_ylabel('Y')
cbar = ax.figure.colorbar(im, ax=ax, label='Accumulated Damage Occurrences')
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.text(0.5, 0.01, f"Total Games: {total_games}, Total Creatures: {total_creatures}, Total Turns: {total_turns}",
         ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8))
fig.savefig(damage_output_file)
plt.close(fig)

# Save the heatmap of car positions
position_output_file = os.path.join(output_dir, f"car_positions_heatmap_{timestamp}.png")
fig, ax = plt.subplots(figsize=(10, 10))
im = ax.imshow(accumulated_position_grid, cmap='hot', interpolation='nearest')
ax.set_title('Heatmap of Car Positions')
ax.set_xlabel('X')
ax.set_ylabel('Y')
cbar = ax.figure.colorbar(im, ax=ax, label='Normalized Car Position Occurrences')
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.text(0.5, 0.01, f"Total Games: {total_games}, Total Creatures: {total_creatures}, Total Turns: {total_turns}",
         ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8))
fig.savefig(position_output_file)
plt.close(fig)

print(f"Damage heatmap saved as {damage_output_file}")
print(f"Car positions heatmap saved as {position_output_file}")