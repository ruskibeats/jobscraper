from typing import List, Dict, Any
import logging
import asyncio
from deduplicator import deduplicate_jobs
import time
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import JobSpy - required for this module to work
try:
    # Try to import from python-jobspy (GitHub version)
    from jobspy import scrape_jobs as jobspy_scrape
    from jobspy import Site, JobType
    JOBSPY_AVAILABLE = True
    logger.info("JobSpy available for live job scraping (GitHub version)")
except ImportError:
    try:
        # Fallback to old jobspy
        from jobspy import scrape_jobs as jobspy_scrape
        from jobspy import Site, JobType
        JOBSPY_AVAILABLE = True
        logger.info("JobSpy available for live job scraping (PyPI version)")
    except ImportError:
        JOBSPY_AVAILABLE = False
        logger.error("JobSpy not available. Please install it with: pip install git+https://github.com/Bunsly/JobSpy.git")

# Import JobServe extension if available
try:
    from crawl4ai.crawlers.jobspy.jobserve_extension import search_jobserve
    JOBSERVE_AVAILABLE = True
    logger.info("JobServe extension available for UK job searches")
except ImportError:
    JOBSERVE_AVAILABLE = False
    logger.warning("JobServe extension not available. UK job searches may be limited.")

async def scrape_jobs(search_query: dict) -> List[Dict[str, Any]]:
    """
    Scrape job listings based on search query using JobSpy.
    
    Args:
        search_query: Search query parameters
        
    Returns:
        List of job listings from real job sites
    """
    logger.info(f"📊 Scraping jobs for query: {search_query}")
    
    # JobSpy is always available since we're importing it directly
    
    try:
        return await scrape_jobs_with_jobspy(search_query)
    except Exception as e:
        logger.error(f"Error scraping jobs with JobSpy: {str(e)}")
        return []

