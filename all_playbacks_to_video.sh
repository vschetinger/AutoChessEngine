#!/bin/bash

# Check if a directory path was provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/playbacks/directory"
    exit 1
fi

# Use the first argument as the directory containing the .json playback files
PLAYBACKS_DIRECTORY="$1"

# Iterate over all .json files in the specified directory
for json_file in "$PLAYBACKS_DIRECTORY"/*.json; do
    # Call the AutoChessPlaybackToVideo.py script with the current .json file as an argument
    python AutoChessPlaybackToVideo.py "$json_file"
    echo "Generated video for playback: $json_file"
done