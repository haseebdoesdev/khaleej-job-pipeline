# Khaleej Jobs Pipeline

An automated job scraping and publishing pipeline that scrapes job postings from Khaleej Times, processes them using AI, and publishes them to a Blogger site.

## 🚀 Features

- **Incremental Scraping**: Scrapes only new job postings every 30 minutes
- **AI Processing**: Uses Google's Gemini AI to extract structured data from job descriptions
- **Location Enrichment**: Enhances job data with Google Places API
- **Automated Publishing**: Publishes formatted job posts to Blogger using Selenium automation
- **Rich Schema**: Generates SEO-optimized HTML with Google Rich Results schema
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Modular Architecture**: Clean, maintainable code structure

## 📁 Project Structure

```
khaleej_job_pipeline/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Configuration management
│   │   └── templates.py         # HTML templates
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py      # Base scraper class
│   │   └── khaleej_scraper.py   # Khaleej Times scraper
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── gemini_processor.py  # AI data extraction
│   │   ├── location_enricher.py # Google Places integration
│   │   └── data_validator.py    # Data validation and normalization
│   ├── publishers/
│   │   ├── __init__.py
│   │   ├── html_generator.py    # HTML generation
│   │   └── blogger_publisher.py # Blogger automation
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py          # JSON database operations
│   │   └── helpers.py           # Utility functions
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_models.py        # Data models
│   └── job_pipeline.py          # Main pipeline orchestrator
├── data/
│   ├── jobs.json               # Raw scraped data
│   └── processed_jobs.json     # Processed job data
├── logs/                       # Application logs
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── .env.example               # Environment variables example
├── .gitignore                 # Git ignore file
└── README.md                   # This file
```

## 🛠️ Setup

### Prerequisites

1. **Python 3.8+**
2. **Chrome Browser** (for Selenium automation)
3. **API Keys**:
   - Google Gemini AI API key
   - Google Places API key
4. **Selenium Grid** (for browser automation)

### Installation

1. **Clone the repository:**
```bash
git clone 
cd khaleej_job_pipeline
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env file with your API keys
```

5. **Configure Selenium Grid:**
   - Start Selenium Grid with your browser automation setup
   - Update browser ID in `src/config/settings.py` if needed

### Environment Variables

Create a `.env` file with the following:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
SELENIUM_URL=http://127.0.0.1:54345
BROWSER_ID=3bc7d8d47e1f4b31a38416e8d00083e0
```

## 🚀 Usage

### Running the Pipeline

**Start the scheduled pipeline:**
```bash
python main.py
```

**Run once for testing:**
```bash
python main.py once
```

**Test only the scraper:**
```bash
python main.py test
```

**Show database statistics:**
```bash
python main.py stats
```

**Show help:**
```bash
python main.py help
```

## 🔄 Pipeline Workflow

1. **Scraping Phase**:
   - Scrapes job URLs from Khaleej Times job board
   - Extracts job details and metadata
   - Filters out already processed jobs
   - Stores raw data in JSON database

2. **Processing Phase**:
   - Sends job descriptions to Gemini AI for structured extraction
   - Enriches location data using Google Places API
   - Validates and normalizes extracted data
   - Assigns unique job IDs

3. **Publishing Phase**:
   - Generates SEO-optimized HTML with rich schema
   - Automates Blogger post creation using Selenium
   - Sets appropriate labels, descriptions, and metadata
   - Publishes with custom permalinks

## 📊 Data Models

### RawJobData
Represents scraped job data before AI processing:
- URL, description, industry, location
- Salary, experience, job type
- Contact information, posting dates

### ProcessedJobData
Represents structured job data after AI extraction and validation:
- Structured job details (title, organization, requirements)
- Normalized location and salary data
- SEO metadata and rich schema data
- Publishing-ready format

## 🛡️ Error Handling

- **Network Errors**: Automatic retries with exponential backoff
- **API Errors**: Graceful degradation and fallback values
- **Validation Errors**: Comprehensive data validation and sanitization
- **Browser Automation**: Robust element selection and error recovery

## 📝 Logging

Comprehensive logging to both console and files:
- Daily log rotation in `logs/` directory
- Structured log messages with timestamps
- Error tracking and debugging information
- Performance metrics and execution times

## ⚙️ Configuration

### Scraping Configuration
- Base URL and selectors for Khaleej Times
- Retry logic and timeout settings
- Concurrent processing limits

### Processing Configuration
- Gemini AI model settings
- Google Places API configuration
- Data validation rules

### Publishing Configuration
- Blogger automation settings
- HTML template customization
- SEO and schema configuration

## 🔧 Customization

### Adding New Scrapers

1. Inherit from `BaseScraper`
2. Implement required methods (`scrape_job_urls`, `scrape_job_details`)
3. Add to pipeline configuration

```python
from src.scrapers.base_scraper import BaseScraper

class NewSiteScraper(BaseScraper):
    def scrape_job_urls(self) -> Set[str]:
        # Implementation here
        pass
    
    def scrape_job_details(self, url: str) -> Optional[dict]:
        # Implementation here
        pass
```

### Modifying AI Prompts

Edit prompt templates in `src/processors/gemini_processor.py`:

```python
def _get_extraction_prompt(self, job_data: RawJobData) -> str:
    # Customize the prompt here
    pass
```

### Customizing HTML Templates

Modify templates in `src/config/templates.py`:
- `HTML_TEMPLATE` for regular jobs
- `HTML_REMOTE_TEMPLATE` for remote jobs

## 📈 Monitoring

Monitor pipeline execution through:
- **Log files** in `logs/` directory
- **Console output** during execution
- **JSON database files** for data inspection
- **Statistics command** for quick overview

## 🐛 Troubleshooting

### Common Issues

1. **Browser Automation Failures**:
   ```bash
   # Check Selenium Grid status
   curl http://127.0.0.1:54345/status
   
   # Verify browser configuration
   python main.py test
   ```

2. **API Rate Limits**:
   - Increase delays between API calls in configuration
   - Check API quotas and limits in Google Cloud Console

3. **Data Validation Errors**:
   - Review Gemini AI responses in logs
   - Update validation rules in `data_validator.py`
   - Check input data quality

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 🧪 Testing

**Run all components:**
```bash
python main.py test
```

**Test individual components:**
```python
# Test scraper only
from src.scrapers.khaleej_scraper import KhaleejScraper
# ... test code

# Test AI processing
from src.processors.gemini_processor import GeminiProcessor
# ... test code
```

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Check the logs for detailed error information
- Review the troubleshooting section above
- Submit issues through the repository issue tracker
- Check configuration and API key setup

## 🗺️ Roadmap

- [ ] Add support for more job sites
- [ ] Implement web dashboard for monitoring
- [ ] Add email notifications
- [ ] Support for multiple languages
- [ ] Advanced filtering and categorization
- [ ] API endpoint for external integrations