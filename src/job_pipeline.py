import time
import logging
from typing import List, Set
from datetime import datetime

from .scrapers.khaleej_scraper import KhaleejScraper
from .processors.gemini_processor import GeminiProcessor
from .processors.location_enricher import LocationEnricher
from .processors.data_validator import DataValidator
from .publishers.html_generator import HTMLGenerator
from .publishers.blogger_publisher import BloggerPublisher
from .utils.database import JobDatabase
from .models.job_models import RawJobData, ProcessedJobData

class JobPipeline:
    """Main job processing pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.database = JobDatabase(config)
        self.scraper = KhaleejScraper(config.scraping)
        self.gemini_processor = GeminiProcessor(config.processing)
        self.location_enricher = LocationEnricher(config.processing)
        self.data_validator = DataValidator()
        self.html_generator = HTMLGenerator()
        self.blogger_publisher = BloggerPublisher(config.blogger)
    
    def run_pipeline(self):
        """Run the complete job processing pipeline"""
        self.logger.info("Starting job pipeline execution")
        start_time = time.time()
        
        try:
            # Step 1: Scrape new job URLs
            self.logger.info("Step 1: Scraping job URLs")
            new_job_count = self._scrape_new_jobs()
            
            if new_job_count == 0:
                self.logger.info("No new jobs found. Pipeline complete.")
                return
            
            # Step 2: Process new jobs
            self.logger.info("Step 2: Processing new jobs")
            processed_count = self._process_new_jobs()
            
            # Step 3: Publish to blog
            self.logger.info("Step 3: Publishing to blog")
            published_count = self._publish_new_jobs()
            
            execution_time = time.time() - start_time
            self.logger.info(
                f"Pipeline execution complete. "
                f"Scraped: {new_job_count}, Processed: {processed_count}, "
                f"Published: {published_count} jobs in {execution_time:.2f} seconds"
            )
            
        except Exception as e:
            self.logger.error(f"Error in pipeline execution: {str(e)}")
        finally:
            # Clean up resources
            self.blogger_publisher.close_driver()
    
    def _scrape_new_jobs(self) -> int:
        """Scrape new jobs and save to database"""
        try:
            # Get existing URLs to avoid duplicates
            existing_urls = self.database.get_existing_urls()
            
            # Scrape all job URLs
            all_urls = self.scraper.scrape_job_urls()
            
            # Filter out existing URLs
            new_urls = all_urls - existing_urls
            
            if not new_urls:
                self.logger.info("No new job URLs found")
                return 0
            
            self.logger.info(f"Found {len(new_urls)} new job URLs")
            
            # Scrape details for new jobs
            new_jobs = []
            for i, url in enumerate(new_urls, 1):
                self.logger.info(f"Scraping job {i}/{len(new_urls)}: {url}")
                job_data = self.scraper.scrape_job_details(url)
                if job_data:
                    new_jobs.append(job_data)
                
                # Add small delay to be respectful
                time.sleep(0.5)
            
            # Save to database
            added_count = self.database.add_raw_jobs(new_jobs)
            self.logger.info(f"Added {added_count} new jobs to database")
            
            return added_count
            
        except Exception as e:
            self.logger.error(f"Error in scraping phase: {str(e)}")
            return 0
    
    def _process_new_jobs(self) -> int:
        """Process unprocessed jobs through Gemini and validation"""
        try:
            # Get unprocessed jobs
            unprocessed_jobs = self.database.get_unprocessed_jobs()
            
            if not unprocessed_jobs:
                self.logger.info("No unprocessed jobs found")
                return 0
            
            self.logger.info(f"Processing {len(unprocessed_jobs)} jobs")
            
            processed_count = 0
            for i, raw_job in enumerate(unprocessed_jobs, 1):
                self.logger.info(f"Processing job {i}/{len(unprocessed_jobs)}: {raw_job.url}")
                
                try:
                    # Process through Gemini
                    gemini_data = self.gemini_processor.process_job(raw_job)
                    if not gemini_data:
                        self.logger.warning(f"Failed to process job with Gemini: {raw_job.url}")
                        continue
                    
                    # Enrich with location data
                    enriched_data = self.location_enricher.enrich_job_data(gemini_data)
                    
                    # Validate and normalize
                    processed_job = self.data_validator.validate_and_normalize(raw_job, enriched_data)
                    if not processed_job:
                        self.logger.warning(f"Failed to validate job: {raw_job.url}")
                        continue
                    
                    # Set job ID
                    processed_job.job_value_id = self.database.get_next_job_id()
                    
                    # Save to database
                    self.database.add_processed_job(processed_job)
                    processed_count += 1
                    
                    self.logger.info(f"Successfully processed job: {processed_job.title}")
                    
                    # Add delay between API calls
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing job {raw_job.url}: {str(e)}")
                    continue
            
            self.logger.info(f"Processed {processed_count} jobs successfully")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Error in processing phase: {str(e)}")
            return 0
    
    def _publish_new_jobs(self) -> int:
        """Publish processed jobs to Blogger"""
        try:
            # Get processed jobs that haven't been published
            processed_jobs_data = self.database.load_processed_jobs()
            
            # Filter for recent jobs (you might want to add a published flag to the data)
            # For now, we'll assume the most recent jobs need publishing
            jobs_to_publish = []
            for job_data in processed_jobs_data[:10]:  # Publish up to 10 most recent
                try:
                    # Convert dict back to ProcessedJobData
                    job = ProcessedJobData(**{k: v for k, v in job_data.items() if k in ProcessedJobData.__annotations__})
                    jobs_to_publish.append(job)
                except Exception as e:
                    self.logger.warning(f"Could not convert job data for publishing: {str(e)}")
            
            if not jobs_to_publish:
                self.logger.info("No jobs to publish")
                return 0
            
            published_count = 0
            for i, job in enumerate(jobs_to_publish, 1):
                self.logger.info(f"Publishing job {i}/{len(jobs_to_publish)}: {job.title}")
                
                try:
                    # Generate HTML
                    html_content = self.html_generator.generate_html(job)
                    if not html_content:
                        self.logger.warning(f"Failed to generate HTML for job: {job.title}")
                        continue
                    
                    # Publish to Blogger
                    success = self.blogger_publisher.create_blog_post(job, html_content)
                    if success:
                        published_count += 1
                        self.logger.info(f"Successfully published job: {job.title}")
                    else:
                        self.logger.warning(f"Failed to publish job: {job.title}")
                
                except Exception as e:
                    self.logger.error(f"Error publishing job {job.title}: {str(e)}")
                    continue
            
            self.logger.info(f"Published {published_count} jobs successfully")
            return published_count
            
        except Exception as e:
            self.logger.error(f"Error in publishing phase: {str(e)}")