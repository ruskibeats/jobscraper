from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class JobSource(ABC):
    """Base interface for all job sources."""
    
    @abstractmethod
    async def search_jobs(
        self,
        search_term: str,
        location: str,
        remote: bool = False,
        job_type: Optional[str] = None,
        results_wanted: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for jobs with the given parameters."""
        pass
        
    @abstractmethod
    def normalize_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize job data to a standard format."""
        pass
