#!/bin/bash

# SCRIPT IS IN SIMULATION MODE - NO FILES WILL BE DELETED
# The actual delete command is commented out below.

TARGET_DIR=${1:-/tmp}

echo "[$(date)] Cleaning up old files in: $TARGET_DIR"

if [ -d "$TARGET_DIR" ]; then
    # Delete files older than 7 days
    # find "$TARGET_DIR" -type f -mtime +7 -delete
    echo "Simulated: find $TARGET_DIR -type f -mtime +7 -delete"
else
    echo "Directory $TARGET_DIR does not exist."
fi

echo "Disk cleanup completed."
