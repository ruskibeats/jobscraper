import pytest
from unittest.mock import AsyncMock
from job_sources.glassdoor import GlassdoorJobSource

@pytest.fixture
def glassdoor_source():
    return GlassdoorJobSource()

@pytest.mark.asyncio
async def test_search_jobs(glassdoor_source, mocker):
    # Mock the jobspy_scrape function
    mock_jobspy_scrape = AsyncMock(return_value=[
        {
            "title": "Software Engineer",
            "company": "Acme Inc.",
            "location": "London, UK",
            "is_remote": False,
            "job_type": "fulltime",
            "job_url": "https://www.glassdoor.com/job-listing/123",
            "description": "A great software engineering role.",
            "date_posted": "2025-04-01"
        }
    ])
    mocker.patch("job_sources.glassdoor.jobspy_scrape", mock_jobspy_scrape)
    
    # Call the search_jobs method
    results = await glassdoor_source.search_jobs(
        search_term="Software Engineer",
        location="London",
        remote=False,
        job_type="fulltime",
        results_wanted=1
    )
    
    # Check the results
    assert len(results) == 1
    assert results[0]["title"] == "Software Engineer"
    assert results[0]["company"] == "Acme Inc."
    assert results[0]["location"] == "London, UK"
    assert results[0]["remote"] == False
    assert results[0]["job_type"] == "fulltime"
    assert results[0]["url"] == "https://www.glassdoor.com/job-listing/123"
    assert results[0]["source"] == "glassdoor"
    assert results[0]["description"] == "A great software engineering role."
    assert results[0]["posted_at"] == "2025-04-01"
    
    # Check that jobspy_scrape was called with the correct arguments
    mock_jobspy_scrape.assert_called_once_with(
        site_name=["glassdoor"],
        search_term="Software Engineer",
        location="London",
        results_wanted=1,
        remote=False,
        job_type="fulltime"
    )

def test_normalize_job(glassdoor_source):
    # Test normalization of Glassdoor job data
    job_data = {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "is_remote": False,
        "job_type": "fulltime",
        "job_url": "https://www.glassdoor.com/job-listing/123",
        "description": "A great software engineering role.",
        "date_posted": "2025-04-01"
    }
    
    normalized_job = glassdoor_source.normalize_job(job_data)
    
    assert normalized_job == {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "remote": False,
        "job_type": "fulltime",
        "url": "https://www.glassdoor.com/job-listing/123",
        "source": "glassdoor",
        "description": "A great software engineering role.",
        "posted_at": "2025-04-01"
    }
