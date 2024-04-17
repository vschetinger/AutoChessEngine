#!/bin/bash

# Description:
# This script iterates over .json files in a specified directory and uses them as input
# for the AutoChessPlaybackToVideo.py script to generate videos.

# Usage:
# ./all_playbacks_to_video.sh /path/to/playbacks/directory [/path/to/output/directory]

# Check if a directory path was provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/playbacks/directory [/path/to/output/directory]"
    exit 1
fi

# Use the first argument as the directory containing the .json playback files
PLAYBACKS_DIRECTORY="$1"

# Check if the provided directory exists
if [ ! -d "$PLAYBACKS_DIRECTORY" ]; then
    echo "Error: Directory '$PLAYBACKS_DIRECTORY' does not exist."
    exit 1
fi

# Check if the provided directory contains .json files
if [ -z "$(find "$PLAYBACKS_DIRECTORY" -maxdepth 1 -name '*.json')" ]; then
    echo "Error: No .json files found in directory '$PLAYBACKS_DIRECTORY'."
    exit 1
fi

# Use the second argument as the output directory for the videos (default to current directory)
OUTPUT_DIRECTORY="${2:-.}"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIRECTORY"

# Iterate over all .json files in the specified directory
for json_file in "$PLAYBACKS_DIRECTORY"/*.json; do
    # Extract the base filename without the .json extension
    filename=$(basename "$json_file" .json)
    
    # Call the AutoChessPlaybackToVideo.py script with the current .json file and output directory as arguments
    python AutoChessPlaybackToVideo.py "$json_file" "$OUTPUT_DIRECTORY/$filename.mp4"
    echo "Generated video for playback: $json_file"
done