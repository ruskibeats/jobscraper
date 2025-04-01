# Job Search API Codebase Summary

## Key Components and Their Interactions

### API Layer
- **api.py**: Main FastAPI application with route definitions for synchronous job search
- **api/async_routes.py**: Asynchronous job search endpoints with task management
- **api/metrics_routes.py**: Endpoints for metrics and dashboard data

### Service Layer
- **api/scrapeJobs.py**: Core job scraping functionality using JobSpy
- **api/cacheService.py**: Caching service for storing and retrieving job search results
- **api/dbService.py**: Database service for storing jobs and tracking search queries

### Monitoring
- **metrics_collector.py**: Collects system and API metrics at regular intervals

### Testing
- **tests/api/**: API endpoint tests
- **tests/integration/**: Integration tests with mock responses
- **tests/load/**: Load testing with Locust
- **run_tests.py**: Test runner script

## Data Flow

1. **Job Search Request Flow**:
   - User sends a search request to `/search` endpoint
   - API checks cache for existing results
   - If not found, calls JobSpy to scrape job listings
   - Results are stored in cache and database
   - Deduplicated results are returned to the user

2. **Async Job Search Flow**:
   - User sends a search request to `/async/search` endpoint
   - API enqueues a job search task and returns a task ID
   - User can check task status with `/async/search/{task_id}/status`
   - When task is complete, user can get results with `/async/search/{task_id}/results`

3. **Metrics Flow**:
   - Metrics collector runs at regular intervals
   - Collects system metrics (CPU, memory) and API metrics (requests, queue status)
   - Metrics are stored in memory
   - User can view metrics with `/metrics/dashboard` endpoint

## External Dependencies

### JobSpy
- Used for scraping job listings from multiple job boards
- Integrated in `scrapeJobs.py`
- Mocked in integration tests

### FastAPI and Related Libraries
- Core web framework with routing, validation, and OpenAPI documentation
- TestClient for API testing

### Testing Libraries
- pytest and pytest-asyncio for testing
- unittest.mock for mocking
- Locust for load testing

## Recent Significant Changes

1. **Multi-Source Integration**:
   - Successfully integrated multiple job sources (LinkedIn, Glassdoor, Indeed, JobServe)
   - Implemented UK-specific handling for better regional results
   - Added JobServe integration for specialized UK job searches

2. **Description Enhancement**:
   - Fixed "nan" description issue in LinkedIn results
   - Added default descriptions with meaningful job information
   - Included salary information when available

3. **Performance Optimization**:
   - Increased result limits for more comprehensive searches
   - Added proxy support for LinkedIn to avoid rate limiting
   - Implemented separate Indeed search for UK locations

4. **Code Review and Refactoring Plan**:
   - Identified issues in code structure and organization
   - Created comprehensive refactoring plan
   - Updated project roadmap and current task documentation

## User Feedback Integration

Recent user feedback has highlighted the need for:

1. **Better UK Job Search Support**: Improved results for UK-based job searches
2. **More Comprehensive Results**: Increased number of results from each source
3. **Better Job Descriptions**: More detailed and consistent job descriptions
4. **Performance Concerns**: Potential performance impact from increased result limits

These points have been addressed by:
- Enhancing UK job search with JobServe integration and UK-specific handling
- Increasing result limits for more comprehensive searches
- Fixing LinkedIn job description issues and adding default descriptions
- Creating a refactoring plan to address performance concerns
