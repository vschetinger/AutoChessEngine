import json
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Specify the directory containing the JSON files
playbacks_dir = "playbacks"

# Specify the output directory for saving the heatmap image
output_dir = "statistics"

# Specify the number of bins for the heatmap
num_bins = 50

# Initialize variables to store the accumulated data
accumulated_grid = None

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
        
        # Create or update the accumulated grid
        if accumulated_grid is None:
            accumulated_grid = np.zeros((num_bins, num_bins))
        
        # Calculate the bin size based on the arena dimensions
        bin_width = arena_width / num_bins
        bin_height = arena_height / num_bins
        
        # Iterate through the events and update the accumulated grid
        for timestep, events in data['events'].items():
            for event in events:
                if event['type'] == 'deltaSetter' and event['attribute'] == 'health':
                    creature_id = event['id']
                    creature = next((c for c in data['header']['creatures'] if c['id'] == creature_id), None)
                    if creature:
                        position = creature['position']
                        x_bin = int(position[0] / bin_width)
                        y_bin = int(position[1] / bin_height)
                        accumulated_grid[y_bin, x_bin] += 1

# Apply Gaussian blur to the accumulated grid (optional)
from scipy.ndimage import gaussian_filter
accumulated_grid = gaussian_filter(accumulated_grid, sigma=1)

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Generate a timestamp for the output file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = os.path.join(output_dir, f"heatmap_{timestamp}.png")

# Plot the heatmap and save it as an image
plt.figure(figsize=(10, 10))
plt.imshow(accumulated_grid, cmap='hot', interpolation='nearest')
plt.colorbar(label='Accumulated Damage Occurrences')
plt.title('Heatmap of Accumulated Damage Occurrences')
plt.xlabel('X')
plt.ylabel('Y')
plt.savefig(output_file)
plt.close()

print(f"Heatmap saved as {output_file}")