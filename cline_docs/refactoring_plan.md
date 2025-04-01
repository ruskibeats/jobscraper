# Job Search API Refactoring Plan

## Overview

Based on the code review, this document outlines a comprehensive plan for refactoring the Job Search API to improve maintainability, testability, and performance. The plan focuses on addressing the identified issues while preserving the enhanced functionality.

## Goals

1. Improve code organization and maintainability
2. Enhance testability and test coverage
3. Optimize performance
4. Reduce technical debt
5. Improve documentation

## Phase 1: Code Restructuring

### 1.1 Create Job Source Interface

Create a common interface for all job sources:

```python
# job_sources/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class JobSource(ABC):
    """Base interface for all job sources."""
    
    @abstractmethod
    async def search_jobs(
        self,
        search_term: str,
        location: str,
        remote: bool = False,
        job_type: Optional[str] = None,
        results_wanted: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for jobs with the given parameters."""
        pass
        
    @abstractmethod
    def normalize_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize job data to a standard format."""
        pass
```

### 1.2 Implement Job Source Modules

Create separate modules for each job source:

```
job_sources/
  ├── __init__.py
  ├── base.py
  ├── indeed.py
  ├── linkedin.py
  ├── glassdoor.py
  └── jobserve.py
```

Each module will implement the `JobSource` interface.

### 1.3 Create Job Source Factory

Implement a factory for selecting and instantiating job sources:

```python
# job_sources/factory.py
from typing import Dict, List, Type
from .base import JobSource
from .indeed import IndeedJobSource
from .linkedin import LinkedInJobSource
from .glassdoor import GlassdoorJobSource
from .jobserve import JobServeJobSource

class JobSourceFactory:
    """Factory for creating job source instances."""
    
    _sources: Dict[str, Type[JobSource]] = {
        'indeed': IndeedJobSource,
        'linkedin': LinkedInJobSource,
        'glassdoor': GlassdoorJobSource,
        'jobserve': JobServeJobSource
    }
    
    @classmethod
    def create(cls, source_name: str) -> JobSource:
        """Create a job source instance by name."""
        if source_name not in cls._sources:
            raise ValueError(f"Unknown job source: {source_name}")
        return cls._sources[source_name]()
        
    @classmethod
    def create_all(cls) -> List[JobSource]:
        """Create instances of all available job sources."""
        return [source_class() for source_class in cls._sources.values()]
```

### 1.4 Create Configuration Module

Move hard-coded values to a configuration module:

```python
# config.py
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
```

### 1.5 Refactor Main Scraping Module

Refactor `scrapeJobs.py` to use the new structure:

```python
# api/scrapeJobs.py
from typing import List, Dict, Any
import logging
import asyncio
from deduplicator import deduplicate_jobs
import time
from datetime import datetime

from config import JobSearchConfig
from job_sources.factory import JobSourceFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_jobs(search_query: dict) -> List[Dict[str, Any]]:
    """
    Scrape job listings based on search query using multiple job sources.
    
    Args:
        search_query: Search query parameters
        
    Returns:
        List of job listings from real job sites
    """
    logger.info(f"📊 Scraping jobs for query: {search_query}")
    
    # Extract search parameters
    search_term = search_query.get("title", "")
    location = search_query.get("location", "")
    remote = search_query.get("remote", False)
    job_type_str = search_query.get("job_type", "")
    
    # Map job type to standardized format
    mapped_job_type = JobSearchConfig.map_job_type(job_type_str) if job_type_str else None
    
    # Check if this is a UK job search
    is_uk_search = JobSearchConfig.is_uk_location(location)
    
    # Select job sources based on location
    job_sources = []
    if is_uk_search:
        # For UK searches, include JobServe
        job_sources = JobSourceFactory.create_all()
    else:
        # For non-UK searches, exclude JobServe
        job_sources = [
            JobSourceFactory.create('indeed'),
            JobSourceFactory.create('linkedin'),
            JobSourceFactory.create('glassdoor')
        ]
    
    # Execute searches in parallel
    tasks = []
    for source in job_sources:
        task = asyncio.create_task(
            source.search_jobs(
                search_term=search_term,
                location=location,
                remote=remote,
                job_type=mapped_job_type,
                results_wanted=JobSearchConfig.DEFAULT_RESULTS_PER_SOURCE
            )
        )
        tasks.append(task)
    
    # Wait for all searches to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    all_jobs = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error searching {job_sources[i].__class__.__name__}: {str(result)}")
        else:
            all_jobs.extend(result)
            logger.info(f"Found {len(result)} jobs from {job_sources[i].__class__.__name__}")
    
    # Apply deduplication
    deduplicated_jobs = deduplicate_jobs(all_jobs)
    
    logger.info(f"Returning {len(deduplicated_jobs)} deduplicated jobs")
    return deduplicated_jobs
```

## Phase 2: Testing Improvements

### 2.1 Create Unit Tests for Job Sources

Create unit tests for each job source module:

