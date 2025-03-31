#!/usr/bin/env python3
"""
Test script for the JobServe scraper.

This script demonstrates how to use the JobServe scraper once it's integrated with JobSpy.
Note: This script will only work after you've integrated the JobServe scraper with JobSpy
as described in the README.md file.
"""

import csv
import os
import sys
import pandas as pd

# Add the parent directory to the Python path so that we can import jobspy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jobspy import scrape_jobs

def test_jobserve_alone():
    """Test the JobServe scraper alone."""
    print("Testing JobServe scraper alone...")
    
    try:
        jobs = scrape_jobs(
            site_name=["jobserve"],
            search_term="Software Engineer",
            location="London",
            results_wanted=10,
            country_indeed='UK',
        )
        
        print(f"Found {len(jobs)} jobs")
        if not jobs.empty:
            print("\nSample of jobs found:")
            print(jobs[["title", "company", "location", "job_type", "job_url"]].head())
            
            # Save to CSV
            jobs.to_csv("jobserve_jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            print("Results saved to jobserve_jobs.csv")
        else:
            print("No jobs found.")
    
    except Exception as e:
        print(f"Error testing JobServe scraper: {e}")

def test_jobserve_with_others():
    """Test the JobServe scraper with other job boards."""
    print("\nTesting JobServe scraper with other job boards...")
    
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "jobserve"],
            search_term="Software Engineer",
            location="London",
            results_wanted=10,
            country_indeed='UK',
        )
        
        print(f"Found {len(jobs)} jobs")
        if not jobs.empty:
            # Group by site and count
            site_counts = jobs.groupby("site").size().reset_index(name="count")
            print("\nJobs by site:")
            print(site_counts)
            
            print("\nSample of jobs found:")
            print(jobs[["site", "title", "company", "location"]].head())
            
            # Save to CSV
            jobs.to_csv("combined_jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            print("Results saved to combined_jobs.csv")
        else:
            print("No jobs found.")
    
    except Exception as e:
        print(f"Error testing JobServe with other job boards: {e}")

def test_remote_jobs():
    """Test searching for remote jobs on JobServe."""
    print("\nTesting remote jobs on JobServe...")
    
    try:
        jobs = scrape_jobs(
            site_name=["jobserve"],
            search_term="Software Engineer",
            location="United Kingdom",
            results_wanted=10,
            country_indeed='UK',
            is_remote=True,
        )
        
        print(f"Found {len(jobs)} remote jobs")
        if not jobs.empty:
            print("\nSample of remote jobs found:")
            print(jobs[["title", "company", "location", "is_remote"]].head())
        else:
            print("No remote jobs found.")
    
    except Exception as e:
        print(f"Error testing remote jobs: {e}")

def test_job_types():
    """Test searching for different job types on JobServe."""
    print("\nTesting different job types on JobServe...")
    
    job_types = ["fulltime", "contract"]
    
    for job_type in job_types:
        print(f"\nTesting {job_type} jobs...")
        
        try:
            jobs = scrape_jobs(
                site_name=["jobserve"],
                search_term="Software Engineer",
                location="London",
                results_wanted=5,
                country_indeed='UK',
                job_type=job_type,
            )
            
            print(f"Found {len(jobs)} {job_type} jobs")
            if not jobs.empty:
                print("\nSample of jobs found:")
                print(jobs[["title", "company", "location", "job_type"]].head())
            else:
                print(f"No {job_type} jobs found.")
        
        except Exception as e:
            print(f"Error testing {job_type} jobs: {e}")

if __name__ == "__main__":
    print("JobServe Scraper Test Script")
    print("============================")
    print("Note: This script will only work after you've integrated the JobServe scraper with JobSpy.")
    print("See README.md for integration instructions.")
    print("")
    
    # Run tests
    test_jobserve_alone()
    test_jobserve_with_others()
    test_remote_jobs()
    test_job_types()
