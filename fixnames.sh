#!/bin/bash

# Check if a directory was provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Target directory from the first script argument
DIR=$1

# Find and rename files
find "$DIR" -depth -type f -name "*_*" -exec bash -c '
for file; do
    dir=$(dirname "$file")
    base=$(basename "$file")
    newbase=${base//_/--}
    mv -i "$file" "$dir/$newbase"
done
' bash {} +
