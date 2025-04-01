"""
Mock responses for JobSpy integration tests.

This module provides mock JobSpy responses for testing the integration
with the JobSpy library without making actual API calls.
"""

import pandas as pd
from typing import Dict, List, Any

# Mock Indeed job listings
MOCK_INDEED_RESPONSE = [
    {
        "title": "Senior Software Engineer",
        "company": "Tech Company",
        "location": "Remote",
        "date_posted": "2025-03-28",
        "job_type": "fulltime",
        "remote": True,
        "url": "https://indeed.com/job/123",
        "site": "indeed",
        "description": "Example job description for Indeed. We are looking for a Senior Software Engineer with experience in Python, JavaScript, and cloud technologies. The ideal candidate will have 5+ years of experience in software development and a strong background in web technologies."
    },
    {
        "title": "Backend Developer",
        "company": "Startup Inc",
        "location": "San Francisco, CA",
        "date_posted": "2025-03-29",
        "job_type": "fulltime",
        "remote": False,
        "url": "https://indeed.com/job/456",
        "site": "indeed",
        "description": "Startup Inc is seeking a Backend Developer to join our growing team. You will be responsible for developing and maintaining our core API services, database design, and server infrastructure."
    },
    {
        "title": "DevOps Engineer",
        "company": "Cloud Solutions",
        "location": "Remote",
        "date_posted": "2025-03-30",
        "job_type": "contract",
        "remote": True,
        "url": "https://indeed.com/job/789",
        "site": "indeed",
        "description": "We are looking for a DevOps Engineer to help us build and maintain our cloud infrastructure. Experience with AWS, Kubernetes, and CI/CD pipelines is required."
    }
]

# Mock LinkedIn job listings
MOCK_LINKEDIN_RESPONSE = [
    {
        "title": "Full Stack Developer",
        "company": "LinkedIn Corp",
        "location": "New York, NY",
        "date_posted": "2025-03-29",
        "job_type": "fulltime",
        "remote": False,
        "url": "https://linkedin.com/jobs/view/123",
        "site": "linkedin",
        "description": "LinkedIn Corp is hiring a Full Stack Developer to join our New York office. You will work on our core product features, collaborating with designers, product managers, and other engineers."
    },
    {
        "title": "Frontend Engineer",
        "company": "Web Design Agency",
        "location": "Remote",
        "date_posted": "2025-03-30",
        "job_type": "fulltime",
        "remote": True,
        "url": "https://linkedin.com/jobs/view/456",
        "site": "linkedin",
        "description": "Join our team as a Frontend Engineer and help us build beautiful, responsive web applications. Experience with React, TypeScript, and modern CSS frameworks is required."
    },
    {
        "title": "Data Engineer",
        "company": "Big Data Inc",
        "location": "Chicago, IL",
        "date_posted": "2025-03-31",
        "job_type": "fulltime",
        "remote": False,
        "url": "https://linkedin.com/jobs/view/789",
        "site": "linkedin",
        "description": "Big Data Inc is looking for a Data Engineer to help us build and maintain our data pipelines. Experience with Spark, Hadoop, and cloud data services is a plus."
    }
]

# Mock Glassdoor job listings
MOCK_GLASSDOOR_RESPONSE = [
    {
        "title": "Data Scientist",
        "company": "Data Analytics Inc",
        "location": "San Francisco, CA",
        "date_posted": "2025-03-30",
        "job_type": "fulltime",
        "remote": False,
        "url": "https://glassdoor.com/job/123",
        "site": "glassdoor",
        "description": "Data Analytics Inc is seeking a Data Scientist to join our team. You will work on developing machine learning models, analyzing large datasets, and providing insights to our clients."
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Solutions",
        "location": "Remote",
        "date_posted": "2025-03-31",
        "job_type": "fulltime",
        "remote": True,
        "url": "https://glassdoor.com/job/456",
        "site": "glassdoor",
        "description": "AI Solutions is looking for a Machine Learning Engineer to help us build and deploy ML models. Experience with PyTorch or TensorFlow is required."
    },
    {
        "title": "Product Manager",
        "company": "Tech Innovations",
        "location": "Austin, TX",
        "date_posted": "2025-04-01",
        "job_type": "fulltime",
        "remote": False,
        "url": "https://glassdoor.com/job/789",
        "site": "glassdoor",
        "description": "Tech Innovations is hiring a Product Manager to lead our product development efforts. You will work closely with engineering, design, and marketing teams to define and deliver product features."
    }
]

def create_mock_jobspy_response() -> pd.DataFrame:
    """
    Create a mock JobSpy response DataFrame.
    
    Returns:
        A pandas DataFrame containing mock job listings from multiple sources.
    """
    # Combine all responses
    all_jobs = MOCK_INDEED_RESPONSE + MOCK_LINKEDIN_RESPONSE + MOCK_GLASSDOOR_RESPONSE
    
    # Convert to DataFrame (JobSpy returns pandas DataFrame)
    df = pd.DataFrame(all_jobs)
    
    return df
