#!/bin/bash
# Combined script that searches for jobs and then filters the results using an LLM
# Example usage: ./search_and_filter.sh Job="Project Manager" Location="London" Contract="Yes" ApiKey="your-openai-api-key"

# Default values
JOB=""
LOCATION=""
CONTRACT="No"
PERMANENT="No"
REMOTE="No"
SITES="jobserve"
RESULTS=100
DISTANCE=50
COUNTRY="UK"
JOBSERVE_URL=""
API_KEY=""
MODEL="gpt-3.5-turbo"
MIN_SCORE=0.7
LIMIT=50

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

# Generate unique filenames based on timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)
RAW_OUTPUT="jobs_${TIMESTAMP}.csv"
FILTERED_OUTPUT="filtered_jobs_${TIMESTAMP}.csv"

echo "Step 1: Searching for jobs..."
echo "========================================"

# Build search command
SEARCH_CMD="./job_search.sh Job=\"$JOB\" Location=\"$LOCATION\" Output=\"$RAW_OUTPUT\" Sites=\"$SITES\" Results=$RESULTS Distance=$DISTANCE Country=\"$COUNTRY\""

# Add JobServe URL if provided
if [ -n "$JOBSERVE_URL" ]; then
    SEARCH_CMD="$SEARCH_CMD JobServeUrl=\"$JOBSERVE_URL\""
fi

# Add flags
if [ "$CONTRACT" = "Yes" ] || [ "$CONTRACT" = "yes" ] || [ "$CONTRACT" = "Y" ] || [ "$CONTRACT" = "y" ] || [ "$CONTRACT" = "true" ] || [ "$CONTRACT" = "True" ]; then
    SEARCH_CMD="$SEARCH_CMD Contract=\"Yes\""
fi

if [ "$PERMANENT" = "Yes" ] || [ "$PERMANENT" = "yes" ] || [ "$PERMANENT" = "Y" ] || [ "$PERMANENT" = "y" ] || [ "$PERMANENT" = "true" ] || [ "$PERMANENT" = "True" ]; then
    SEARCH_CMD="$SEARCH_CMD Permanent=\"Yes\""
fi

if [ "$REMOTE" = "Yes" ] || [ "$REMOTE" = "yes" ] || [ "$REMOTE" = "Y" ] || [ "$REMOTE" = "y" ] || [ "$REMOTE" = "true" ] || [ "$REMOTE" = "True" ]; then
    SEARCH_CMD="$SEARCH_CMD Remote=\"Yes\""
fi

# Execute search command
echo "Executing: $SEARCH_CMD"
eval "$SEARCH_CMD"

echo ""
echo "Step 2: Filtering and ranking jobs using LLM..."
echo "========================================"

# Build filter command
FILTER_CMD="./filter_results.sh Input=\"$RAW_OUTPUT\" Output=\"$FILTERED_OUTPUT\" Query=\"$JOB\" ApiKey=\"$API_KEY\" Model=\"$MODEL\" MinScore=$MIN_SCORE Limit=$LIMIT"

# Execute filter command
echo "Executing: $FILTER_CMD"
eval "$FILTER_CMD"

echo ""
echo "========================================"
echo "Process complete!"
echo "Raw results: $RAW_OUTPUT"
echo "Filtered results: $FILTERED_OUTPUT"
echo "========================================"