```
tests/unit/
  ├── __init__.py
  ├── test_indeed_source.py
  ├── test_linkedin_source.py
  ├── test_glassdoor_source.py
  └── test_jobserve_source.py
```

### 2.2 Create Mock Responses

Create mock responses for each job source:

```
tests/mocks/
  ├── __init__.py
  ├── indeed_responses.py
  ├── linkedin_responses.py
  ├── glassdoor_responses.py
  └── jobserve_responses.py
```

### 2.3 Implement Integration Tests

Create integration tests for the refactored code:

```
tests/integration/
  ├── __init__.py
  ├── test_uk_job_search.py
  ├── test_multi_source_integration.py
  └── test_jobserve_integration.py
```

### 2.4 Create Performance Tests

Implement performance tests:

```
tests/performance/
  ├── __init__.py
  ├── test_search_performance.py
  └── test_parallel_requests.py
```

## Phase 3: Performance Optimization

### 3.1 Optimize DataFrame Operations

Fix the FutureWarning in DataFrame concatenation:

```python
# Before concatenation, ensure all DataFrames have the same columns
def safe_concat(dataframes):
    """Safely concatenate DataFrames with different columns."""
    if not dataframes:
        return pd.DataFrame()
        
    # Get all unique columns
    all_columns = set()
    for df in dataframes:
        all_columns.update(df.columns)
        
    # Ensure all DataFrames have the same columns
    for i, df in enumerate(dataframes):
        for col in all_columns:
            if col not in df.columns:
                dataframes[i][col] = None
                
    return pd.concat(dataframes, ignore_index=True)
```

### 3.2 Implement Rate Limiting

Add rate limiting for external API calls:

```python
# utils/rate_limiter.py
import asyncio
import time
from typing import Dict, Any, Callable, Awaitable

class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0.0
        
    async def execute(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Execute a function with rate limiting."""
        # Calculate time since last call
        now = time.time()
        time_since_last_call = now - self.last_call_time
        
        # If we need to wait, do so
        if time_since_last_call < self.min_interval:
            wait_time = self.min_interval - time_since_last_call
            await asyncio.sleep(wait_time)
            
        # Update last call time
        self.last_call_time = time.time()
        
        # Execute the function
        return await func(*args, **kwargs)
```

### 3.3 Implement Configurable Result Limits

Add configurable result limits:

```python
# config.py
class JobSearchConfig:
    # ... existing code ...
    
    @classmethod
    def get_results_wanted(cls, source_name: str, is_uk_search: bool) -> int:
        """Get the number of results wanted for a specific source."""
        if source_name == 'indeed' and is_uk_search:
            return 15  # More results for Indeed UK searches
        elif source_name == 'jobserve' and is_uk_search:
            return 20  # More results for JobServe UK searches
        else:
            return cls.DEFAULT_RESULTS_PER_SOURCE
```

## Phase 4: Documentation Updates

### 4.1 Update API Documentation

Update API documentation with new features:

```markdown
# Job Search API Documentation

## Endpoints

### GET /search

Search for jobs across multiple job boards.

#### Parameters

- `title` (string, required): Job title or keywords
- `location` (string, required): Job location
- `remote` (boolean, optional): Filter for remote jobs
- `job_type` (string, optional): Job type (fulltime, contract, parttime, internship)

#### UK-Specific Features

For UK job searches (location contains UK, London, etc.):
- JobServe results are included
- Indeed UK-specific domain is used
- Additional UK-specific filters are applied
```

### 4.2 Create Usage Examples

Add usage examples for UK-specific searches:

```python
# UK Software Engineer Search
search_query = {
    'title': 'Software Engineer',
    'location': 'London',
    'remote': False,
    'job_type': 'contract'
}

# Execute search
result = await scrape_jobs(search_query)
```

### 4.3 Create Troubleshooting Guide

Create a troubleshooting guide:

```markdown
# Job Search API Troubleshooting Guide

## Common Issues

### No Results from a Specific Source

If you're not getting results from a specific source:

1. Check if the source is available for your location
2. Verify that your search parameters are valid
3. Check the logs for any errors from that source

### UK-Specific Issues

For UK job searches:

1. Ensure the location contains UK-specific keywords (London, UK, etc.)
2. Check if JobServe is available and configured correctly
3. Verify that Indeed UK-specific domain is being used
```

## Implementation Timeline

1. **Phase 1: Code Restructuring** - 2 weeks
   - Week 1: Create interfaces and job source modules
   - Week 2: Implement factory and configuration

2. **Phase 2: Testing Improvements** - 2 weeks
   - Week 1: Create unit tests and mock responses
   - Week 2: Implement integration and performance tests

3. **Phase 3: Performance Optimization** - 1 week
   - Optimize DataFrame operations
   - Implement rate limiting
   - Add configurable result limits

4. **Phase 4: Documentation Updates** - 1 week
   - Update API documentation
   - Create usage examples
   - Create troubleshooting guide

## Conclusion

This refactoring plan addresses the issues identified in the code review while preserving the enhanced functionality. By implementing this plan, the Job Search API will be more maintainable, testable, and performant in production.
