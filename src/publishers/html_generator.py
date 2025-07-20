from jinja2 import Template
import logging
from typing import Dict, Any
from ..models.job_models import ProcessedJobData
from ..config.templates import HTML_TEMPLATE, HTML_REMOTE_TEMPLATE

class HTMLGenerator:
    """Generates HTML content for job postings"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_html(self, job_data: ProcessedJobData) -> str:
        """Generate HTML content for a job posting"""
        try:
            # Choose template based on job location type
            if job_data.job_location_type == "TELECOMMUTE":
                template_str = HTML_REMOTE_TEMPLATE
            else:
                template_str = HTML_TEMPLATE
            
            # Convert job data to dictionary for template rendering
            data_dict = job_data.to_dict()
            
            # Render template
            template = Template(template_str)
            html_content = template.render(data=data_dict)
            
            self.logger.info(f"Generated HTML for job: {job_data.title}")
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error generating HTML for job {job_data.title}: {str(e)}")
            return ""