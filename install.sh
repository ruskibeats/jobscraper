#!/bin/bash
# Installation script for the JobServe scraper

echo "JobServe Scraper Installation Script"
echo "==================================="
echo "This script will install the JobServe scraper for JobSpy."
echo ""

# Check if JOBSPY_DIR is set
if [ -z "$JOBSPY_DIR" ]; then
    # Try to find JobSpy installation
    if [ -d "$HOME/projects/JobSpy" ]; then
        JOBSPY_DIR="$HOME/projects/JobSpy"
    elif [ -d "$HOME/JobSpy" ]; then
        JOBSPY_DIR="$HOME/JobSpy"
    else
        echo "JobSpy directory not found."
        echo "Please set the JOBSPY_DIR environment variable to the JobSpy installation directory."
        echo "For example:"
        echo "export JOBSPY_DIR=/path/to/JobSpy"
        exit 1
    fi
fi

echo "Using JobSpy directory: $JOBSPY_DIR"
echo ""

# Check if the JobSpy directory exists
if [ ! -d "$JOBSPY_DIR" ]; then
    echo "Error: JobSpy directory not found at $JOBSPY_DIR"
    exit 1
fi

# Check if the jobspy directory exists
if [ ! -d "$JOBSPY_DIR/jobspy" ]; then
    echo "Error: jobspy directory not found at $JOBSPY_DIR/jobspy"
    exit 1
fi

# Copy the jobserve directory to the jobspy directory
echo "Copying jobserve directory to $JOBSPY_DIR/jobspy..."
cp -r jobserve "$JOBSPY_DIR/jobspy/"

# Check if the copy was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy jobserve directory to $JOBSPY_DIR/jobspy"
    exit 1
fi

echo "JobServe directory copied successfully."
echo ""

# Update model.py
echo "Updating model.py..."
MODEL_FILE="$JOBSPY_DIR/jobspy/model.py"

# Check if model.py exists
if [ ! -f "$MODEL_FILE" ]; then
    echo "Error: model.py not found at $MODEL_FILE"
    exit 1
fi

# Check if JOBSERVE is already in model.py
if grep -q "JOBSERVE = \"jobserve\"" "$MODEL_FILE"; then
    echo "JOBSERVE already exists in model.py. Skipping..."
else
    # Manually update the Site enum by replacing the entire class
    # First, find the Site enum class
    SITE_ENUM_START=$(grep -n "class Site(Enum):" "$MODEL_FILE" | cut -d: -f1)
    
    if [ -z "$SITE_ENUM_START" ]; then
        echo "Error: Site enum not found in model.py"
        exit 1
    fi
    
    # Create a temporary file with the updated Site enum
    TMP_FILE=$(mktemp)
    
    # Copy the file up to the Site enum
    head -n $SITE_ENUM_START "$MODEL_FILE" > "$TMP_FILE"
    
    # Add the Site enum with JOBSERVE
    cat >> "$TMP_FILE" << 'EOF'
class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIP_RECRUITER = "zip_recruiter"
    GLASSDOOR = "glassdoor"
    GOOGLE = "google"
    BAYT = "bayt"
    NAUKRI = "naukri"
    JOBSERVE = "jobserve"
EOF
    
    # Find the end of the Site enum
    SITE_ENUM_END=$(tail -n +$SITE_ENUM_START "$MODEL_FILE" | grep -n "^$" | head -1 | cut -d: -f1)
    SITE_ENUM_END=$((SITE_ENUM_START + SITE_ENUM_END))
    
    # Copy the rest of the file
    tail -n +$SITE_ENUM_END "$MODEL_FILE" >> "$TMP_FILE"
    
    # Replace the original file
    mv "$TMP_FILE" "$MODEL_FILE"
    
    echo "Added JOBSERVE to Site enum in model.py."
fi

# Update __init__.py
echo "Updating __init__.py..."
INIT_FILE="$JOBSPY_DIR/jobspy/__init__.py"

