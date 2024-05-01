#!/bin/bash

# Check if a directory path and FPS value were provided as arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 /path/to/playbacks/directory fps"
    exit 1
fi

playback_dir=$1
output_dir=$playback_dir
fps=$2

# Iterate over all JSON files in the playback directory, excluding the batch output file
for file in "$playback_dir"/*.json; do
    if [[ $file == *.json && $file != *"batch_output"* ]]; then
        python AutoChessPlaybackToVideo.py "$file" --fps "$fps"
    fi
done