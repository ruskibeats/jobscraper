#!/usr/bin/env python3
"""
Search for Field Engineer jobs in London, UK.

This script demonstrates the Job Search API by searching for Field Engineer
positions in London, UK that are remote and contract-based.
"""

import sys
import asyncio
import json
sys.path.insert(0, '.')

from api.scrapeJobs import scrape_jobs

async def search_field_engineer_jobs():
    """Search for Field Engineer jobs in London, UK."""
    print('Searching for Software Engineer jobs in London, UK...')
    
    # Define search parameters
    search_query = {
        'title': 'Software Engineer',  # Changed to a common job title
        'location': 'London',  # Using just 'London' for better Indeed compatibility
        'remote': False,      # Changed to False since remote=True filters out too many jobs
        'job_type': 'contract'
    }
    
    # Get max results parameter from environment or use default
    max_results = 50  # Default to 50 results
    
    # Execute search
    result = await scrape_jobs(search_query)
    
    # Print summary
    print(f'\nFound {len(result)} jobs from multiple sources:')
    
    # Analyze sources
    sources = {}
    for job in result:
        source = job.get('source')
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sources.items():
        print(f'- {source}: {count} jobs')
    
    # Group jobs by source
    jobs_by_source = {}
    for job in result:
        source = job.get('source')
        if source not in jobs_by_source:
            jobs_by_source[source] = []
        jobs_by_source[source].append(job)
    
    # Print top jobs from each source
    print('\nTop jobs from each source:')
    for source, jobs in jobs_by_source.items():
        print(f"\n=== {source.upper()} JOBS ===")
        for i, job in enumerate(jobs[:2]):  # Show top 2 from each source
            print(f"\n#{i+1}: {job.get('title')} at {job.get('company')} ({job.get('location')})")
            print(f"   Posted: {job.get('posted_at')}")
            print(f"   Remote: {job.get('remote')}")
            print(f"   Job Type: {job.get('job_type')}")
            
            # Print URL (handle None/NaN values)
            url = job.get('url')
            if url and str(url).lower() != 'nan':
                print(f"   URL: {url}")
            else:
                print("   URL: No URL available")
            
            # Print a truncated description (first 200 characters)
            description = job.get('description', '')
            if description:
                truncated_desc = description[:200] + '...' if len(description) > 200 else description
                print(f"   Description: {truncated_desc}")

if __name__ == "__main__":
    asyncio.run(search_field_engineer_jobs())
