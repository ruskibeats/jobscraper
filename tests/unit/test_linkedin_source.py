import pytest
from unittest.mock import AsyncMock
from job_sources.linkedin import LinkedInJobSource
from config import JobSearchConfig

@pytest.fixture
def linkedin_source():
    return LinkedInJobSource()

@pytest.mark.asyncio
async def test_search_jobs(linkedin_source, mocker):
    # Mock the jobspy_scrape function
    mock_jobspy_scrape = AsyncMock(return_value=[
        {
            "title": "Software Engineer",
            "company": "Acme Inc.",
            "location": "London, UK",
            "is_remote": False,
            "job_type": "fulltime",
            "job_url": "https://www.linkedin.com/jobs/view/123",
            "description": "A great software engineering role.",
            "date_posted": "2025-04-01",
            "company_industry": "Technology",
            "company_description": "A leading tech company"
        }
    ])
    mocker.patch("job_sources.linkedin.jobspy_scrape", mock_jobspy_scrape)
    
    # Call the search_jobs method
    results = await linkedin_source.search_jobs(
        search_term="Software Engineer",
        location="London",
        remote=False,
        job_type="fulltime",
        results_wanted=1
    )
    
    # Check the results
    assert len(results) == 1
    assert results[0]["title"] == "Software Engineer"
    assert results[0]["company"] == "Acme Inc. (Technology)"
    assert results[0]["location"] == "London, UK"
    assert results[0]["remote"] == False
    assert results[0]["job_type"] == "fulltime"
    assert results[0]["url"] == "https://www.linkedin.com/jobs/view/123"
    assert results[0]["source"] == "linkedin"
    assert results[0]["description"] == "A great software engineering role."
    assert results[0]["posted_at"] == "2025-04-01"
    
    # Check that jobspy_scrape was called with the correct arguments
    mock_jobspy_scrape.assert_called_once_with(
        site_name=["linkedin"],
        search_term="Software Engineer",
        location="London",
        results_wanted=1,
        remote=False,
        job_type="fulltime",
        fetch_full_text=True,
        proxies=JobSearchConfig.USE_PROXIES_FOR_LINKEDIN
    )

def test_normalize_job(linkedin_source):
    # Test normalization of LinkedIn job data with company industry
    job_data = {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "is_remote": False,
        "job_type": "fulltime",
        "job_url": "https://www.linkedin.com/jobs/view/123",
        "description": "A great software engineering role.",
        "date_posted": "2025-04-01",
        "company_industry": "Technology"
    }
    
    normalized_job = linkedin_source.normalize_job(job_data)
    
    assert normalized_job == {
        "title": "Software Engineer",
        "company": "Acme Inc. (Technology)",
        "location": "London, UK",
        "remote": False,
        "job_type": "fulltime",
        "url": "https://www.linkedin.com/jobs/view/123",
        "source": "linkedin",
        "description": "A great software engineering role.",
        "posted_at": "2025-04-01"
    }
    
    # Test normalization with company description
    job_data = {
        "title": "Software Engineer",
        "company": "Acme Inc.",
        "location": "London, UK",
        "is_remote": False,
        "job_type": "fulltime",
        "job_url": "https://www.linkedin.com/jobs/view/123",
        "description": "A great software engineering role.",
        "date_posted": "2025-04-01",
        "company_description": "A leading tech company with a mission to change the world through innovation."
    }
    
    normalized_job = linkedin_source.normalize_job(job_data)
    
    assert normalized_job == {
        "title": "Software Engineer",
        "company": "Acme Inc. - A leading tech company with a mission to change the...",
        "location": "London, UK", 
        "remote": False,
        "job_type": "fulltime",
        "url": "https://www.linkedin.com/jobs/view/123",
        "source": "linkedin",
        "description": "A great software engineering role.",
        "posted_at": "2025-04-01"
    }
