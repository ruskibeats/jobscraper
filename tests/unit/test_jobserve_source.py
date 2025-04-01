import pytest
from unittest.mock import AsyncMock
from job_sources.jobserve import JobServeJobSource

@pytest.fixture
def jobserve_source():
    return JobServeJobSource()

@pytest.mark.asyncio
async def test_search_jobs(jobserve_source, mocker):
    # Mock the search_jobserve function
    mock_search_jobserve = AsyncMock(return_value=[
        {
            "title": "Software Engineer",
            "company": "Acme Inc.",
            "location": "London, UK",
            "is_remote": False,
            "job_type": "contract",
            "job_url": "https://www.jobserve.com/job/123",
            "description": "A great software engineering contract role.",
            "date_posted": "2025-04-01"
        }
    ])
    mocker.patch("job_sources.jobserve.search_jobserve", mock_search_jobserve)
    
    # Call the search_jobs method
    results = await jobserve_source.search_jobs(
        search_term="Software Engineer",
        location="London",
        remote=False,
        job_type="contract",
        results_wanted=1
    )
    
    # Check the results
    assert len(results) == 1
    assert results[0]["title"] == "Software Engineer"
    assert results[0]["company"] == "Acme Inc."
    assert results[0]["location"] == "London, UK"
    assert results[0]["remote"] == False
    assert results[0]["job_type"] == "contract"
    assert results[0]["url"] == "https://www.jobserve.com/job/123"
    assert results[0]["source"] == "jobserve"
    assert results[0]["description"] == "A great software engineering contract role."
    assert results[0]["posted_at"] == "2025-04-01"
    
    # Check that search_jobserve was called with the correct arguments
    mock_search_jobserve.assert_called_once_with(
        search_term="Software Engineer",
        location="London",
        results_wanted=1,
        job_type="contract"
    )

def test_normalize_job(jobserve_source):
    # Test normalization of JobServe job data
    job_data = {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "is_remote": False,
        "job_type": "contract",
        "job_url": "https://www.jobserve.com/job/123",
        "description": "A great software engineering contract role.",
        "date_posted": "2025-04-01"
    }
    
    normalized_job = jobserve_source.normalize_job(job_data)
    
    assert normalized_job == {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "remote": False,
        "job_type": "contract",
        "url": "https://www.jobserve.com/job/123",
        "source": "jobserve",
        "description": "A great software engineering contract role.",
        "posted_at": "2025-04-01"
    }
