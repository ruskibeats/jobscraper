"""
Integration tests for JobSpy integration.

This module contains tests for the integration with the JobSpy library,
using mock responses to simulate JobSpy API calls.
"""

import pytest
import asyncio
import pandas as pd
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import api
from api.scrapeJobs import scrape_jobs, scrape_jobs_with_jobspy
from tests.integration.jobspy_responses import create_mock_jobspy_response

@pytest.fixture
def mock_jobspy_response():
    """Create a mock JobSpy response."""
    return create_mock_jobspy_response()

@patch("api.scrapeJobs.jobspy_scrape")
@pytest.mark.asyncio
async def test_scrape_jobs_with_jobspy(mock_scrape, mock_jobspy_response):
    """Test the JobSpy integration with mock responses."""
    # Configure the mock to return our test data
    mock_scrape.return_value = mock_jobspy_response
    
    # Test search query
    search_query = {
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "fulltime"
    }
    
    # Call the function
    results = await scrape_jobs_with_jobspy(search_query)
    
    # Verify the results
    assert len(results) > 0
    
    # Check that the results have been properly normalized
    for job in results:
        assert "title" in job
        assert "company" in job
        assert "location" in job
        assert "remote" in job
        assert "job_type" in job
        assert "url" in job
        assert "source" in job
        assert "description" in job
        assert "posted_at" in job
    
    # Verify that JobSpy was called with the correct parameters
    mock_scrape.assert_called_once()
    call_args = mock_scrape.call_args[1]
    assert call_args["search_term"] == search_query["title"]
    assert call_args["location"] == search_query["location"]
    assert call_args["remote"] == search_query["remote"]

@patch("api.scrapeJobs.jobspy_scrape")
@pytest.mark.asyncio
async def test_scrape_jobs_main_function(mock_scrape, mock_jobspy_response):
    """Test the main scrape_jobs function with mock responses."""
    # Configure the mock to return our test data
    mock_scrape.return_value = mock_jobspy_response
    
    # Test search query
    search_query = {
        "title": "Data Scientist",
        "location": "San Francisco",
        "remote": False,
        "job_type": "fulltime"
    }
    
    # Call the function
    results = await scrape_jobs(search_query)
    
    # Verify the results
    assert len(results) > 0
    
    # Check that the results have been properly normalized and deduplicated
    for job in results:
        assert "title" in job
        assert "company" in job
        assert "location" in job
        assert "remote" in job
        assert "job_type" in job
        assert "url" in job
        assert "source" in job
        assert "description" in job
        assert "posted_at" in job
        assert "fingerprint" in job  # Deduplication adds fingerprints

@patch("api.scrapeJobs.jobspy_scrape")
@pytest.mark.asyncio
async def test_error_handling(mock_scrape):
    """Test error handling in the scrape_jobs function."""
    # Configure the mock to raise an exception
    mock_scrape.side_effect = Exception("JobSpy API error")
    
    # Test search query
    search_query = {
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "fulltime"
    }
    
    # Call the function
    results = await scrape_jobs(search_query)
    
    # Verify that an empty list is returned on error
    assert results == []

@patch("api.scrapeJobs.jobspy_scrape")
@pytest.mark.asyncio
async def test_job_type_mapping(mock_scrape, mock_jobspy_response):
    """Test job type mapping in the scrape_jobs_with_jobspy function."""
    # Configure the mock to return our test data
    mock_scrape.return_value = mock_jobspy_response
    
    # Test different job types
    job_types = [
        ("permanent", "fulltime"),
        ("full-time", "fulltime"),
        ("contract", "contract"),
        ("part-time", "parttime"),
        ("internship", "internship"),
        ("unknown", None)
    ]
    
    for input_type, expected_type in job_types:
        # Test search query
        search_query = {
            "title": "Software Engineer",
            "location": "Remote",
            "remote": True,
            "job_type": input_type
        }
        
        # Call the function
        await scrape_jobs_with_jobspy(search_query)
        
        # Verify that JobSpy was called with the correct job type
        call_args = mock_scrape.call_args[1]
        assert call_args["job_type"] == expected_type
        
        # Reset the mock for the next iteration
        mock_scrape.reset_mock()

@patch("api.scrapeJobs.jobspy_scrape")
@pytest.mark.asyncio
async def test_empty_response(mock_scrape):
    """Test handling of empty responses from JobSpy."""
    # Configure the mock to return an empty DataFrame
    mock_scrape.return_value = pd.DataFrame()
    
    # Test search query
    search_query = {
        "title": "Non-existent Job",
        "location": "Nowhere",
        "remote": False,
        "job_type": "fulltime"
    }
    
    # Call the function
    results = await scrape_jobs(search_query)
    
    # Verify that an empty list is returned
    assert results == []
