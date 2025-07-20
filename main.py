import schedule
import time
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config.settings import AppConfig
    from src.utils.helpers import setup_logging
    from src.job_pipeline import JobPipeline
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory and all files are in place.")
    sys.exit(1)

def run_job_pipeline():
    """Run the job processing pipeline"""
    try:
        # Initialize configuration
        config = AppConfig()
        
        # Setup logging
        logger = setup_logging(config.logs_dir)
        logger.info("=" * 60)
        logger.info(f"Starting Khaleej Jobs Pipeline at {datetime.now()}")
        logger.info("=" * 60)
        
        # Initialize and run pipeline
        pipeline = JobPipeline(config)
        result = pipeline.run_pipeline()
        
        # Log results
        if result['status'] == 'success':
            logger.info("Pipeline execution completed successfully")
            if result.get('scraped', 0) > 0:
                logger.info(f"📊 Results: {result['scraped']} scraped, {result['processed']} processed, {result['published']} published")
        else:
            logger.error(f"Pipeline execution failed: {result.get('message', 'Unknown error')}")
        
        logger.info("=" * 60)
        
        return result
        
    except KeyboardInterrupt:
        logging.info("Pipeline execution interrupted by user")
        return {'status': 'interrupted', 'message': 'Interrupted by user'}
    except Exception as e:
        logging.error(f"Critical error in pipeline execution: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}

def main():
    """Main application entry point"""
    print("🚀 Khaleej Jobs Pipeline Starting...")
    print("=" * 60)
    
    try:
        # Initialize configuration
        config = AppConfig()
        
        # Setup logging
        logger = setup_logging(config.logs_dir)
        logger.info("Khaleej Jobs Pipeline Scheduler Starting...")
        logger.info(f"Schedule interval: {config.schedule_interval_minutes} minutes")
        
        # Verify configuration
        if not config.processing.gemini_api_key or config.processing.gemini_api_key == 'your_gemini_api_key_here':
            logger.error("GEMINI_API_KEY not properly configured. Please set the environment variable or update settings.py")
            print("❌ Error: GEMINI_API_KEY not properly configured")
            print("Please set the GEMINI_API_KEY environment variable or edit src/config/settings.py")
            return 1
        
        if not config.processing.google_places_api_key or config.processing.google_places_api_key == 'your_google_places_api_key_here':
            logger.warning("GOOGLE_PLACES_API_KEY not properly configured. Location enrichment will be limited.")
            print("⚠️  Warning: GOOGLE_PLACES_API_KEY not configured - location enrichment will be limited")
        
        # Schedule the pipeline to run every N minutes
        schedule.every(config.schedule_interval_minutes).minutes.do(run_job_pipeline)
        
        # Show startup information
        print(f"📊 Data directory: {config.data_dir}")
        print(f"📝 Logs directory: {config.logs_dir}")
        print(f"⏰ Schedule interval: {config.schedule_interval_minutes} minutes")
        print(f"🤖 Gemini API: {'✅ Configured' if config.processing.gemini_api_key else '❌ Not configured'}")
        print(f"🗺️  Places API: {'✅ Configured' if config.processing.google_places_api_key else '❌ Not configured'}")
        print("=" * 60)
        
        # Run once immediately
        logger.info("Running initial pipeline execution...")
        print("🔄 Running initial pipeline execution...")
        result = run_job_pipeline()
        
        if result['status'] == 'success':
            print("✅ Initial execution completed successfully")
            if result.get('scraped', 0) > 0:
                print(f"📊 Results: {result['scraped']} scraped, {result['processed']} processed, {result['published']} published")
            else:
                print("ℹ️  No new jobs found")
        else:
            print(f"❌ Initial execution failed: {result.get('message', 'Unknown error')}")
        
        # Log next scheduled run
        next_run = schedule.next_run()
        logger.info(f"Next scheduled run: {next_run}")
        print(f"⏰ Next scheduled run: {next_run}")
        print("=" * 60)
        print("📊 Pipeline is now running. Press Ctrl+C to stop.")
        print("=" * 60)
        
        # Main scheduler loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Pipeline scheduler stopped by user")
                print("\n👋 Pipeline scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
                print(f"⚠️  Error in scheduler: {str(e)}")
                print("🔄 Waiting 60 seconds before retrying...")
                time.sleep(60)  # Wait a minute before retrying
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        logging.error(f"Critical application error: {str(e)}", exc_info=True)
        return 1

def run_once():
    """Run the pipeline once without scheduling (useful for testing)"""
    print("🧪 Running pipeline once for testing...")
    result = run_job_pipeline()
    
    if result['status'] == 'success':
        print("✅ Single execution completed successfully")
        if result.get('scraped', 0) > 0:
            print(f"📊 Results: {result['scraped']} scraped, {result['processed']} processed, {result['published']} published")
        else:
            print("ℹ️  No new jobs found")
    else:
        print(f"❌ Single execution failed: {result.get('message', 'Unknown error')}")

def test_scraper():
    """Test only the scraping component"""
    print("🕷️  Testing scraper component...")
    
    try:
        from src.scrapers.khaleej_scraper import KhaleejScraper
        from src.utils.database import JobDatabase
        from src.config.settings import AppConfig
        
        config = AppConfig()
        logger = setup_logging(config.logs_dir)
        
        # Test scraper
        scraper = KhaleejScraper(config.scraping)
        database = JobDatabase(config)
        
        # Get existing URLs
        existing_urls = database.get_existing_urls()
        logger.info(f"Found {len(existing_urls)} existing URLs in database")
        print(f"📊 Found {len(existing_urls)} existing URLs in database")
        
        # Scrape URLs (limit for testing)
        print("🔍 Scraping job URLs...")
        all_urls = scraper.scrape_job_urls()
        new_urls = list(all_urls - existing_urls)[:3]  # Test with first 3 new URLs
        
        print(f"🆕 Found {len(new_urls)} new URLs to test")
        logger.info(f"Testing with {len(new_urls)} new URLs")
        
        if not new_urls:
            print("ℹ️  No new URLs found for testing")
            return
        
        # Test scraping details
        for i, url in enumerate(new_urls, 1):
            print(f"📄 Scraping job {i}/{len(new_urls)}: {url}")
            job_data = scraper.scrape_job_details(url)
            if job_data:
                print(f"✅ Successfully scraped: {job_data.url}")
                print(f"   Description length: {len(job_data.description)} characters")
                logger.info(f"Successfully scraped: {job_data.url}")
            else:
                print(f"❌ Failed to scrape: {url}")
                logger.warning(f"Failed to scrape: {url}")
        
        print("✅ Scraper test completed")
        
    except Exception as e:
        print(f"❌ Error testing scraper: {str(e)}")
        logging.error(f"Error testing scraper: {str(e)}", exc_info=True)

def show_stats():
    """Show database statistics"""
    print("📊 Database Statistics")
    print("=" * 30)
    
    try:
        from src.utils.database import JobDatabase
        from src.config.settings import AppConfig
        
        config = AppConfig()
        database = JobDatabase(config)
        
        # Raw jobs stats
        raw_jobs = database.load_raw_jobs()
        processed_jobs = database.load_processed_jobs()
        unprocessed_jobs = database.get_unprocessed_jobs()
        
        print(f"📄 Raw jobs in database: {len(raw_jobs)}")
        print(f"✅ Processed jobs: {len(processed_jobs)}")
        print(f"⏳ Pending processing: {len(unprocessed_jobs)}")
        
        if len(raw_jobs) > 0:
            processing_rate = len(processed_jobs) / len(raw_jobs) * 100
            print(f"📈 Processing rate: {processing_rate:.1f}%")
        
        if raw_jobs:
            latest_raw = raw_jobs[0].get('scraped_at', 'Unknown')
            print(f"🕐 Latest raw job: {latest_raw}")
        
        if processed_jobs:
            latest_processed = processed_jobs[0].get('processed_at', 'Unknown')
            print(f"🕐 Latest processed job: {latest_processed}")
        
        # Show some sample data
        if unprocessed_jobs:
            print(f"\n📋 Next {min(3, len(unprocessed_jobs))} jobs to process:")
            for i, job in enumerate(unprocessed_jobs[:3], 1):
                print(f"  {i}. {job.url}")
        
        if processed_jobs:
            print(f"\n📋 Recent {min(3, len(processed_jobs))} processed jobs:")
            for i, job_data in enumerate(processed_jobs[:3], 1):
                title = job_data.get('title', 'Unknown')
                org = job_data.get('short_name', 'Unknown')
                print(f"  {i}. {title} at {org}")
        
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")

def show_help():
    """Show help information"""
    print("Khaleej Jobs Pipeline")
    print("=" * 30)
    print("An automated job scraping and publishing pipeline for Khaleej Times")
    print("\nUsage:")
    print("  python main.py          - Run scheduled pipeline (default)")
    print("  python main.py once     - Run pipeline once for testing")
    print("  python main.py test     - Test scraper component only")
    print("  python main.py stats    - Show database statistics")
    print("  python main.py help     - Show this help message")
    print("\nConfiguration:")
    print("  - Set GEMINI_API_KEY environment variable")
    print("  - Set GOOGLE_PLACES_API_KEY environment variable")
    print("  - Edit src/config/settings.py for advanced configuration")
    print("\nFiles created:")
    print("  - data/jobs.json         - Raw scraped data")
    print("  - data/processed_jobs.json - Processed job data")
    print("  - logs/                  - Application logs")

if __name__ == "__main__":
    # Check command line arguments for special modes
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "once":
            run_once()
        elif command == "test":
            test_scraper()
        elif command == "stats":
            show_stats()
        elif command == "help":
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python main.py help' for available commands")
            sys.exit(1)
    else:
        # Run normal scheduled mode
        sys.exit(main())