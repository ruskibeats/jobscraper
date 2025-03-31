#!/usr/bin/env python3
"""
Script to search for jobs using JobSpy with command-line parameters.

Example usage:
    python search_jobs.py --job "Project Manager" --location "London" --contract --output "project_manager_jobs.csv"
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime

# Add the parent directory to the Python path so that we can import jobspy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jobspy import scrape_jobs
from jobspy.model import JobType




def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Search for jobs using JobSpy.')
    
    # Required arguments
    parser.add_argument('--job', required=True, help='Job title or search term')
    parser.add_argument('--location', required=True, help='Location to search in')
    
    # Optional arguments
    parser.add_argument('--output', default='jobs.csv', help='Output file path (CSV format)')
    parser.add_argument('--sites', default='jobserve', help='Comma-separated list of job sites to search (e.g., "jobserve,linkedin,indeed")')
    parser.add_argument('--results', type=int, default=100, help='Number of results to fetch')
    parser.add_argument('--distance', type=int, default=50, help='Distance in miles from the location')
    parser.add_argument('--country', default='UK', help='Country code (e.g., UK, US, CA)')
    parser.add_argument('--jobserve-url', help='Direct JobServe search URL (e.g., "https://www.jobserve.com/gb/en/JobSearch.aspx?shid=A52743B548BF3DE25A4A")')
    
    # Job type flags
    parser.add_argument('--contract', action='store_true', help='Search for contract jobs')
    parser.add_argument('--permanent', action='store_true', help='Search for permanent jobs')
    parser.add_argument('--remote', action='store_true', help='Search for remote jobs')
    
    return parser.parse_args()

def main():
    """Main function to search for jobs and save results."""
    args = parse_arguments()
    
    # Parse job sites
    sites = [site.strip() for site in args.sites.split(',')]
    
    # Determine job type
    job_type = None
    if args.contract:
        job_type = "contract"
    elif args.permanent:
        job_type = "fulltime"
    
    print(f"Searching for '{args.job}' in {args.location}...")
    print(f"Sites: {', '.join(sites)}")
    print(f"Job type: {job_type if job_type else 'Any'}")
    print(f"Remote: {'Yes' if args.remote else 'No'}")
    print(f"Results wanted: {args.results}")
    print(f"Distance: {args.distance} miles")
    print(f"Country: {args.country}")
    
    try:
        # Check if a direct JobServe URL is provided
        if args.jobserve_url and 'jobserve' in sites:
            print(f"Using direct JobServe URL: {args.jobserve_url}")
            
            # Instead of using the scraper, let's use the JobServe API directly
            import requests
            import json
            
            print("Using JobServe API directly...")
            
            # Extract the shid from the URL
            import re
            shid_match = re.search(r'shid=([A-Z0-9]+)', args.jobserve_url)
            if not shid_match:
                print("Error: Could not extract shid from URL")
                return
            
            shid = shid_match.group(1)
            print(f"Using shid: {shid}")
            
            # Let's try using the JobServe API directly to retrieve jobs
            print("Using JobServe API directly to retrieve jobs...")
            
            # Set up the API request headers
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json; charset=UTF-8',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Referer': args.jobserve_url,
            }
            
            # Try multiple API endpoints to maximize our chances of getting job data
            
            # 1. RetrieveJobs endpoint - this seems to be the main endpoint for retrieving job listings
            retrieve_jobs_url = 'https://www.jobserve.com/WebServices/JobSearch.asmx/RetrieveJobs'
            retrieve_jobs_data = f'{{"shid":"{shid}"}}'
            
            print(f"Trying RetrieveJobs API endpoint with shid: {shid}")
            retrieve_jobs_response = requests.post(retrieve_jobs_url, headers=headers, data=retrieve_jobs_data)
            
            if retrieve_jobs_response.status_code == 200:
                print("Successfully retrieved jobs from RetrieveJobs API endpoint")
                try:
                    # Save the API response for debugging
                    with open('jobserve_api_response.json', 'w', encoding='utf-8') as f:
                        f.write(retrieve_jobs_response.text)
                    print("Saved API response to jobserve_api_response.json for debugging")
                except Exception as e:
                    print(f"Error saving API response: {e}")
            else:
                print(f"RetrieveJobs API request failed with status code {retrieve_jobs_response.status_code}")
            
            # 2. GetSavedSearchManagerWEmail endpoint - this might provide additional metadata
            saved_search_url = 'https://www.jobserve.com/WebServices/JobSearch.asmx/GetSavedSearchManagerWEmail'
            saved_search_data = f'{{ suggestedJobTitle: \'{args.job} {args.location} {datetime.now().strftime("%d %b %Y")}\' }}'
            
            print("Trying GetSavedSearchManagerWEmail API endpoint")
            saved_search_response = requests.post(saved_search_url, headers=headers, data=saved_search_data)
            
            if saved_search_response.status_code == 200:
                print("Successfully retrieved data from GetSavedSearchManagerWEmail API endpoint")
            else:
                print(f"GetSavedSearchManagerWEmail API request failed with status code {saved_search_response.status_code}")
            
            # 3. GetInternationalOpportunity endpoint - this might provide international job opportunities
            international_url = 'https://www.jobserve.com/WebServices/JobSearch.asmx/GetInternationalOpportunity'
            international_data = f'{{"shid":"{shid}"}}'
            
            print("Trying GetInternationalOpportunity API endpoint")
            international_response = requests.post(international_url, headers=headers, data=international_data)
            
            if international_response.status_code == 200:
                print("Successfully retrieved data from GetInternationalOpportunity API endpoint")
            else:
                print(f"GetInternationalOpportunity API request failed with status code {international_response.status_code}")
            
            # Also make a request to the JobServe website to scrape job listings
            print("Also scraping job listings from JobServe website...")
            response = requests.get(args.jobserve_url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error: API request failed with status code {response.status_code}")
                print(response.text)
                return
            
            # Parse the HTML response
            try:
                from bs4 import BeautifulSoup
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Save the HTML content for debugging
                with open('jobserve_debug.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("Saved HTML content to jobserve_debug.html for debugging")
                
                # Look for job listings using the correct CSS selectors from the repository
                job_listings = soup.select('#jsJobResContent .jobItem')
                print(f"Found {len(job_listings)} job listings on the page")
                
                # Initialize job data list
                job_data = []
                
                # Extract job details from job listings
                for job in job_listings:
                    try:
                        # Extract job ID
                        job_id = job.get('id', '')
                        
                        # Extract job title
                        title_element = job.select_one('h3.jobResultsTitle')
                        title = title_element.text.strip() if title_element else 'Unknown Title'
                        
                        # Extract salary
                        salary_element = job.select_one('p.jobResultsSalary')
                        salary = salary_element.text.strip() if salary_element else ''
                        
                        # Extract location
                        location_element = job.select_one('p.jobResultsLoc')
                        location = location_element.text.strip() if location_element else 'Unknown Location'
                        
                        # Extract job type
                        job_type_element = job.select_one('p.jobResultsType')
                        job_type_text = job_type_element.text.strip() if job_type_element else ''
                        job_type_value = job_type if job_type else ('contract' if 'Contract' in job_type_text else 'fulltime')
                        
                        # Extract posting date
                        date_element = job.select_one('p.when')
                        date_posted = date_element.text.strip() if date_element else ''
                        
                        # Create job URL
                        job_url = f'https://www.jobserve.com/gb/en/JobDetail.aspx?id={job_id}' if job_id else args.jobserve_url
                        
                        # Add to job data
                        job_data.append({
                            'title': title,
                            'company': 'JobServe',  # Company name is not directly available in the HTML
                            'location': location,
                            'job_type': job_type_value,
                            'job_url': job_url,
                            'description': f"Salary: {salary}, Posted: {date_posted}",  # Use salary and date as description
                            'site': 'jobserve'
                        })
                    except Exception as e:
                        print(f"Error extracting featured job details: {e}")
                
                # If no featured jobs found, try to find regular job listings
                if not job_data:
                    print("No featured jobs found, trying to find regular job listings")
                    
                    # Try different CSS selectors for job listings
                    regular_jobs = soup.select('div.jobListItem')
                    if not regular_jobs:
                        regular_jobs = soup.select('div.jobItem')
                    if not regular_jobs:
                        regular_jobs = soup.select('div[class*="job"]')
                    
                    print(f"Found {len(regular_jobs)} regular job listings on the page")
                    
                    # Extract job details from regular jobs
                    for job in regular_jobs:
                        try:
                            # Extract job title and URL
                            title_element = job.select_one('a.jobListItemTitle')
                            title = title_element.text.strip() if title_element else 'Unknown Title'
                            job_url = 'https://www.jobserve.com' + title_element['href'] if title_element and 'href' in title_element.attrs else args.jobserve_url
                            
                            # Extract company name
                            company_element = job.select_one('span.jobListCompany')
                            company = company_element.text.strip() if company_element else 'Unknown Company'
                            
                            # Extract location
                            location_element = job.select_one('span.jobListLocation')
                            location = location_element.text.strip() if location_element else 'Unknown Location'
                            
                            # Extract job type
                            job_type_element = job.select_one('span.jobListJobType')
                            job_type_text = job_type_element.text.strip() if job_type_element else ''
                            job_type_value = job_type if job_type else ('contract' if 'Contract' in job_type_text else 'fulltime')
                            
                            # Extract description
                            description_element = job.select_one('div.jobListItemDescription')
                            description = description_element.text.strip() if description_element else ''
                            
                            # Add to job data
                            job_data.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'job_type': job_type_value,
                                'job_url': job_url,
                                'description': description,
                                'site': 'jobserve'
                            })
                        except Exception as e:
                            print(f"Error extracting regular job details: {e}")
                
                # If still no jobs found, try to extract from job titles
                if not job_data:
                    print("No job listings found with CSS selectors, trying to extract from job titles")
                    
                    # Look for job titles
                    job_titles = soup.select('a[href*="JobDetail"]')
                    print(f"Found {len(job_titles)} job titles")
                    
                    # Extract job details from job titles
                    for title_element in job_titles:
                        try:
                            title = title_element.text.strip()
                            job_url = 'https://www.jobserve.com' + title_element['href'] if 'href' in title_element.attrs else args.jobserve_url
                            
                            # Add to job data
                            job_data.append({
                                'title': title,
                                'company': 'JobServe',
                                'location': args.location,
                                'job_type': job_type if job_type else 'fulltime',
                                'job_url': job_url,
                                'description': '',
                                'site': 'jobserve'
                            })
                        except Exception as e:
                            print(f"Error extracting job title details: {e}")
                
                # Create DataFrame
                if job_data:
                    jobs = pd.DataFrame(job_data)
                    print(f"Extracted {len(jobs)} jobs from JobServe")
                else:
                    print("No jobs found on JobServe")
                    # Create an empty DataFrame with the expected columns
                    jobs = pd.DataFrame(columns=['title', 'company', 'location', 'job_type', 'job_url', 'description', 'site'])
                
                # Remove 'jobserve' from sites to avoid duplicate scraping
                sites = [site for site in sites if site != 'jobserve']
                
                # Scrape other sites if any
                if sites:
                    other_jobs = scrape_jobs(
                        site_name=sites,
                        search_term=args.job,
                        location=args.location,
                        results_wanted=args.results,
                        country_indeed=args.country,
                        job_type=job_type,
                        distance=args.distance,
                        is_remote=args.remote
                    )
                    
                    # Combine results
                    if not other_jobs.empty:
                        jobs = pd.concat([jobs, other_jobs], ignore_index=True)
                
            except Exception as e:
                print(f"Error parsing API response: {e}")
                print(f"Response text: {response.text}")
                return
        else:
            # Standard search across all specified sites
            jobs = scrape_jobs(
                site_name=sites,
                search_term=args.job,
                location=args.location,
                results_wanted=args.results,
                country_indeed=args.country,
                job_type=job_type,
                distance=args.distance,
                is_remote=args.remote
            )
        
        # Check if we found any jobs
        if jobs.empty:
            print("No jobs found.")
            return
        
        # Print summary
        print(f"\nFound {len(jobs)} jobs")
        
        # Group by site and count
        if len(sites) > 1:
            site_counts = jobs.groupby("site").size().reset_index(name="count")
            print("\nJobs by site:")
            print(site_counts)
        
        # Print sample of jobs found
        print("\nSample of jobs found:")
        print(jobs[["title", "company", "location", "job_type", "job_url"]].head())
        
        # Save to CSV
        jobs.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}")
        
    except Exception as e:
        print(f"Error searching for jobs: {e}")

if __name__ == "__main__":
    main()
