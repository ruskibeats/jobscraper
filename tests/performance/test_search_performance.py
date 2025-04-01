import pytest
import asyncio
from api.scrapeJobs import scrape_jobs
from job_sources.factory import JobSourceFactory
from tests.mocks.indeed_responses import get_indeed_search_response
from tests.mocks.linkedin_responses import get_linkedin_search_response
from tests.mocks.glassdoor_responses import get_glassdoor_search_response
from tests.mocks.jobserve_responses import get_jobserve_search_response

@pytest.mark.asyncio
async def test_search_performance(mocker):
    # Mock the job source search methods
    mocker.patch.object(JobSourceFactory, 'create_all', return_value=[
        asyncio.coroutine(lambda *args, **kwargs: get_indeed_search_response())(),
        asyncio.coroutine(lambda *args, **kwargs: get_linkedin_search_response())(),
        asyncio.coroutine(lambda *args, **kwargs: get_glassdoor_search_response())(),
        asyncio.coroutine(lambda *args, **kwargs: get_jobserve_search_response())()
    ])
    
    # Call the scrape_jobs function with a typical search query
    search_query = {
        "title": "Software Engineer",
        "location": "London, UK",
        "remote": False,
        "job_type": "fulltime"
    }
    
    # Measure the execution time
    start_time = asyncio.get_event_loop().time()
    results = await scrape_jobs(search_query)
    end_time = asyncio.get_event_loop().time()
    execution_time = end_time - start_time
    
    # Check that the execution time is within acceptable limits
    assert execution_time < 5.0  # Should complete within 5 seconds
    
    # Check that the correct number of results are returned
    assert len(results) == 12  # 3 results from each of the 4 sources
