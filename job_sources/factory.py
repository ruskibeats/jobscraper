from typing import Dict, List, Type
from .base import JobSource
from .indeed import IndeedJobSource
from .linkedin import LinkedInJobSource
from .glassdoor import GlassdoorJobSource
from .jobserve import JobServeJobSource

class JobSourceFactory:
    """Factory for creating job source instances."""
    
    _sources: Dict[str, Type[JobSource]] = {
        'indeed': IndeedJobSource,
        'linkedin': LinkedInJobSource,
        'glassdoor': GlassdoorJobSource,
        'jobserve': JobServeJobSource
    }
    
    @classmethod
    def create(cls, source_name: str) -> JobSource:
        """Create a job source instance by name."""
        if source_name not in cls._sources:
            raise ValueError(f"Unknown job source: {source_name}")
        return cls._sources[source_name]()
        
    @classmethod
    def create_all(cls) -> List[JobSource]:
        """Create instances of all available job sources."""
        return [source_class() for source_class in cls._sources.values()]
