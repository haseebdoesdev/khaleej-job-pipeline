
from pathlib import Path
from typing import Dict, Any
import os
from dataclasses import dataclass

@dataclass
class ScrapingConfig:
    """Configuration for web scraping"""
    base_url: str = "https://buzzon.khaleejtimes.com/ad-category/jobs-vacancies/"
    max_retries: int = 5
    retry_delay: int = 8
    timeout: int = 30
    max_workers: int = 10
    
    headers: Dict[str, str] = None
    cookies: Dict[str, str] = None
    selectors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            }
        
        if self.cookies is None:
            self.cookies = {
                "ct_sfw_pass_key": "4a1b84682f291a73f6cf5f3c3f2590810",
                "wordpress_test_cookie": "WP Cookie check",
                "ct_timezone": "5",
                "PHPSESSID": "tej3q9gt9e26bt8nqpu1s49ubv",
            }
        
        if self.selectors is None:
            self.selectors = {
                "pages": "div.paging > div.pages > span.total",
                "urls": "div.post-left > a",
                "description": "div.single-main",
                "details": "div.bigright ul",
            }

@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    gemini_api_key: str = ""
    google_places_api_key: str = ""
    model_name: str = "gemini-1.5-flash"
    max_tokens: int = 8000
    
    def __post_init__(self):
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyAsCniqEhNyOK9xfPKP3bLZ4msfI9ul-qM')
        if not self.google_places_api_key:
            self.google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', 'AIzaSyDbVb3d7eBdRnAtAxs1STwhGh4ttbhiiB4')

@dataclass
class BloggerConfig:
    """Configuration for Blogger publishing"""
    browser_id: str = "3bc7d8d47e1f4b31a38416e8d00083e0"
    selenium_url: str = "http://127.0.0.1:54345"
    blog_base_url: str = "https://www.blogger.com/"
    
@dataclass
class AppConfig:
    """Main application configuration"""
    data_dir: Path = Path("data")
    logs_dir: Path = Path("logs")
    jobs_file: Path = Path("data/jobs.json")
    processed_jobs_file: Path = Path("data/processed_jobs.json")
    
    schedule_interval_minutes: int = 30
    
    scraping: ScrapingConfig = None
    processing: ProcessingConfig = None
    blogger: BloggerConfig = None
    
    def __post_init__(self):
        if self.scraping is None:
            self.scraping = ScrapingConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
        if self.blogger is None:
            self.blogger = BloggerConfig()
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
