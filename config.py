from typing import Dict, Any, List

class JobSearchConfig:
    """Configuration for job search functionality."""
    
    # Default result limits
    DEFAULT_RESULTS_WANTED = 20
    DEFAULT_RESULTS_PER_SOURCE = 10
    
    # UK location detection
    UK_LOCATION_KEYWORDS = [
        "uk", "london", "united kingdom", "england", "scotland", 
        "wales", "northern ireland", "edinburgh", "glasgow", 
        "cardiff", "belfast", "manchester", "liverpool", 
        "birmingham", "leeds", "bristol", "newcastle", 
        "sheffield", "nottingham"
    ]
    
    # Job type mapping
    JOB_TYPE_MAPPING = {
        "permanent": "fulltime",
        "full-time": "fulltime",
        "contract": "contract",
        "part-time": "parttime",
        "internship": "internship"
    }
    
    # Proxy settings
    USE_PROXIES_FOR_LINKEDIN = True
    
    @classmethod
    def is_uk_location(cls, location: str) -> bool:
        """Check if a location is in the UK."""
        location_lower = location.lower()
        return any(keyword in location_lower for keyword in cls.UK_LOCATION_KEYWORDS)
        
    @classmethod
    def map_job_type(cls, job_type: str) -> str:
        """Map job type to standardized format."""
        return cls.JOB_TYPE_MAPPING.get(job_type.lower(), job_type.lower())
