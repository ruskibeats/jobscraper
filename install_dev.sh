#!/bin/bash
# Script to install JobSpy in development mode

echo "JobSpy Development Mode Installation Script"
echo "=========================================="
echo "This script will install JobSpy in development mode, which is useful for testing."
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

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed. Please install pip first."
    exit 1
fi

# Install JobSpy in development mode
echo "Installing JobSpy in development mode..."
cd "$JOBSPY_DIR"
pip install -e .

# Check if the installation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to install JobSpy in development mode."
    exit 1
fi

echo ""
echo "JobSpy has been installed in development mode."
echo "You can now run the test script with:"
echo ""
echo "cd $JOBSPY_DIR"
echo "./jobserve_implementation/test_jobserve.py"
echo ""
echo "This will allow the test script to import the jobspy module correctly."
