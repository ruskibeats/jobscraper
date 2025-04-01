# Job Search API Technology Stack

## Backend Framework
- **FastAPI**: Chosen for its high performance, automatic OpenAPI documentation, and built-in validation. FastAPI's async support is particularly valuable for handling concurrent job search requests.

## Job Search Integration
- **JobSpy**: A Python library that provides access to multiple job boards including LinkedIn, Indeed, and Glassdoor. Selected for its comprehensive coverage and ease of integration.
- **JobServe Integration**: Custom implementation for JobServe job board, particularly useful for UK contract positions.

## Data Storage
- **In-memory storage** (for development): Currently using Python dictionaries for caching and data storage.
- **Planned production storage**:
  - **Redis**: For caching job search results and managing task queues
  - **PostgreSQL**: For persistent storage of job listings and analytics data

## Testing
- **pytest**: Core testing framework with support for both synchronous and asynchronous tests
- **pytest-asyncio**: Extension for testing asynchronous code
- **TestClient (FastAPI)**: For testing API endpoints without starting a server
- **unittest.mock**: For mocking external dependencies during testing
- **Locust**: For load testing and performance analysis

## Monitoring and Metrics
- **Custom metrics collection**: Tracking system and API metrics
- **Dashboard**: Simple web dashboard for visualizing metrics

## CI/CD
- **GitHub Actions**: For automated testing and deployment
- **Docker**: For containerization and consistent deployment environments

## Development Tools
- **Python 3.11+**: Core programming language
- **uvicorn**: ASGI server for running the FastAPI application
- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linter
- **mypy**: Static type checker

## Architecture Decisions

### Asynchronous Processing
The API supports both synchronous and asynchronous job search requests. Asynchronous requests are particularly useful for long-running searches across multiple job boards, allowing users to check status and retrieve results when ready.

### Caching Strategy
Job search results are cached using a simple key-value store (to be replaced with Redis in production). The cache key is generated from a hash of the search parameters, ensuring consistent caching behavior.

### Task Queue
A simple in-memory task queue is used for managing asynchronous job searches. In production, this would be replaced with a more robust solution like Celery or Redis-based queues.

### Metrics Collection
System and API metrics are collected at regular intervals and stored in memory. This provides insights into API usage patterns and system performance.