async def scrape_jobs_with_jobspy(search_query: dict) -> List[Dict[str, Any]]:
    """
    Scrape jobs using JobSpy library and JobServe extension if available.
    
    Args:
        search_query: Search query parameters
        
    Returns:
        List of job listings
    """
    # Extract search parameters
    search_term = search_query.get("title", "")
    location = search_query.get("location", "")
    remote = search_query.get("remote", False)
    job_type_str = search_query.get("job_type", "")
    
    # Convert job_type to lowercase if it's a string
    job_type = job_type_str.lower() if isinstance(job_type_str, str) else ""
    
    # Map job_type to JobSpy format
    mapped_job_type = None
    if job_type == "permanent" or job_type == "full-time":
        mapped_job_type = "fulltime"
    elif job_type == "contract":
        mapped_job_type = "contract"
    elif job_type == "part-time":
        mapped_job_type = "parttime"
    elif job_type == "internship":
        mapped_job_type = "internship"
    
    # Initialize JobSpy
    logger.info(f"Initializing JobSpy for {search_term} in {location}")
    
    # Determine which sites to use
    sites = ["indeed", "linkedin", "glassdoor"]
    
    # Ensure Indeed is included for all searches
    if "indeed" not in sites:
        sites.append("indeed")
    
    # Check if this is a UK job search
    is_uk_search = "uk" in location.lower() or "london" in location.lower() or "united kingdom" in location.lower() or "england" in location.lower() or "scotland" in location.lower() or "wales" in location.lower() or "northern ireland" in location.lower() or "edinburgh" in location.lower() or "glasgow" in location.lower() or "cardiff" in location.lower() or "belfast" in location.lower() or "manchester" in location.lower() or "liverpool" in location.lower() or "birmingham" in location.lower() or "leeds" in location.lower() or "bristol" in location.lower() or "newcastle" in location.lower() or "sheffield" in location.lower() or "nottingham" in location.lower()
    
    # Perform search
    logger.info(f"Searching for jobs with JobSpy")
    start_time = time.time()
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    
    # Define the search function
    def search_jobs():
        try:
            # Try to search with all sites first
            all_sites_jobs = jobspy_scrape(
                site_name=sites,
                search_term=search_term,
                location=location,
                results_wanted=20,  # Increased from 10 to get more results
                country_indeed="UK" if is_uk_search else "USA",
                remote=remote,
                job_type=mapped_job_type,
                fetch_full_text=True  # Try to get full job descriptions
            )
            
            # If we're doing a UK search, also do a separate Indeed-only search to ensure we get Indeed results
            if is_uk_search:
                try:
                    indeed_jobs = jobspy_scrape(
                        site_name=["indeed"],
                        search_term=search_term,
                        location=location,
                        results_wanted=5,
                        country_indeed="UK",
                        remote=remote,
                        fetch_full_text=True  # Try to get full job descriptions
                    )
                    
                    if not indeed_jobs.empty:
                        logger.info(f"Found {len(indeed_jobs)} additional jobs from Indeed UK")
                        # Combine with main results
                        return pd.concat([all_sites_jobs, indeed_jobs], ignore_index=True)
                except Exception as e_indeed:
                    logger.warning(f"Error in separate Indeed UK search: {str(e_indeed)}")
            
            return all_sites_jobs
        except Exception as e:
            logger.warning(f"Error with full search, trying individual sites: {str(e)}")
            
            # If that fails, try each site individually and combine results
            all_results = []
            
            # Try Indeed first - use specific domain for UK searches
            try:
                # For Indeed, try without job_type first if this is a UK search
                if is_uk_search and mapped_job_type:
                    try:
                        indeed_jobs = jobspy_scrape(
                            site_name=["indeed"],
                            search_term=search_term,
                            location=location,
                            results_wanted=10,
                            country_indeed="UK",
                            remote=remote,
                            fetch_full_text=True  # Try to get full job descriptions
                        )
                        if not indeed_jobs.empty:
                            all_results.append(indeed_jobs)
                            logger.info(f"Found {len(indeed_jobs)} jobs from Indeed (without job_type filter)")
                    except Exception as e_indeed_no_filter:
                        logger.warning(f"Error searching Indeed without job_type: {str(e_indeed_no_filter)}")
                
                # Try with all filters
                indeed_jobs = jobspy_scrape(
                    site_name=["indeed"],
                    search_term=search_term,
                    location=location,
                    results_wanted=10,
                    country_indeed="UK" if is_uk_search else "USA",
                    remote=remote,
                    job_type=mapped_job_type,
                    fetch_full_text=True  # Try to get full job descriptions
                )
                if not indeed_jobs.empty:
                    all_results.append(indeed_jobs)
                    logger.info(f"Found {len(indeed_jobs)} jobs from Indeed")
            except Exception as e_indeed:
                logger.warning(f"Error searching Indeed: {str(e_indeed)}")
            
            # Try LinkedIn
            try:
                linkedin_jobs = jobspy_scrape(
                    site_name=["linkedin"],
                    search_term=search_term,
                    location=location,
                    results_wanted=10,
                    remote=remote,
                    job_type=mapped_job_type,
                    fetch_full_text=True,  # Try to get full job descriptions
                    proxies=True  # Use proxies to avoid rate limiting
                )
                if not linkedin_jobs.empty:
                    all_results.append(linkedin_jobs)
                    logger.info(f"Found {len(linkedin_jobs)} jobs from LinkedIn")
            except Exception as e_linkedin:
                logger.warning(f"Error searching LinkedIn: {str(e_linkedin)}")
            
            # Try Glassdoor
            try:
                glassdoor_jobs = jobspy_scrape(
                    site_name=["glassdoor"],
                    search_term=search_term,
                    location=location,
                    results_wanted=10,
                    remote=remote,
                    job_type=mapped_job_type
                )
                if not glassdoor_jobs.empty:
                    all_results.append(glassdoor_jobs)
                    logger.info(f"Found {len(glassdoor_jobs)} jobs from Glassdoor")
            except Exception as e_glassdoor:
                logger.warning(f"Error searching Glassdoor: {str(e_glassdoor)}")
            
            # Combine results
            if all_results:
                return pd.concat(all_results, ignore_index=True)
            
            # If all individual searches failed, raise the original error
            raise e
    
    # Execute the search
    try:
        jobs = await loop.run_in_executor(None, search_jobs)
        logger.info(f"JobSpy search completed in {time.time() - start_time:.2f} seconds")
        logger.info(f"Found {len(jobs)} jobs with JobSpy")
    except Exception as e:
        logger.error(f"Error executing JobSpy search: {str(e)}")
        jobs = pd.DataFrame()  # Empty DataFrame
    
    # Add JobServe results for UK searches if available
    jobserve_jobs = pd.DataFrame()
    if JOBSERVE_AVAILABLE and is_uk_search:
        try:
            logger.info(f"Searching for jobs on JobServe")
            jobserve_start_time = time.time()
            jobserve_jobs = await search_jobserve(
                search_term=search_term,
                location=location,
                results_wanted=10,
                job_type=mapped_job_type
            )
            logger.info(f"JobServe search completed in {time.time() - jobserve_start_time:.2f} seconds")
            logger.info(f"Found {len(jobserve_jobs)} jobs on JobServe")
        except Exception as e:
            logger.error(f"Error searching JobServe: {str(e)}")
    
    # Combine results if we have both
    if not jobs.empty and not jobserve_jobs.empty:
        # Rename columns to match if needed
        if 'job_url' in jobserve_jobs.columns and 'url' not in jobserve_jobs.columns:
            jobserve_jobs = jobserve_jobs.rename(columns={'job_url': 'url'})
        
        # Combine the DataFrames
        combined_jobs = pd.concat([jobs, jobserve_jobs], ignore_index=True)
        logger.info(f"Combined {len(jobs)} JobSpy jobs with {len(jobserve_jobs)} JobServe jobs")
        jobs = combined_jobs
    elif not jobserve_jobs.empty:
        # If JobSpy failed but JobServe worked
        jobs = jobserve_jobs
        if 'job_url' in jobs.columns and 'url' not in jobs.columns:
            jobs = jobs.rename(columns={'job_url': 'url'})
    
    # Convert to our format
    normalized = []
    
    # Check if jobs is a DataFrame
    if not isinstance(jobs, pd.DataFrame) or jobs.empty:
        logger.warning("No jobs found or invalid job data format")
        return []
    
    # Process each job
    for _, job_row in jobs.iterrows():
        # Convert date to ISO format if possible
        posted_date = ""
        if hasattr(job_row, "date_posted") and job_row.date_posted:
            try:
                if isinstance(job_row.date_posted, datetime):
                    posted_date = job_row.date_posted.isoformat()
                elif isinstance(job_row.date_posted, (str, int)):
                    posted_date = str(job_row.date_posted)
                else:
                    posted_date = "Unknown"
            except:
                posted_date = "Unknown"
        
        # For LinkedIn, try to extract company info
        company_info = ""
        if hasattr(job_row, "company") and job_row.company:
            company_info = str(job_row.company)
            
            # Try to get additional company info
            if hasattr(job_row, "company_industry") and job_row.company_industry:
                company_info += f" ({job_row.company_industry})"
            elif hasattr(job_row, "company_description") and job_row.company_description:
                company_info += f" - {job_row.company_description[:100]}..."
        
        try:
            # Safely get job type
            job_type_value = ""
            if hasattr(job_row, "job_type"):
                if isinstance(job_row.job_type, str):
                    job_type_value = job_row.job_type
                elif job_row.job_type is not None:
                    job_type_value = str(job_row.job_type)
            
            # Handle different URL field names in different sources
            url = ""
            # Check for job_url first (used by LinkedIn, Glassdoor)
            if hasattr(job_row, "job_url") and job_row.job_url and str(job_row.job_url) != "nan":
                url = str(job_row.job_url)
            # Check for url (used by some sources)
            elif hasattr(job_row, "url") and job_row.url and str(job_row.url) != "nan":
                url = str(job_row.url)
            # Check for apply_link (used by some sources)
            elif hasattr(job_row, "apply_link") and job_row.apply_link and str(job_row.apply_link) != "nan":
                url = str(job_row.apply_link)
            # Check for job_url_direct (used by some sources as a backup)
            elif hasattr(job_row, "job_url_direct") and job_row.job_url_direct and str(job_row.job_url_direct) != "nan":
                url = str(job_row.job_url_direct)
            
            # Clean up URL if it's "nan" or None
            if url.lower() == "nan" or url.lower() == "none":
                url = ""
            
            # For LinkedIn, Glassdoor, and Indeed, add default job type if missing
            if hasattr(job_row, "site"):
                site = str(job_row.site).lower()
                if (site == "linkedin" or site == "glassdoor" or site == "indeed") and not job_type_value:
                    # Set default job type based on title
                    title = str(job_row.title).lower() if hasattr(job_row, "title") and job_row.title else ""
                    if "contract" in title:
                        job_type_value = "Contract"
                    elif "part-time" in title or "part time" in title:
                        job_type_value = "Part-time"
                    elif "intern" in title:
                        job_type_value = "Internship"
                    else:
                        job_type_value = "Full-time"
            
            # Add default description if missing for any source
            description = ""
            if hasattr(job_row, "description") and job_row.description and str(job_row.description).lower() != "nan":
                description = str(job_row.description)
            
            # If description is still empty or "nan", create a default one
            if not description or description.lower() == "nan":
                site = str(job_row.site).lower() if hasattr(job_row, "site") and job_row.site else "unknown"
                title = str(job_row.title) if hasattr(job_row, "title") and job_row.title else "Job"
                company = str(job_row.company) if hasattr(job_row, "company") and job_row.company else "Company"
                location = str(job_row.location) if hasattr(job_row, "location") and job_row.location else "Location"
                
                # Add salary information if available
                salary_info = ""
                if hasattr(job_row, "min_amount") and hasattr(job_row, "max_amount") and job_row.min_amount and job_row.max_amount:
                    currency = str(job_row.currency) if hasattr(job_row, "currency") and job_row.currency else "GBP"
                    interval = str(job_row.interval) if hasattr(job_row, "interval") and job_row.interval else "yearly"
                    salary_info = f" Salary range: {job_row.min_amount}-{job_row.max_amount} {currency} ({interval})."
                elif hasattr(job_row, "min_amount") and job_row.min_amount:
                    currency = str(job_row.currency) if hasattr(job_row, "currency") and job_row.currency else "GBP"
                    interval = str(job_row.interval) if hasattr(job_row, "interval") and job_row.interval else "yearly"
                    salary_info = f" Salary: {job_row.min_amount}+ {currency} ({interval})."
                
                description = f"This is a {job_type_value} {title} position at {company} in {location}.{salary_info} For more details, please click the URL to view the full job description on {site.capitalize()}."
            
            # Create job entry with safe attribute access
            job_entry = {
                "title": str(job_row.title) if hasattr(job_row, "title") and job_row.title else "",
                "company": company_info if company_info else (str(job_row.company) if hasattr(job_row, "company") and job_row.company else ""),
                "location": str(job_row.location) if hasattr(job_row, "location") and job_row.location else "",
                "remote": "true" if (hasattr(job_row, "remote") and job_row.remote) else "false",
                "job_type": job_type_value,
                "url": url,
                "source": str(job_row.site) if hasattr(job_row, "site") and job_row.site else "",
                "description": description,
                "posted_at": posted_date
            }
            normalized.append(job_entry)
        except Exception as e:
            logger.error(f"Error normalizing job: {str(e)}")
            continue
    
    # Apply deduplication
    deduplicated_jobs = deduplicate_jobs(normalized)
    
    logger.info(f"Returning {len(deduplicated_jobs)} deduplicated jobs from JobSpy")
    return deduplicated_jobs
