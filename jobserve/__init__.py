from __future__ import annotations

import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re

import requests
from bs4 import BeautifulSoup

from jobspy.model import JobPost, JobResponse, ScraperInput, Scraper, Site, Location, Country, JobType, Compensation, CompensationInterval
from .constant import BASE_URL, SEARCH_URL, HEADERS, SELECTORS
from .util import parse_job_type, parse_date_posted, parse_salary, is_remote_job

class JobServeScraper(Scraper):
    """
    Scraper for JobServe.com
    """
    def __init__(self, proxies: List[str] = None, ca_cert: str = None):
        super().__init__(Site.JOBSERVE, proxies, ca_cert)
        self.logger = logging.getLogger("JobServe")

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrape job postings from JobServe.
        
        Args:
            scraper_input: The input parameters for the scraper.
            
        Returns:
            A JobResponse object containing the scraped job postings.
        """
        self.logger.info(f"Scraping JobServe for {scraper_input.search_term} in {scraper_input.location}")
        
        # Initialize the response
        response = JobResponse(jobs=[])
        
        try:
            # Construct the search URL
            url = self._construct_search_url(scraper_input)
            
            # Get the number of pages to scrape
            total_results_needed = scraper_input.results_wanted
            results_per_page = 20  # JobServe typically shows 20 results per page
            pages_to_scrape = (total_results_needed + results_per_page - 1) // results_per_page
            
            # Scrape each page
            for page in range(1, pages_to_scrape + 1):
                page_url = f"{url}&pg={page}" if page > 1 else url
                
                # Send a request
                self.logger.info(f"Scraping page {page} of {pages_to_scrape}")
                page_response = requests.get(page_url, headers=HEADERS)
                
                # Check if the request was successful
                if page_response.status_code != 200:
                    self.logger.error(f"Failed to get page {page}: {page_response.status_code}")
                    continue
                
                # Parse the response
                soup = BeautifulSoup(page_response.content, "html.parser")
                
                # Extract job postings
                job_elements = soup.select(SELECTORS["job_card"])
                
                if not job_elements:
                    self.logger.warning(f"No job elements found on page {page}")
                    break
                
                # Process each job posting
                for job_element in job_elements:
                    # Extract job details
                    job = self._extract_job_details(job_element, scraper_input)
                    
                    if job:
                        response.jobs.append(job)
                    
                    # Check if we have enough results
                    if len(response.jobs) >= total_results_needed:
                        break
                
                # Check if we have enough results
                if len(response.jobs) >= total_results_needed:
                    break
                
                # Sleep to avoid rate limiting
                time.sleep(2)
            
        except Exception as e:
            self.logger.error(f"Error scraping JobServe: {e}")
        
        return response
    
    def _construct_search_url(self, scraper_input: ScraperInput) -> str:
        """
        Construct the search URL based on the input parameters.
        
        Args:
            scraper_input: The input parameters for the scraper.
            
        Returns:
            The search URL.
        """
        # Base search URL
        url = SEARCH_URL
        
        # Add search term
        if scraper_input.search_term:
            url += f"?kw={scraper_input.search_term.replace(' ', '+')}"
        else:
            url += "?"
        
        # Add location
        if scraper_input.location:
            url += f"&loc={scraper_input.location.replace(' ', '+')}"
        
        # Add distance
        if scraper_input.distance:
            url += f"&rad={scraper_input.distance}"
        
        # Add job type
        if scraper_input.job_type:
            job_type_param = self._get_job_type_param(scraper_input.job_type)
            if job_type_param:
                url += f"&jt={job_type_param}"
        
        # Add remote filter
        if scraper_input.is_remote:
            url += "&remote=true"
        
        # Add posted time filter
        if scraper_input.hours_old:
            days_old = (scraper_input.hours_old + 23) // 24  # Convert hours to days, rounding up
            url += f"&posted={days_old}d"
        
        return url
    
    def _get_job_type_param(self, job_type: JobType) -> Optional[str]:
        """
        Get the job type parameter for the URL.
        
        Args:
            job_type: The job type.
            
        Returns:
            The job type parameter.
        """
        job_type_mapping = {
            JobType.FULL_TIME: "1",
            JobType.PART_TIME: "2",
            JobType.CONTRACT: "3",
            JobType.TEMPORARY: "4",
            JobType.INTERNSHIP: "5",
        }
        
        return job_type_mapping.get(job_type)
    
    def _extract_job_details(self, job_element: Any, scraper_input: ScraperInput) -> Optional[JobPost]:
        """
        Extract job details from a job element.
        
        Args:
            job_element: The job element.
            scraper_input: The input parameters for the scraper.
            
        Returns:
            A JobPost object, or None if the job details could not be extracted.
        """
        try:
            # Extract basic job details
            title_element = job_element.select_one(SELECTORS["job_title"])
            if not title_element:
                return None
            
            title = title_element.text.strip()
            
            # Extract job URL
            job_url_element = title_element.parent if title_element.parent.name == "a" else title_element.find("a")
            if not job_url_element:
                return None
            
            job_url = job_url_element.get("href")
            if not job_url.startswith("http"):
                job_url = f"{BASE_URL}{job_url}"
            
            # Extract company name
            company_element = job_element.select_one(SELECTORS["company_name"])
            company_name = company_element.text.strip() if company_element else None
            
            # Extract location
            location_element = job_element.select_one(SELECTORS["job_location"])
            location_text = location_element.text.strip() if location_element else None
            
            # Parse location
            city = None
            state = None
            if location_text:
                location_parts = location_text.split(",")
                city = location_parts[0].strip() if len(location_parts) > 0 else None
                state = location_parts[1].strip() if len(location_parts) > 1 else None
            
            # Extract job type
            job_type_element = job_element.select_one(SELECTORS["job_type"])
            job_type_text = job_type_element.text.strip() if job_type_element else None
            
            # Parse job type
            job_type_value = parse_job_type(job_type_text) if job_type_text else None
            job_type = [JobType.FULL_TIME] if job_type_value == "fulltime" else \
                      [JobType.PART_TIME] if job_type_value == "parttime" else \
                      [JobType.CONTRACT] if job_type_value == "contract" else \
                      [JobType.TEMPORARY] if job_type_value == "temporary" else \
                      [JobType.INTERNSHIP] if job_type_value == "internship" else \
                      [JobType.FULL_TIME]  # Default to full-time
            
            # Extract date posted
            date_element = job_element.select_one(SELECTORS["job_date"])
            date_text = date_element.text.strip() if date_element else None
            date_posted = parse_date_posted(date_text) if date_text else None
            
            # Extract salary
            salary_element = job_element.select_one(SELECTORS["job_salary"])
            salary_text = salary_element.text.strip() if salary_element else None
            
            # Parse salary
            compensation = None
            if salary_text:
                interval, min_amount, max_amount, currency = parse_salary(salary_text)
                if interval and (min_amount or max_amount):
                    compensation = Compensation(
                        interval=CompensationInterval(interval) if interval else None,
                        min_amount=min_amount,
                        max_amount=max_amount,
                        currency=currency
                    )
            
            # Check if remote
            is_remote = False
            if job_type_text:
                is_remote = is_remote_job(job_type_text)
            
            # Create JobPost object
            job = JobPost(
                title=title,
                company_name=company_name,
                location=Location(
                    country=scraper_input.country,
                    city=city,
                    state=state
                ),
                job_url=job_url,
                job_type=job_type,
                date_posted=date_posted.date() if date_posted else None,
                is_remote=is_remote,
                compensation=compensation
            )
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error extracting job details: {e}")
            return None
