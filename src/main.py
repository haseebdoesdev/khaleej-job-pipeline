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
    """
    Main job processing pipeline that orchestrates the entire workflow
    
    This class coordinates all the components of the pipeline:
    1. Scraping new jobs from Khaleej Times
    2. Processing job data through AI
    3. Publishing to Blogger
    """
    
    def __init__(self, config):
        """
        Initialize the job pipeline with all necessary components
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize all pipeline components
        self.logger.info("Initializing pipeline components...")
        
        try:
            self.database = JobDatabase(config)
            self.scraper = KhaleejScraper(config.scraping)
            self.gemini_processor = GeminiProcessor(config.processing)
            self.location_enricher = LocationEnricher(config.processing)
            self.data_validator = DataValidator()
            self.html_generator = HTMLGenerator()
            self.blogger_publisher = BloggerPublisher(config.blogger)
            
            self.logger.info("All pipeline components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pipeline components: {str(e)}")
            raise
    
    def run_pipeline(self):
        """
        Execute the complete job processing pipeline
        
        This method runs all three phases of the pipeline:
        1. Scraping phase - Get new job data
        2. Processing phase - Extract structured data with AI
        3. Publishing phase - Publish to Blogger
        """
        self.logger.info("Starting job pipeline execution")
        start_time = time.time()
        
        try:
            # Phase 1: Scraping
            self.logger.info("=" * 50)
            self.logger.info("PHASE 1: SCRAPING NEW JOBS")
            self.logger.info("=" * 50)
            
            new_job_count = self._scrape_new_jobs()
            
            if new_job_count == 0:
                self.logger.info("No new jobs found. Pipeline execution complete.")
                return {
                    'status': 'success',
                    'message': 'No new jobs to process',
                    'scraped': 0,
                    'processed': 0,
                    'published': 0,
                    'execution_time': time.time() - start_time
                }
            
            # Phase 2: Processing
            self.logger.info("=" * 50)
            self.logger.info("PHASE 2: PROCESSING NEW JOBS")
            self.logger.info("=" * 50)
            
            processed_count = self._process_new_jobs()
            
            # Phase 3: Publishing
            self.logger.info("=" * 50)
            self.logger.info("PHASE 3: PUBLISHING TO BLOGGER")
            self.logger.info("=" * 50)
            
            published_count = self._publish_new_jobs()
            
            # Summary
            execution_time = time.time() - start_time
            self.logger.info("=" * 50)
            self.logger.info("PIPELINE EXECUTION SUMMARY")
            self.logger.info("=" * 50)
            self.logger.info(
                f"✅ Pipeline execution complete!\n"
                f"   📥 Scraped: {new_job_count} new jobs\n"
                f"   🤖 Processed: {processed_count} jobs\n"
                f"   📤 Published: {published_count} jobs\n"
                f"   ⏱️  Total time: {execution_time:.2f} seconds"
            )
            
            return {
                'status': 'success',
                'scraped': new_job_count,
                'processed': processed_count,
                'published': published_count,
                'execution_time': execution_time
            }
            
        except Exception as e:
            self.logger.error(f"Critical error in pipeline execution: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'execution_time': time.time() - start_time
            }
        finally:
            # Clean up resources
            self._cleanup()
    
    def _scrape_new_jobs(self) -> int:
        """
        Scrape new jobs from Khaleej Times and save to database
        
        Returns:
            int: Number of new jobs added to database
        """
        try:
            # Get existing URLs to avoid duplicates
            existing_urls = self.database.get_existing_urls()
            self.logger.info(f"Found {len(existing_urls)} existing jobs in database")
            
            # Scrape all job URLs from the website
            self.logger.info("Scraping job URLs from Khaleej Times...")
            all_urls = self.scraper.scrape_job_urls()
            
            # Filter out existing URLs to get only new ones
            new_urls = all_urls - existing_urls
            
            if not new_urls:
                self.logger.info("No new job URLs found")
                return 0
            
            self.logger.info(f"Found {len(new_urls)} new job URLs to process")
            
            # Scrape detailed information for each new job
            new_jobs = []
            successful_scrapes = 0
            failed_scrapes = 0
            
            for i, url in enumerate(new_urls, 1):
                self.logger.info(f"Scraping job details {i}/{len(new_urls)}: {url}")
                
                try:
                    job_data = self.scraper.scrape_job_details(url)
                    if job_data:
                        new_jobs.append(job_data)
                        successful_scrapes += 1
                        self.logger.debug(f"Successfully scraped: {url}")
                    else:
                        failed_scrapes += 1
                        self.logger.warning(f"Failed to scrape details for: {url}")
                
                except Exception as e:
                    failed_scrapes += 1
                    self.logger.error(f"Error scraping {url}: {str(e)}")
                
                # Add small delay to be respectful to the server
                time.sleep(0.5)
            
            # Log scraping statistics
            self.scraper.log_scraping_stats(len(new_urls), successful_scrapes, failed_scrapes)
            
            # Save new jobs to database
            if new_jobs:
                added_count = self.database.add_raw_jobs(new_jobs)
                self.logger.info(f"Added {added_count} new jobs to database")
                return added_count
            else:
                self.logger.warning("No jobs were successfully scraped")
                return 0
            
        except Exception as e:
            self.logger.error(f"Error in scraping phase: {str(e)}", exc_info=True)
            return 0
    
    def _process_new_jobs(self) -> int:
        """
        Process unprocessed jobs through AI and validation pipeline
        
        Returns:
            int: Number of jobs successfully processed
        """
        try:
            # Get jobs that haven't been processed yet
            unprocessed_jobs = self.database.get_unprocessed_jobs()
            
            if not unprocessed_jobs:
                self.logger.info("No unprocessed jobs found")
                return 0
            
            self.logger.info(f"Processing {len(unprocessed_jobs)} unprocessed jobs")
            
            processed_count = 0
            
            for i, raw_job in enumerate(unprocessed_jobs, 1):
                self.logger.info(f"Processing job {i}/{len(unprocessed_jobs)}: {raw_job.url}")
                
                try:
                    # Step 1: Process through Gemini AI
                    self.logger.debug("Sending to Gemini AI for data extraction...")
                    gemini_data = self.gemini_processor.process_job(raw_job)
                    
                    if not gemini_data:
                        self.logger.warning(f"Gemini AI failed to process job: {raw_job.url}")
                        continue
                    
                    self.logger.debug("Gemini AI processing successful")
                    
                    # Step 2: Enrich with location data
                    self.logger.debug("Enriching with location data...")
                    enriched_data = self.location_enricher.enrich_job_data(gemini_data)
                    
                    # Step 3: Validate and normalize data
                    self.logger.debug("Validating and normalizing data...")
                    processed_job = self.data_validator.validate_and_normalize(raw_job, enriched_data)
                    
                    if not processed_job:
                        self.logger.warning(f"Data validation failed for job: {raw_job.url}")
                        continue
                    
                    # Step 4: Assign unique job ID
                    processed_job.job_value_id = self.database.get_next_job_id()
                    
                    # Step 5: Save to database
                    self.database.add_processed_job(processed_job)
                    processed_count += 1
                    
                    self.logger.info(
                        f"✅ Successfully processed: {processed_job.title} "
                        f"at {processed_job.short_name} (ID: {processed_job.job_value_id})"
                    )
                    
                    # Add delay between API calls to respect rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing job {raw_job.url}: {str(e)}", exc_info=True)
                    continue
            
            self.logger.info(f"Processing phase complete: {processed_count}/{len(unprocessed_jobs)} jobs processed successfully")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Error in processing phase: {str(e)}", exc_info=True)
            return 0
    
    def _publish_new_jobs(self) -> int:
        """
        Publish processed jobs to Blogger
        
        Returns:
            int: Number of jobs successfully published
        """
        try:
            # Get recently processed jobs that need publishing
            processed_jobs_data = self.database.load_processed_jobs()
            
            # For this implementation, we'll publish the most recent jobs
            # In a production system, you might want to add a "published" flag
            jobs_to_publish = []
            
            # Get up to 10 most recent processed jobs for publishing
            for job_data in processed_jobs_data[:10]:
                try:
                    # Convert dict back to ProcessedJobData object
                    job_dict = {k: v for k, v in job_data.items() 
                              if k in ProcessedJobData.__annotations__}
                    job = ProcessedJobData(**job_dict)
                    jobs_to_publish.append(job)
                except Exception as e:
                    self.logger.warning(f"Could not convert job data for publishing: {str(e)}")
            
            if not jobs_to_publish:
                self.logger.info("No jobs ready for publishing")
                return 0
            
            self.logger.info(f"Publishing {len(jobs_to_publish)} jobs to Blogger")
            
            published_count = 0
            
            for i, job in enumerate(jobs_to_publish, 1):
                self.logger.info(f"Publishing job {i}/{len(jobs_to_publish)}: {job.title}")
                
                try:
                    # Step 1: Generate HTML content
                    self.logger.debug("Generating HTML content...")
                    html_content = self.html_generator.generate_html(job)
                    
                    if not html_content:
                        self.logger.warning(f"Failed to generate HTML for job: {job.title}")
                        continue
                    
                    self.logger.debug("HTML generation successful")
                    
                    # Step 2: Publish to Blogger
                    self.logger.debug("Publishing to Blogger...")
                    success = self.blogger_publisher.create_blog_post(job, html_content)
                    
                    if success:
                        published_count += 1
                        self.logger.info(f"✅ Successfully published: {job.title}")
                    else:
                        self.logger.warning(f"❌ Failed to publish: {job.title}")
                    
                    # Add delay between publications to avoid overwhelming Blogger
                    time.sleep(5)
                    
                except Exception as e:
                    self.logger.error(f"Error publishing job {job.title}: {str(e)}", exc_info=True)
                    continue
            
            self.logger.info(f"Publishing phase complete: {published_count}/{len(jobs_to_publish)} jobs published successfully")
            return published_count
            
        except Exception as e:
            self.logger.error(f"Error in publishing phase: {str(e)}", exc_info=True)
            return 0
    
    def _cleanup(self):
        """Clean up resources after pipeline execution"""
        try:
            # Close browser driver if it was opened
            if hasattr(self.blogger_publisher, 'driver') and self.blogger_publisher.driver:
                self.blogger_publisher.close_driver()
                self.logger.debug("Closed browser driver")
            
            # Any other cleanup tasks can be added here
            
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {str(e)}")
    
    def get_pipeline_status(self) -> dict:
        """
        Get current pipeline status and statistics
        
        Returns:
            dict: Pipeline status information
        """
        try:
            raw_jobs = self.database.load_raw_jobs()
            processed_jobs = self.database.load_processed_jobs()
            unprocessed_jobs = self.database.get_unprocessed_jobs()
            
            return {
                'total_raw_jobs': len(raw_jobs),
                'total_processed_jobs': len(processed_jobs),
                'pending_processing': len(unprocessed_jobs),
                'processing_rate': len(processed_jobs) / max(len(raw_jobs), 1) * 100,
                'last_scraped': raw_jobs[0].get('scraped_at') if raw_jobs else None,
                'last_processed': processed_jobs[0].get('processed_at') if processed_jobs else None,
            }
            
        except Exception as e:
            self.logger.error(f"Error getting pipeline status: {str(e)}")
            return {'error': str(e)}
