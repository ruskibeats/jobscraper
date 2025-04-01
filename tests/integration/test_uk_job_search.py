import pytest
from unittest.mock import AsyncMock
from api.scrapeJobs import scrape_jobs
from job_sources.factory import JobSourceFactory
from tests.mocks.indeed_responses import get_indeed_search_response
from tests.mocks.linkedin_responses import get_linkedin_search_response
from tests.mocks.glassdoor_responses import get_glassdoor_search_response
from tests.mocks.jobserve_responses import get_jobserve_search_response

@pytest.mark.asyncio
async def test_uk_job_search(mocker):
    # Mock the job source search methods
    mocker.patch.object(JobSourceFactory, 'create_all', return_value=[
        AsyncMock(search_jobs=AsyncMock(return_value=get_indeed_search_response())),
        AsyncMock(search_jobs=AsyncMock(return_value=get_linkedin_search_response())),
        AsyncMock(search_jobs=AsyncMock(return_value=get_glassdoor_search_response())),
        AsyncMock(search_jobs=AsyncMock(return_value=get_jobserve_search_response()))
    ])
    
    # Call the scrape_jobs function with a UK location
    search_query = {
        "title": "Software Engineer",
        "location": "London, UK",
        "remote": False,
        "job_type": "fulltime"
    }
    results = await scrape_jobs(search_query)
    
    # Check that the correct number of results are returned
    assert len(results) == 12  # 3 results from each of the 4 sources
    
    # Check that JobServe results are included
    jobserve_results = [job for job in results if job['source'] == 'jobserve']
    assert len(jobserve_results) == 3
    
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
