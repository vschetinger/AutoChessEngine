#!/bin/bash

# Check if a directory path was provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/playbacks/directory"
    exit 1
fi

playback_dir=$1
output_dir=$playback_dir

# Iterate over all JSON files in the playback directory, excluding the batch output file
for file in "$playback_dir"/*.json; do
    if [[ $file == *.json && $file != *"batch_output"* ]]; then
        python AutoChessPlaybackToVideo.py "$file"
    fi
done