import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import logging
from ..models.job_models import ProcessedJobData

class DataValidator:
    """Validates and normalizes processed job data"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.employment_to_app_type = {
            'FULL_TIME': 'Full-time',
            'PART_TIME': 'Part-time',
            'CONTRACTOR': 'Consultancy',
            'TEMPORARY': 'Temporary',
            'INTERN': 'Internship',
            'VOLUNTEER': 'Volunteer',
            'OTHER': 'Other',
            'PER_DIEM': 'Per-diem'
        }
        
        self.default_benefits = [
            "Competitive Salary", "Health Insurance", "Pension/Retirement Plan",
            "Life Insurance", "Paid Time Off (PTO)", "Parental Leave", "Professional Development"
        ]
    
    def validate_and_normalize(self, raw_job_data, gemini_data: Dict[str, Any]) -> Optional[ProcessedJobData]:
        """Validate and normalize job data"""
        try:
            # Basic validation
            if not gemini_data.get('jobTitle') or not gemini_data.get('orgName'):
                self.logger.warning(f"Missing essential job data for {raw_job_data.url}")
                return None
            
            # Normalize employment type and app type
            employment_type = gemini_data.get('employmentType', 'FULL_TIME')
            app_type = self.employment_to_app_type.get(employment_type, 'Full-time')
            
            # Handle dates
            date_posted = self._normalize_date_posted(raw_job_data.scraped_at)
            deadline, valid_through = self._calculate_deadline(gemini_data.get('deadLine'), date_posted)
            
            # Handle salary
            min_salary, max_salary = self._normalize_salary(gemini_data)
            
            # Handle location
            cities_countries = self._format_cities_countries(
                gemini_data.get('jobCity'), 
                gemini_data.get('jobCountry', 'United Arab Emirates')
            )
            
            # Handle JSON fields
            responsibilities = self._normalize_json_field(gemini_data.get('responsibilities', []))
            skills = self._normalize_json_field(gemini_data.get('skills', []))
            qualifications = self._normalize_json_field(gemini_data.get('qualifications', []))
            job_benefits = self._normalize_json_field(gemini_data.get('jobBenefits', []))
            
            # Use default benefits if none provided
            if not job_benefits or job_benefits == '[]':
                job_benefits = json.dumps(self.default_benefits, ensure_ascii=False, indent=4)
            
            # Handle keywords
            keywords = ', '.join(gemini_data.get('keywords', []))
            
            # Handle categories
            categories = ', '.join(gemini_data.get('category', []))
            
            # Generate logo URL
            logo = None
            if gemini_data.get('orgWeb'):
                logo = f"https://logo.clearbit.com/{gemini_data['orgWeb']}"
            
            # Create ProcessedJobData instance
            processed_job = ProcessedJobData(
                url=raw_job_data.url,
                title=gemini_data['jobTitle'],
                short_name=gemini_data.get('shortName', gemini_data['orgName']),
                long_name=gemini_data['orgName'],
                short_name_for_url=gemini_data.get('shortName', gemini_data['orgName']).lower().replace(' ', '-'),
                apply_url=raw_job_data.url,  # Using original URL as apply URL
                description=raw_job_data.description,
                description_html_body=f"<p>{raw_job_data.description}</p>",
                description_html_schema=raw_job_data.description.replace('"', '\\"'),
                grade=gemini_data.get('jobGrade'),
                level=gemini_data.get('jobLevel'),
                cities_countries=cities_countries,
                employment_type=employment_type,
                app_type=app_type,
                logo=logo,
                posted_date=gemini_data.get('postedDate'),
                date_posted=date_posted,
                deadline=deadline,
                valid_through=valid_through,
                job_city=gemini_data.get('jobCity'),
                job_country=gemini_data.get('jobCountry', 'United Arab Emirates'),
                address_country_iso=gemini_data.get('addressCountryISO', 'AE'),
                street_address=gemini_data.get('streetAddress'),
                address_locality=gemini_data.get('addressLocality'),
                address_region=gemini_data.get('addressRegion'),
                postal_code=gemini_data.get('postalCode', '00000'),
                currency=gemini_data.get('currency', 'AED'),
                min_salary=min_salary,
                max_salary=max_salary,
                salary_unit_text=gemini_data.get('salaryunittext', 'MONTH'),
                categories=categories,
                recruitment_place=gemini_data.get('RecruitmentPlace'),
                search_description=gemini_data.get('meta_description', ''),
                job_industry=gemini_data.get('industry', ''),
                job_summary=gemini_data.get('jobSummary', ''),
                occupational_category=gemini_data.get('occupationalCategory'),
                responsibilities=responsibilities,
                skills=skills,
                qualifications=qualifications,
                keywords=keywords,
                job_benefits=job_benefits,
                education_requirements=gemini_data.get('educationRequirements'),
                educational_credential_category=gemini_data.get('EducationalOccupationalCredential_Category', 'bachelor degree'),
                experience_requirements=gemini_data.get('experienceRequirements'),
                months_of_experience=gemini_data.get('MonthsOfExperience', 24),
                job_location_type=gemini_data.get('jobLocationType', 'ON-SITE'),
                org_headquarter=gemini_data.get('orgHeadquarter'),
                org_founded=gemini_data.get('orgFounded'),
                org_type=gemini_data.get('orgType'),
                org_web=gemini_data.get('orgWeb'),
                about_org=gemini_data.get('aboutOrg', ''),
                schema=None,  # Will be set later if needed
                job_value_id=None  # Will be set later
            )
            
            return processed_job
            
        except Exception as e:
            self.logger.error(f"Error validating job data for {raw_job_data.url}: {str(e)}")
            return None
    
    def _normalize_date_posted(self, scraped_at: str) -> str:
        """Normalize date posted format"""
        try:
            dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S") + '+00:00'
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '+00:00'
    
    def _calculate_deadline(self, deadline_str: Optional[str], date_posted: str) -> tuple:
        """Calculate deadline and valid_through dates"""
        try:
            if deadline_str:
                # Parse deadline and create valid_through
                deadline_dt = datetime.strptime(deadline_str, "%d %b %Y")
                valid_through = deadline_dt.replace(
                    hour=23, minute=59, second=59, tzinfo=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
                return deadline_str, valid_through
            else:
                # Default to 30 days from posting
                posted_dt = datetime.fromisoformat(date_posted.replace('+00:00', ''))
                deadline_dt = posted_dt + timedelta(days=30)
                deadline = deadline_dt.strftime("%d %b %Y")
                valid_through = deadline_dt.replace(
                    hour=23, minute=59, second=59, tzinfo=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
                return deadline, valid_through
        except:
            # Fallback
            fallback_dt = datetime.now() + timedelta(days=30)
            deadline = fallback_dt.strftime("%d %b %Y")
            valid_through = fallback_dt.replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            return deadline, valid_through
    
    def _normalize_salary(self, gemini_data: Dict[str, Any]) -> tuple:
        """Normalize salary values"""
        min_salary = gemini_data.get('minSalary', 0)
        max_salary = gemini_data.get('maxSalary', 0)
        
        # Ensure numeric values
        try:
            min_salary = int(min_salary) if min_salary is not None else 0
        except:
            min_salary = 0
        
        try:
            max_salary = int(max_salary) if max_salary is not None else min_salary
        except:
            max_salary = min_salary
        
        return min_salary, max_salary
    
    def _format_cities_countries(self, city: Optional[str], country: str) -> str:
        """Format cities and countries string"""
        if city and country:
            return f"{city} ({country})"
        elif country:
            return country
        else:
            return ""
    
    def _normalize_json_field(self, field_data) -> str:
        """Normalize JSON field to string"""
        if isinstance(field_data, list):
            return json.dumps(field_data, ensure_ascii=False, indent=4)
        elif isinstance(field_data, str):
            try:
                # Try to parse and re-serialize for consistency
                parsed = json.loads(field_data)
                return json.dumps(parsed, ensure_ascii=False, indent=4)
            except:
                # If not valid JSON, wrap in list
                return json.dumps([field_data], ensure_ascii=False, indent=4)
        else:
            return json.dumps([], ensure_ascii=False, indent=4)
            