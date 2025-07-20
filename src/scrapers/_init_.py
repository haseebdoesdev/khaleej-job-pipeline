"""
Web scrapers package for job data extraction
"""

from .base_scraper import BaseScraper
from .khaleej_scraper import KhaleejScraper

__all__ = ['BaseScraper', 'KhaleejScraper']