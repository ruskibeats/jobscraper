#!/bin/bash
# Simple wrapper script for search_jobs.py that accepts parameters in a simpler format
# Example usage: ./job_search.sh Job="Project Manager" Location="London" Contract="Yes" Output="project_manager_jobs.csv"

# Default values
JOB=""
LOCATION=""
CONTRACT="No"
PERMANENT="No"
REMOTE="No"
OUTPUT="jobs.csv"
SITES="jobserve"
RESULTS=100
DISTANCE=50
COUNTRY="UK"
JOBSERVE_URL=""

# Parse arguments
for arg in "$@"; do
    key=$(echo "$arg" | cut -d= -f1)
    value=$(echo "$arg" | cut -d= -f2- | tr -d '"')
    
    case "$key" in
        Job)
            JOB="$value"
            ;;
        Location)
            LOCATION="$value"
            ;;
        Contract)
            CONTRACT="$value"
            ;;
        Permanent)
            PERMANENT="$value"
            ;;
        Remote)
            REMOTE="$value"
            ;;
        Output)
            OUTPUT="$value"
            ;;
        Sites)
            SITES="$value"
            ;;
        Results)
            RESULTS="$value"
            ;;
        Distance)
            DISTANCE="$value"
            ;;
        Country)
            COUNTRY="$value"
            ;;
        JobServeUrl)
            JOBSERVE_URL="$value"
            ;;
        *)
            echo "Unknown parameter: $key"
            ;;
    esac
done

# Check required parameters
if [ -z "$JOB" ]; then
    echo "Error: Job parameter is required"
    exit 1
fi

if [ -z "$LOCATION" ]; then
    echo "Error: Location parameter is required"
    exit 1
fi

# Build command
CMD="./search_jobs.py --job \"$JOB\" --location \"$LOCATION\" --output \"$OUTPUT\" --sites \"$SITES\" --results $RESULTS --distance $DISTANCE --country \"$COUNTRY\""

# Add JobServe URL if provided
if [ -n "$JOBSERVE_URL" ]; then
    CMD="$CMD --jobserve-url \"$JOBSERVE_URL\""
fi

# Add flags
if [ "$CONTRACT" = "Yes" ] || [ "$CONTRACT" = "yes" ] || [ "$CONTRACT" = "Y" ] || [ "$CONTRACT" = "y" ] || [ "$CONTRACT" = "true" ] || [ "$CONTRACT" = "True" ]; then
    CMD="$CMD --contract"
fi

if [ "$PERMANENT" = "Yes" ] || [ "$PERMANENT" = "yes" ] || [ "$PERMANENT" = "Y" ] || [ "$PERMANENT" = "y" ] || [ "$PERMANENT" = "true" ] || [ "$PERMANENT" = "True" ]; then
    CMD="$CMD --permanent"
fi

if [ "$REMOTE" = "Yes" ] || [ "$REMOTE" = "yes" ] || [ "$REMOTE" = "Y" ] || [ "$REMOTE" = "y" ] || [ "$REMOTE" = "true" ] || [ "$REMOTE" = "True" ]; then
    CMD="$CMD --remote"
fi

# Print command
echo "Executing: $CMD"

# Execute command
eval "$CMD"