# Check if __init__.py exists
if [ ! -f "$INIT_FILE" ]; then
    echo "Error: __init__.py not found at $INIT_FILE"
    exit 1
fi

# Check if JobServeScraper import is already in __init__.py
if grep -q "from jobspy.jobserve import JobServeScraper" "$INIT_FILE"; then
    echo "JobServeScraper import already exists in __init__.py. Skipping..."
else
    # Create a temporary file with the import added
    TMP_FILE=$(mktemp)
    
    # Add the import at the top
    echo "from jobspy.jobserve import JobServeScraper  # Added by install.sh" > "$TMP_FILE"
    
    # Copy the rest of the file
    cat "$INIT_FILE" >> "$TMP_FILE"
    
    # Replace the original file
    mv "$TMP_FILE" "$INIT_FILE"
    
    echo "Added JobServeScraper import to __init__.py."
fi

# Check if JOBSERVE is already in SCRAPER_MAPPING
if grep -q "Site.JOBSERVE: JobServeScraper" "$INIT_FILE"; then
    echo "JOBSERVE already exists in SCRAPER_MAPPING. Skipping..."
else
    # Create a temporary file
    TMP_FILE=$(mktemp)
    
    # Find the SCRAPER_MAPPING dictionary
    SCRAPER_MAPPING_START=$(grep -n "SCRAPER_MAPPING = {" "$INIT_FILE" | cut -d: -f1)
    
    if [ -z "$SCRAPER_MAPPING_START" ]; then
        echo "Error: SCRAPER_MAPPING not found in __init__.py"
        exit 1
    fi
    
    # Copy the file up to the SCRAPER_MAPPING
    head -n $SCRAPER_MAPPING_START "$INIT_FILE" > "$TMP_FILE"
    
    # Add the SCRAPER_MAPPING with JOBSERVE
    echo "    SCRAPER_MAPPING = {" >> "$TMP_FILE"
    echo "        Site.LINKEDIN: LinkedIn," >> "$TMP_FILE"
    echo "        Site.INDEED: Indeed," >> "$TMP_FILE"
    echo "        Site.ZIP_RECRUITER: ZipRecruiter," >> "$TMP_FILE"
    echo "        Site.GLASSDOOR: Glassdoor," >> "$TMP_FILE"
    echo "        Site.GOOGLE: Google," >> "$TMP_FILE"
    echo "        Site.BAYT: BaytScraper," >> "$TMP_FILE"
    echo "        Site.NAUKRI: Naukri," >> "$TMP_FILE"
    echo "        Site.JOBSERVE: JobServeScraper,  # Added by install.sh" >> "$TMP_FILE"
    echo "    }" >> "$TMP_FILE"
    
    # Find the end of the SCRAPER_MAPPING
    SCRAPER_MAPPING_END=$(tail -n +$SCRAPER_MAPPING_START "$INIT_FILE" | grep -n "^[[:space:]]*}" | head -1 | cut -d: -f1)
    SCRAPER_MAPPING_END=$((SCRAPER_MAPPING_START + SCRAPER_MAPPING_END))
    
    # Copy the rest of the file
    tail -n +$SCRAPER_MAPPING_END "$INIT_FILE" >> "$TMP_FILE"
    
    # Replace the original file
    mv "$TMP_FILE" "$INIT_FILE"
    
    echo "Added JOBSERVE to SCRAPER_MAPPING in __init__.py."
fi

echo ""
echo "Installation complete!"
echo "You can now use JobServe in your JobSpy searches:"
echo ""
echo "from jobspy import scrape_jobs"
echo ""
echo "jobs = scrape_jobs("
echo "    site_name=[\"jobserve\"],"
echo "    search_term=\"Software Engineer\","
echo "    location=\"London\","
echo "    results_wanted=10,"
echo "    country_indeed='UK',"
echo ")"
echo ""
echo "For more examples, see the test_jobserve.py script."
