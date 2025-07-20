from abc import ABC, abstractmethod
from typing import List, Set, Optional
import logging

class BaseScraper(ABC):
    """
    Base class for all web scrapers
    
    This abstract class defines the interface that all scrapers must implement.
    It provides common functionality and ensures consistent behavior across
    different scraper implementations.
    """
    
    def __init__(self, config):
        """
        Initialize the base scraper
        
        Args:
            config: Configuration object containing scraper settings
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    def scrape_job_urls(self) -> Set[str]:
        """
        Scrape and return job URLs from the target website
        
        Returns:
            Set[str]: Set of unique job URLs found
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    @abstractmethod
    def scrape_job_details(self, url: str) -> Optional[dict]:
        """
        Scrape detailed information for a single job
        
        Args:
            url (str): The job URL to scrape details from
            
        Returns:
            Optional[dict]: Dictionary containing job details or None if failed
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if a URL is properly formatted
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        return url.startswith(('http://', 'https://'))
    
    def log_scraping_stats(self, total_found: int, successful: int, failed: int):
        """
        Log scraping statistics
        
        Args:
            total_found (int): Total URLs found
            successful (int): Successfully scraped count
            failed (int): Failed scraping count
        """
        success_rate = (successful / total_found * 100) if total_found > 0 else 0
        
        self.logger.info(f"Scraping completed:")
        self.logger.info(f"  Total URLs found: {total_found}")
        self.logger.info(f"  Successfully scraped: {successful}")
        self.logger.info(f"  Failed to scrape: {failed}")
        self.logger.info(f"  Success rate: {success_rate:.1f}%")