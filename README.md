# Auto Chess Game Engine

This project provides a game engine for simulating and playing Auto Chess games. The engine is implemented in Python and supports both simulation and playback modes.

## Features

- Simulate Auto Chess games with customizable game objects, creatures, and projectiles
- Playback recorded games for analysis and visualization
- Extensible architecture for adding new game objects and behaviors
- Collision detection and handling between game objects
- Scoring system for tracking player performance
- Data extraction and analysis tools for game statistics and creature data
- Batch simulation capabilities for running multiple game simulations
- Video generation from game playbacks
- Batch video generation from multiple game playbacks

## Getting Started

### Prerequisites

- Python 3.x
- Pygame library
- MoviePy library

### Installation

1. Clone the repository:
git clone https://github.com/vschetinger/AutoChessEngine.git

2. Install the required dependencies:
pip install pygame moviepy


### Usage

1. Simulation Mode:
   - Run the `AutoChessGameSimulation.py` script to start a new game simulation.
   - Customize the game objects, creatures, and projectiles in the script as needed.
   - The simulation will run automatically, and the game state will be recorded.

2. Playback Mode:
   - Run the `AutoChessPlaybackToVideo.py` script to play back a recorded game and generate a video.
   - Provide the path to the recorded game file as an argument to the script.
   - The script will load the recorded game, visualize it using Pygame, and generate a video file.

3. Batch Simulation:
   - Run the `AutoChessBatchSimulation.py` script to perform batch simulations of Auto Chess games.
   - Customize the simulation parameters, such as the number of simulations, creature types, and arena sizes.
   - The script will run multiple simulations and save the results as JSON files.

4. Data Extraction:
   - Use the `AutoChessCreatureDataExtractor.py` script to extract creature statistics from the recorded game files.
   - Provide the folder path containing the JSON files and the output CSV file path.
   - The script will process the JSON files, extract relevant creature data, and save it to a CSV file.

   - Use the `AutoChessGameDataExtractor.py` script to extract game statistics from the recorded game files.
   - Provide the folder path containing the JSON files and the output CSV file path.
   - The script will process the JSON files, extract game-level data, and save it to a CSV file.

5. Batch Video Generation:
   - Use the `all_playbacks_to_video.sh` script to generate videos from multiple game playbacks.
   - Provide the directory path containing the JSON playback files as an argument to the script.
   - Optionally, provide an output directory path as the second argument to specify where the generated videos should be saved.
   - The script will iterate over all the JSON files in the specified directory and generate a video for each playback using the `AutoChessPlaybackToVideo.py` script.

## Code Structure

- `AutoChessEngine.py`: Contains the core classes and functionality for the game engine.
  - `Arena`: Represents the game arena.
  - `GameObject`: Base class for all game objects.
  - `SimulationGameObject`: Represents a game object in simulation mode.
  - `PlaybackGameObject`: Represents a game object in playback mode.
  - `BaseCreature`: Base class for creatures in the game.
  - `SimulationCreature`: Represents a creature in simulation mode.
  - `PlaybackCreature`: Represents a creature in playback mode.
  - `BaseProjectile`: Base class for projectiles in the game.
  - `SimulationProjectile`: Represents a projectile in simulation mode.
  - `PlaybackProjectile`: Represents a projectile in playback mode.
  - `Game`: Base class for the game.
  - `SimulationGame`: Represents the game in simulation mode.

- `AutoChessGameSimulation.py`: Script for running a game simulation.
- `AutoChessPlaybackToVideo.py`: Script for playing back a recorded game and generating a video.
- `AutoChessBatchSimulation.py`: Script for running batch simulations of Auto Chess games.
- `AutoChessCreatureDataExtractor.py`: Script for extracting creature statistics from recorded game files.
- `AutoChessGameDataExtractor.py`: Script for extracting game statistics from recorded game files.
- `all_playbacks_to_video.sh`: Bash script for generating videos from multiple game playbacks.

## Running Your Own Experiments

If you want to conduct your own experiments using the Auto Chess game engine, follow these steps:

1. **Think of experiment logic and parameters:**
   - Consider the specific scenario or hypothesis you want to test.
   - Determine the relevant parameters, such as the number of simulations, creature types, arena sizes, and any other variables you want to explore.

2. **Set the parameters in `AutoChessBatchSimulation.py` and run it:**
   - Open the `AutoChessBatchSimulation.py` script in your preferred Python IDE or text editor.
   - Locate the `__main__` section at the bottom of the script.
   - Modify the parameters according to your experiment design. For example:
``` python num_simulations = 100 # Number of simulations to run creature_types = [get_sniper_creature_b, get_machine_gun_creature_b, get_mine_laying_creature_b] arena_sizes = [2000, 2500, 3000, 4000, 10000] # List of arena sizes ```


   - Save the changes to the script.
   - Open a terminal or command prompt and navigate to the project directory.
   - Run the script using the following command:
```python AutoChessBatchSimulation.py```

   - The script will execute the specified number of simulations with the configured parameters and save the results as JSON files in the `playbacks` directory.

3. **Use `all_playbacks_to_video.sh` to generate videos:**
   - Open a terminal or command prompt and navigate to the project directory.
   - Run the `all_playbacks_to_video.sh` script using the following command:
     ```
./all_playbacks_to_video.sh playbacks [output_directory]

     Replace `playbacks` with the path to the directory containing the JSON playback files, and optionally specify an output directory for the generated videos.
   - The script will process all the JSON files in the specified directory and generate a video for each playback using the `AutoChessPlaybackToVideo.py` script.
   - You can watch some of the generated videos to visually analyze the simulations.

4. **Extract the CSV data and load it into Orange Data Mining:**
   - Run the `AutoChessCreatureDataExtractor.py` script to extract creature statistics from the recorded game files:
     ```
python AutoChessCreatureDataExtractor.py playbacks creature_data.csv

     Replace `playbacks` with the path to the directory containing the JSON files, and `creature_data.csv` with the desired output CSV file name.
   - Run the `AutoChessGameDataExtractor.py` script to extract game statistics from the recorded game files:
     ```
python AutoChessGameDataExtractor.py playbacks game_data.csv

     Replace `playbacks` with the path to the directory containing the JSON files, and `game_data.csv` with the desired output CSV file name.
   - Open Orange Data Mining and create a new project.
   - Import the generated CSV files (`creature_data.csv` and `game_data.csv`) into Orange Data Mining.
   - Use the various data analysis and visualization tools provided by Orange Data Mining to explore and interpret the extracted data.

By following these steps, you can design and run your own experiments using the Auto Chess game engine, generate videos for visual analysis, and perform data analysis using Orange Data Mining.


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).