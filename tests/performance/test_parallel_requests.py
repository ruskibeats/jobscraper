import pytest
import asyncio
from api.scrapeJobs import scrape_jobs
from job_sources.factory import JobSourceFactory
from tests.mocks.indeed_responses import get_indeed_search_response
from tests.mocks.linkedin_responses import get_linkedin_search_response
from tests.mocks.glassdoor_responses import get_glassdoor_search_response
from tests.mocks.jobserve_responses import get_jobserve_search_response

@pytest.mark.asyncio
async def test_parallel_requests(mocker):
    # Mock the job source search methods with a delay
    async def delayed_indeed_response():
        await asyncio.sleep(1.0)
        return get_indeed_search_response()
        
    async def delayed_linkedin_response():
        await asyncio.sleep(1.5)
        return get_linkedin_search_response()
        
    async def delayed_glassdoor_response():
        await asyncio.sleep(0.8)
        return get_glassdoor_search_response()
        
    async def delayed_jobserve_response():
        await asyncio.sleep(1.2)
        return get_jobserve_search_response()
        
    mocker.patch.object(JobSourceFactory, 'create_all', return_value=[
        asyncio.coroutine(delayed_indeed_response)(),
        asyncio.coroutine(delayed_linkedin_response)(),
        asyncio.coroutine(delayed_glassdoor_response)(),
        asyncio.coroutine(delayed_jobserve_response)()
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
    
    # Check that the execution time is less than the sum of the individual delays
    # This verifies that the requests are being made in parallel
    assert execution_time < 1.0 + 1.5 + 0.8 + 1.2
    
    # Check that the correct number of results are returned
    assert len(results) == 12  # 3 results from each of the 4 sources
