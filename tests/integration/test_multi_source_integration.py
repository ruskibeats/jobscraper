import pytest
from unittest.mock import AsyncMock
from api.scrapeJobs import scrape_jobs
from job_sources.factory import JobSourceFactory
from tests.mocks.indeed_responses import get_indeed_search_response
from tests.mocks.linkedin_responses import get_linkedin_search_response
from tests.mocks.glassdoor_responses import get_glassdoor_search_response

@pytest.mark.asyncio
async def test_multi_source_integration(mocker):
    # Mock the job source search methods
    mocker.patch.object(JobSourceFactory, 'create_all', return_value=[
        AsyncMock(search_jobs=AsyncMock(return_value=get_indeed_search_response())),
        AsyncMock(search_jobs=AsyncMock(return_value=get_linkedin_search_response())),
        AsyncMock(search_jobs=AsyncMock(return_value=get_glassdoor_search_response()))
    ])
    
    # Call the scrape_jobs function with a non-UK location
    search_query = {
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "remote": True,
        "job_type": "fulltime"
    }
    results = await scrape_jobs(search_query)
    
    # Check that the correct number of results are returned
    assert len(results) == 9  # 3 results from each of the 3 sources
    
    # Check that results from all sources are included
    indeed_results = [job for job in results if job['source'] == 'indeed']
    linkedin_results = [job for job in results if job['source'] == 'linkedin']
    glassdoor_results = [job for job in results if job['source'] == 'glassdoor']
    assert len(indeed_results) == 3
    assert len(linkedin_results) == 3
    assert len(glassdoor_results) == 3
    
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
        
    # Check that remote jobs are included
    remote_jobs = [job for job in results if job['remote'] == True]
    assert len(remote_jobs) > 0
