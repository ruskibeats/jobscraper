from typing import Dict, List, Any, Optional
import logging
from jobspy import scrape_jobs as jobspy_scrape
from .base import JobSource
from config import JobSearchConfig

logger = logging.getLogger(__name__)

class IndeedJobSource(JobSource):
    """Indeed job source implementation."""
    
    async def search_jobs(
        self,
        search_term: str,
        location: str,
        remote: bool = False,
        job_type: Optional[str] = None,
        results_wanted: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for jobs on Indeed."""
        try:
            # Map job type to Indeed format
            mapped_job_type = JobSearchConfig.map_job_type(job_type) if job_type else None
            
            # Determine country for Indeed search
            country_indeed = "UK" if JobSearchConfig.is_uk_location(location) else "USA"
            
            # Perform search
            jobs = jobspy_scrape(
                site_name=["indeed"],
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                country_indeed=country_indeed,
                remote=remote,
                job_type=mapped_job_type,
                fetch_full_text=True
            )
            
            # Normalize and return results
            return [self.normalize_job(job) for job in jobs.to_dict(orient='records')]
        
        except Exception as e:
            logger.error(f"Error searching Indeed: {str(e)}")
            return []
        
    def normalize_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Indeed job data."""
        return {
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "location": job_data.get("location", ""),
            "remote": job_data.get("is_remote", False),
            "job_type": job_data.get("job_type", ""),
            "url": job_data.get("job_url", ""),
            "source": "indeed",
            "description": job_data.get("description", ""),
            "posted_at": job_data.get("date_posted", "")
        }
