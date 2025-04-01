"""
End-to-end integration tests for the job search API.

This module contains tests that simulate the complete flow from search request
to results, testing the integration of all components.
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import api
from api import app
from tests.integration.jobspy_responses import create_mock_jobspy_response

# Create test client
client = TestClient(app)

@pytest.mark.skip(reason="Async endpoints require more setup")
@patch("api.scrapeJobs.jobspy_scrape")
def test_search_to_results_flow(mock_scrape):
    """Test the complete flow from search to results with JobSpy integration."""
    # Configure the mock to return our test data
    mock_scrape.return_value = create_mock_jobspy_response()
    
    # Step 1: Submit a search request
    search_response = client.get("/search", params={
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "Contract"
    })
    
    assert search_response.status_code == 200
    assert len(search_response.json()) > 0
    
    # Verify that the results contain the expected fields
    first_job = search_response.json()[0]
    assert "title" in first_job
    assert "company" in first_job
    assert "location" in first_job
    assert "remote" in first_job
    assert "job_type" in first_job
    assert "url" in first_job
    assert "source" in first_job
    assert "description" in first_job
    
    # Step 2: Test the async flow
    async_response = client.post("/async/search", json={
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "Contract"
    })
    
    assert async_response.status_code == 200
    task_id = async_response.json()["task_id"]
    
    # Step 3: Check task status (may need to retry until completed)
    max_retries = 5
    status = "pending"
    
    for _ in range(max_retries):
        status_response = client.get(f"/async/search/{task_id}/status")
        assert status_response.status_code == 200
        status = status_response.json()["status"]
        
        if status == "completed":
            break
            
        # Wait before retrying
        time.sleep(1)
    
    assert status == "completed", f"Task did not complete in time. Status: {status}"
    
    # Step 4: Get results
    results_response = client.get(f"/async/search/{task_id}/results")
    assert results_response.status_code == 200
    assert len(results_response.json()) > 0

@pytest.mark.skip(reason="Async endpoints require more setup")
@patch("api.scrapeJobs.jobspy_scrape")
def test_error_handling_flow(mock_scrape):
    """Test the error handling flow with JobSpy integration."""
    # Configure the mock to raise an exception
    mock_scrape.side_effect = Exception("JobSpy API error")
    
    # Submit a search request
    search_response = client.get("/search", params={
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "Contract"
    })
    
    # Even with an error, the API should return a 200 status code with empty results
    assert search_response.status_code == 200
    assert search_response.json() == []
    
    # Test the async flow with error
    async_response = client.post("/async/search", json={
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "Contract"
    })
    
    assert async_response.status_code == 200
    task_id = async_response.json()["task_id"]
    
    # Check task status (may need to retry until completed)
    max_retries = 5
    status = "pending"
    
    for _ in range(max_retries):
        status_response = client.get(f"/async/search/{task_id}/status")
        assert status_response.status_code == 200
        status = status_response.json()["status"]
        
        if status in ["completed", "failed"]:
            break
            
        # Wait before retrying
        time.sleep(1)
    
    # Get results (should be empty due to error)
    results_response = client.get(f"/async/search/{task_id}/results")
    if results_response.status_code == 200:
        assert results_response.json() == []
    else:
        # Or it might return an error if the task failed
        assert results_response.status_code in [400, 404, 500]

@pytest.mark.skip(reason="Metrics endpoints require more setup")
@patch("metrics_collector.get_dashboard_data")
def test_metrics_dashboard_flow(mock_get_data):
    """Test the metrics dashboard flow."""
    # Configure the mock to return test data
    mock_get_data.return_value = {
        "queue": {
            "queue_pending": 5,
            "queue_processing": 2,
            "queue_total": 10
        },
        "system": {
            "system_cpu_percent": 25.5,
            "system_memory_percent": 40.2
        },
        "api": {}
    }
    
    # Get dashboard data
    response = client.get("/metrics/dashboard")
    
    assert response.status_code == 200
    assert "queue" in response.json()
    assert "system" in response.json()
    
    # Verify the data
    assert response.json()["queue"]["queue_pending"] == 5
    assert response.json()["queue"]["queue_processing"] == 2
    assert response.json()["queue"]["queue_total"] == 10
    assert response.json()["system"]["system_cpu_percent"] == 25.5
    assert response.json()["system"]["system_memory_percent"] == 40.2

def test_invalid_requests():
    """Test handling of invalid requests."""
    # Test missing required fields
    response = client.get("/search")
    assert response.status_code == 422
    
    # Test invalid job type
    response = client.get("/search", params={
        "title": "Software Engineer",
        "location": "Remote",
        "remote": True,
        "job_type": "InvalidType"
    })
    assert response.status_code == 200  # Should still work, just ignores invalid job type
    
    # Test invalid task ID
    response = client.get("/async/search/invalid-task-id/status")
    assert response.status_code == 404
    
    # Test invalid endpoint
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404
