from typing import Dict, List, Any, Optional
import logging
from jobspy import scrape_jobs as jobspy_scrape
from .base import JobSource
from config import JobSearchConfig

logger = logging.getLogger(__name__)

class GlassdoorJobSource(JobSource):
    """Glassdoor job source implementation."""
    
    async def search_jobs(
        self,
        search_term: str,
        location: str,
        remote: bool = False,
        job_type: Optional[str] = None,
        results_wanted: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for jobs on Glassdoor."""
        try:
            # Map job type to Glassdoor format
            mapped_job_type = JobSearchConfig.map_job_type(job_type) if job_type else None
            
            # Perform search
            jobs = jobspy_scrape(
                site_name=["glassdoor"],
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                remote=remote,
                job_type=mapped_job_type
            )
            
            # Normalize and return results
            return [self.normalize_job(job) for job in jobs.to_dict(orient='records')]
        
        except Exception as e:
            logger.error(f"Error searching Glassdoor: {str(e)}")
            return []
        
    def normalize_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Glassdoor job data."""
        return {
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "location": job_data.get("location", ""),
            "remote": job_data.get("is_remote", False),
            "job_type": job_data.get("job_type", ""),
            "url": job_data.get("job_url", ""),
            "source": "glassdoor",
            "description": job_data.get("description", ""),
            "posted_at": job_data.get("date_posted", "")
        }
