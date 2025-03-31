# JobServe Search

A comprehensive tool for searching and filtering job listings from JobServe and other job boards, with LLM-based intelligent filtering.

## Features

- Search for jobs across multiple job boards (JobServe, LinkedIn, Indeed, Glassdoor)
- Direct JobServe URL support for using saved searches
- LLM-based filtering to identify the most relevant jobs
- Detailed relevance scoring and explanations
- Command-line interface for easy integration into workflows

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/jobserve-search.git
   cd jobserve-search
   ```

2. Install dependencies:
   ```bash
   ./install.sh
   ```

## Usage

### Basic Job Search

```bash
./job_search.sh Job="Project Manager" Location="London" Contract="Yes"
```

### Search with LLM Filtering

```bash
./search_and_filter.sh Job="Data Engineer" Location="London" Contract="Yes" ApiKey="your-api-key"
```

### Search with Direct JobServe URL

```bash
./job_search.sh Job="Project Manager" Location="London" JobServeUrl="https://www.jobserve.com/gb/en/JobSearch.aspx?shid=YOUR_SHID"
```

### Parameters

- `Job`: Job title or search term
- `Location`: Location to search in
- `Contract`: Set to "Yes" for contract jobs
- `Sites`: Comma-separated list of job sites to search (e.g., "jobserve,linkedin,indeed")
- `Results`: Number of results to fetch (default: 100)
- `Distance`: Distance in miles from the location (default: 50)
- `Country`: Country code (default: UK)
- `JobServeUrl`: Direct JobServe search URL
- `ApiKey`: OpenAI or OpenRouter API key for LLM filtering
- `Model`: LLM model to use (default: gpt-3.5-turbo)
- `MinScore`: Minimum relevance score for filtering (default: 0.7)
- `Limit`: Maximum number of filtered results to return (default: 50)

## How It Works

1. **Search Phase**: The tool searches for jobs across specified job boards based on your criteria
2. **Filtering Phase**: The LLM evaluates each job's relevance to your search query
3. **Results**: Jobs with relevance scores above the minimum threshold are returned, ranked by relevance

## License

MIT License
