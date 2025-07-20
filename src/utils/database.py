import json
from pathlib import Path
from typing import List, Set, Dict, Any, Optional
import logging
from datetime import datetime
from ..models.job_models import RawJobData, ProcessedJobData

class JobDatabase:
    """Simple JSON-based database for job data"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure data directory exists
        self.config.data_dir.mkdir(exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize database files if they don't exist"""
        for file_path in [self.config.jobs_file, self.config.processed_jobs_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def load_raw_jobs(self) -> List[Dict[str, Any]]:
        """Load raw job data from file"""
        try:
            with open(self.config.jobs_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading raw jobs: {str(e)}")
            return []
    
    def save_raw_jobs(self, jobs: List[Dict[str, Any]]):
        """Save raw job data to file"""
        try:
            with open(self.config.jobs_file, 'w') as f:
                json.dump(jobs, f, indent=2)
            self.logger.info(f"Saved {len(jobs)} raw jobs to database")
        except Exception as e:
            self.logger.error(f"Error saving raw jobs: {str(e)}")
    
    def load_processed_jobs(self) -> List[Dict[str, Any]]:
        """Load processed job data from file"""
        try:
            with open(self.config.processed_jobs_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading processed jobs: {str(e)}")
            return []
    
    def save_processed_jobs(self, jobs: List[Dict[str, Any]]):
        """Save processed job data to file"""
        try:
            with open(self.config.processed_jobs_file, 'w') as f:
                json.dump(jobs, f, indent=2)
            self.logger.info(f"Saved {len(jobs)} processed jobs to database")
        except Exception as e:
            self.logger.error(f"Error saving processed jobs: {str(e)}")
    
    def get_existing_urls(self) -> Set[str]:
        """Get set of existing job URLs"""
        raw_jobs = self.load_raw_jobs()
        return {job.get('url', '') for job in raw_jobs if job.get('url')}
    
    def get_processed_urls(self) -> Set[str]:
        """Get set of processed job URLs"""
        processed_jobs = self.load_processed_jobs()
        return {job.get('url', '') for job in processed_jobs if job.get('url')}
    
    def add_raw_jobs(self, new_jobs: List[RawJobData]):
        """Add new raw jobs to database"""
        existing_jobs = self.load_raw_jobs()
        existing_urls = {job.get('url', '') for job in existing_jobs}
        
        # Convert RawJobData to dict and filter out existing URLs
        new_job_dicts = []
        for job in new_jobs:
            job_dict = job.__dict__
            if job_dict['url'] not in existing_urls:
                new_job_dicts.append(job_dict)
        
        # Add new jobs to the beginning of the list
        all_jobs = new_job_dicts + existing_jobs
        self.save_raw_jobs(all_jobs)
        
        return len(new_job_dicts)
    
    def add_processed_job(self, job: ProcessedJobData):
        """Add a processed job to database"""
        processed_jobs = self.load_processed_jobs()
        
        # Convert to dict
        job_dict = job.__dict__.copy()
        
        # Add timestamp
        job_dict['processed_at'] = datetime.now().isoformat()
        
        # Add to beginning of list
        processed_jobs.insert(0, job_dict)
        
        self.save_processed_jobs(processed_jobs)
    
    def get_next_job_id(self) -> int:
        """Get next available job ID"""
        processed_jobs = self.load_processed_jobs()
        if not processed_jobs:
            return 1
        
        # Find the highest job_value_id
        max_id = 0
        for job in processed_jobs:
            job_id = job.get('job_value_id', 0)
            if job_id and job_id > max_id:
                max_id = job_id
        
        return max_id + 1
    
    def get_unprocessed_jobs(self) -> List[RawJobData]:
        """Get raw jobs that haven't been processed yet"""
        raw_jobs = self.load_raw_jobs()
        processed_urls = self.get_processed_urls()
        
        unprocessed = []
        for job_dict in raw_jobs:
            if job_dict.get('url', '') not in processed_urls:
                try:
                    unprocessed.append(RawJobData(**job_dict))
                except Exception as e:
                    self.logger.warning(f"Could not convert job data: {str(e)}")
        
        return unprocessed