#!/bin/bash
# Simple wrapper script for filter_jobs.py that accepts parameters in a simpler format
# Example usage: ./filter_results.sh Input="jobs.csv" Output="filtered_jobs.csv" Query="Project Manager" ApiKey="your-openai-api-key"

# Default values
INPUT=""
OUTPUT=""
QUERY=""
API_KEY=""
MODEL="gpt-3.5-turbo"
MIN_SCORE=0.7
LIMIT=50

# Parse arguments
for arg in "$@"; do
    key=$(echo "$arg" | cut -d= -f1)
    value=$(echo "$arg" | cut -d= -f2- | tr -d '"')
    
    case "$key" in
        Input)
            INPUT="$value"
            ;;
        Output)
            OUTPUT="$value"
            ;;
        Query)
            QUERY="$value"
            ;;
        ApiKey)
            API_KEY="$value"
            ;;
        Model)
            MODEL="$value"
            ;;
        MinScore)
            MIN_SCORE="$value"
            ;;
        Limit)
            LIMIT="$value"
            ;;
        *)
            echo "Unknown parameter: $key"
            ;;
    esac
done

# Check required parameters
if [ -z "$INPUT" ]; then
    echo "Error: Input parameter is required"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    echo "Error: Output parameter is required"
    exit 1
fi

if [ -z "$QUERY" ]; then
    echo "Error: Query parameter is required"
    exit 1
fi

# Use API key from environment variable if not provided
if [ -z "$API_KEY" ]; then
    if [ -n "$OPENAI_API_KEY" ]; then
        API_KEY="$OPENAI_API_KEY"
    elif [ -n "$OPENROUTER_API_KEY" ]; then
        API_KEY="$OPENROUTER_API_KEY"
    else
        echo "Error: ApiKey parameter is required or OPENAI_API_KEY/OPENROUTER_API_KEY environment variable must be set"
        exit 1
    fi
fi

# Build command
CMD="./filter_jobs.py --input \"$INPUT\" --output \"$OUTPUT\" --query \"$QUERY\" --api-key \"$API_KEY\" --model \"$MODEL\" --min-score $MIN_SCORE --limit $LIMIT"

# Print command
echo "Executing: $CMD"

# Execute command
eval "$CMD"
