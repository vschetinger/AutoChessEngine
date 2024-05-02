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

#### On Mac:
1. Install homebrew:
```bash 
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
2. Install python using homebrew:
```bash 
brew install python
```
3. Install other dependencies
```bash 
pip3 install pygame moviepy
brew install ffmpeg
```

### Installation

1. Clone the repository:
git clone https://github.com/vschetinger/AutoChessEngine.git

2. Install the required dependencies:
pip install pygame moviepy


### Usage

1. Batch Simulation:
   - Configure the simulation parameters in the `experiment_config.json` file.
   - Run the `AutoChessBatchSimulation.py` script to perform batch simulations of Auto Chess games.
   - The script will run multiple simulations based on the configured parameters and save the results as JSON files in the `playbacks` directory.

2. Batch Video Generation:
   - Use the `all_playbacks_to_video.sh` script to generate videos from multiple game playbacks.
   - Provide the directory path containing the JSON playback files and the desired frames per second (FPS) as arguments to the script.
   - The script will iterate over all the JSON files in the specified directory and generate a video for each playback using the `AutoChessPlaybackToVideo.py` script.

3. Statistics Extraction:
   - Run the `AutoChessStatisticsExtractor.py` script to extract game and creature statistics from the recorded game files.
   - The script will process the JSON files in the `playbacks` and `experiments` directories.
   - It will generate CSV files containing creature statistics, game statistics, and experiment statistics in the `statistics` directory.


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
- `all_playbacks_to_video.sh`: Bash script for generating videos from multiple game playbacks.

## Running Your Own Experiments


If you want to conduct your own experiments using the Auto Chess game engine, follow these steps:

1. **Think of experiment logic and parameters:**
   - Consider the specific scenario or hypothesis you want to test.
   - Determine the relevant parameters, such as the number of simulations, creature types, arena sizes, and any other variables you want to explore.

2. **Set the parameters in `experiment_config.json` and run `AutoChessBatchSimulation.py`:**
   - Open the `experiment_config.json` file and modify the parameters according to your experiment design.
   - Save the changes to the configuration file.
   - Open a terminal or command prompt and navigate to the project directory.
   - Run the `AutoChessBatchSimulation.py` script using the following command:
```bash 
python AutoChessBatchSimulation.py
```

   - The script will execute the specified number of simulations with the configured parameters and save the playbacks as JSON files in the `playbacks` directory, and the experiment details in `experiments`.

3. **Use `all_playbacks_to_video.sh` to generate videos:**
   - Open a terminal or command prompt and navigate to the project directory.
   - Run the `all_playbacks_to_video.sh` script using the following command:
```bash
./all_playbacks_to_video.sh playbacks 25
```
Replace `playbacks` with the path to the directory containing the JSON playback files, and optionally specify an output directory for the generated videos.
   - The script will process all the JSON files in the specified directory and generate a video for each playback using the `AutoChessPlaybackToVideo.py` script.
   - You will need to let it run all simulations in real time and record them through the screen

4. **Extract statistics using `AutoChessStatisticsExtractor.py`:**
   - Run the `AutoChessStatisticsExtractor.py` script to extract game and creature statistics from the recorded game files:
```bash 
python AutoChessStatisticsExtractor
```
   - Open Orange Data Mining and create a new project.
   - Import the generated CSV files into Orange Data Mining.
   - Use the various data analysis and visualization tools provided by Orange Data Mining to explore and interpret the extracted data.

By following these steps, you can design and run your own experiments using the Auto Chess game engine, generate videos for visual analysis, and perform data analysis using Orange Data Mining.

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

- `AutoChessBatchSimulation.py`: Script for running batch simulations of Auto Chess games.
- `AutoChessPlaybackToVideo.py`: Script for playing back a recorded game and generating a video.
- `all_playbacks_to_video.sh`: Bash script for generating videos from multiple game playbacks.
- `AutoChessStatisticsExtractor.py`: Script for extracting game and creature statistics from recorded game files.


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
