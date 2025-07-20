import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException
from time import sleep
from datetime import datetime
from typing import Set, Optional, Dict, Any
from .base_scraper import BaseScraper
from ..models.job_models import RawJobData

class KhaleejScraper(BaseScraper):
    """Scraper for Khaleej Times jobs"""
    
    def __init__(self, config):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(config.headers)
        self.session.cookies.update(config.cookies)
        self.job_urls = set()
    
    def _make_request(self, url: str, retries: int = 0) -> Optional[str]:
        """Make HTTP request with retry logic"""
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", self.config.retry_delay))
                self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                sleep(retry_after)
                if retries < self.config.max_retries:
                    return self._make_request(url, retries + 1)
        except RequestException as e:
            if retries < self.config.max_retries:
                wait_time = self.config.retry_delay * (retries + 1)
                self.logger.warning(f"Request failed: {str(e)}. Retrying in {wait_time} seconds...")
                sleep(wait_time)
                return self._make_request(url, retries + 1)
            else:
                self.logger.error(f"Max retries reached for URL: {url}")
        return None
    
    def _get_total_pages(self) -> int:
        """Get total number of pages"""
        html = self._make_request(self.config.base_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            pagination = soup.select_one(self.config.selectors["pages"])
            if pagination:
                pages = pagination.text.split()[-1]
                if pages.isdigit():
                    return int(pages)
        return 1
    
    def _gather_job_urls_from_page(self, page: int) -> Set[str]:
        """Gather job URLs from a specific page"""
        url = f"{self.config.base_url}page/{page}/"
        html = self._make_request(url)
        urls = set()
        
        if html:
            soup = BeautifulSoup(html, "html.parser")
            listings = soup.select(self.config.selectors["urls"])
            urls = {listing.get("href") for listing in listings if listing.get("href")}
            self.logger.info(f"Found {len(urls)} URLs on page {page}")
        
        return urls
    
    def scrape_job_urls(self) -> Set[str]:
        """Scrape all job URLs"""
        total_pages = self._get_total_pages()
        self.logger.info(f"Found {total_pages} pages to scrape")
        
        all_urls = set()
        
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_page = {
                executor.submit(self._gather_job_urls_from_page, page): page 
                for page in range(1, total_pages + 1)
            }
            
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    urls = future.result()
                    all_urls.update(urls)
                    self.logger.info(f"Completed page {page}, total URLs: {len(all_urls)}")
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {str(e)}")
        
        self.logger.info(f"Total URLs found: {len(all_urls)}")
        return all_urls
    
    def _clean_job_data(self, details, description, url: str) -> Optional[Dict[str, Any]]:
        """Clean and structure job data"""
        if not details or not description:
            return None
        
        description_text = description.get_text(strip=True) if description else ""
        
        job_data = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "description": description_text
        }
        
        # Parse details list
        for item in details.find_all("li"):
            label_elem = item.find("span")
            if not label_elem:
                continue
            
            label = label_elem.text.strip().rstrip(":").lower()
            value = item.get_text(strip=True).replace(label_elem.get_text(strip=True), "").strip()
            field_name = label.replace(" ", "_")
            
            # Special handling for email
            if field_name == "email":
                email_link = item.find("a")
                if email_link and email_link.get("href"):
                    value = email_link["href"].replace("mailto:", "")
            
            job_data[field_name] = value
        
        return job_data
    
    def scrape_job_details(self, url: str) -> Optional[RawJobData]:
        """Scrape details for a single job"""
        html = self._make_request(url)
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            details = soup.select_one(self.config.selectors["details"])
            description = soup.select_one(self.config.selectors["description"])
            
            job_data = self._clean_job_data(details, description, url)
            if job_data:
                return RawJobData(**job_data)
            
        except Exception as e:
            self.logger.error(f"Error scraping job details from {url}: {str(e)}")
        
        return None
