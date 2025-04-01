import pytest
from unittest.mock import AsyncMock
from job_sources.indeed import IndeedJobSource
from config import JobSearchConfig

@pytest.fixture
def indeed_source():
    return IndeedJobSource()

@pytest.mark.asyncio
async def test_search_jobs(indeed_source, mocker):
    # Mock the jobspy_scrape function
    mock_jobspy_scrape = AsyncMock(return_value=[
        {
            "title": "Software Engineer",
            "company": "Acme Inc.",
            "location": "London, UK",
            "is_remote": False,
            "job_type": "fulltime",
            "job_url": "https://www.indeed.com/job/123",
            "description": "A great software engineering role.",
            "date_posted": "2025-04-01"
        }
    ])
    mocker.patch("job_sources.indeed.jobspy_scrape", mock_jobspy_scrape)
    
    # Mock the is_uk_location function
    mocker.patch.object(JobSearchConfig, "is_uk_location", return_value=True)
    
    # Call the search_jobs method
    results = await indeed_source.search_jobs(
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
    assert results[0]["url"] == "https://www.indeed.com/job/123"
    assert results[0]["source"] == "indeed"
    assert results[0]["description"] == "A great software engineering role."
    assert results[0]["posted_at"] == "2025-04-01"
    
    # Check that jobspy_scrape was called with the correct arguments
    mock_jobspy_scrape.assert_called_once_with(
        site_name=["indeed"],
        search_term="Software Engineer",
        location="London",
        results_wanted=1,
        country_indeed="UK",
        remote=False,
        job_type="fulltime",
        fetch_full_text=True
    )

def test_normalize_job(indeed_source):
    # Test normalization of Indeed job data
    job_data = {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "is_remote": False,
        "job_type": "fulltime",
        "job_url": "https://www.indeed.com/job/123",
        "description": "A great software engineering role.",
        "date_posted": "2025-04-01"
    }
    
    normalized_job = indeed_source.normalize_job(job_data)
    
    assert normalized_job == {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "remote": False,
        "job_type": "fulltime",
        "url": "https://www.indeed.com/job/123",
        "source": "indeed",
        "description": "A great software engineering role.",
        "posted_at": "2025-04-01"
    }
