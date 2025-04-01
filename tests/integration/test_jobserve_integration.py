import pytest
from unittest.mock import AsyncMock
from api.scrapeJobs import scrape_jobs
from job_sources.factory import JobSourceFactory
from tests.mocks.jobserve_responses import get_jobserve_search_response

@pytest.mark.asyncio
async def test_jobserve_integration(mocker):
    # Mock the JobServe search method
    mocker.patch.object(JobSourceFactory, 'create', return_value=AsyncMock(
        search_jobs=AsyncMock(return_value=get_jobserve_search_response())
    ))
    
    # Call the scrape_jobs function with a UK location and contract job type
    search_query = {
        "title": "Software Engineer",
        "location": "London, UK",
        "remote": False,
        "job_type": "contract"
    }
    results = await scrape_jobs(search_query)
    
    # Check that only JobServe results are returned
    assert len(results) == 3
    for job in results:
        assert job['source'] == 'jobserve'
        
    # Check that the results are properly normalized
    for job in results:
        assert 'title' in job
        assert 'company' in job
        assert 'location' in job
        assert 'remote' in job
        assert 'job_type' in job
        assert 'url' in job
        assert 'source' in job
        assert 'description' in job
        assert 'posted_at' in job
        
    # Check that the job type is correctly set to contract
    for job in results:
        assert job['job_type'] == 'contract'
