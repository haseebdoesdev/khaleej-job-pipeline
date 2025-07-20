import logging
from datetime import datetime
from pathlib import Path

def setup_logging(logs_dir: Path) -> logging.Logger:
    """Setup logging configuration"""
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with current date
    log_filename = logs_dir / f"khaleej_jobs_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    return logging.getLogger('KhaleejJobPipeline')

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    return ' '.join(text.split())

def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."