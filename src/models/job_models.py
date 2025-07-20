from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class RawJobData:
    """Raw job data from scraping"""
    url: str
    scraped_at: str
    description: str
    industry: Optional[str] = None
    career: Optional[str] = None
    job_location: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None
    job_type: Optional[str] = None
    gender: Optional[str] = None
    contact_no: Optional[str] = None
    email: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    listed: Optional[str] = None
    expires: Optional[str] = None

@dataclass
class ProcessedJobData:
    """Processed job data after Gemini processing"""
    # Original fields
    url: str
    title: str
    short_name: str
    long_name: str
    short_name_for_url: str
    apply_url: str
    description: str
    description_html_body: str
    description_html_schema: str
    
    # Job details
    grade: Optional[str] = None
    level: Optional[str] = None
    cities_countries: str = ""
    employment_type: str = "FULL_TIME"
    app_type: str = "Full-time"
    logo: Optional[str] = None
    posted_date: Optional[str] = None
    date_posted: str = ""
    deadline: Optional[str] = None
    valid_through: str = ""
    
    # Location
    job_city: Optional[str] = None
    job_country: str = "UAE"
    address_country_iso: str = "AE"
    street_address: Optional[str] = None
    address_locality: Optional[str] = None
    address_region: Optional[str] = None
    postal_code: str = "00000"
    
    # Salary
    currency: str = "AED"
    min_salary: int = 0
    max_salary: int = 0
    salary_unit_text: str = "MONTH"
    
    # Categories and skills
    categories: str = ""
    recruitment_place: Optional[str] = None
    search_description: str = ""
    job_industry: str = ""
    job_summary: str = ""
    occupational_category: Optional[str] = None
    
    # JSON fields
    responsibilities: str = "[]"
    skills: str = "[]"
    qualifications: str = "[]"
    keywords: str = ""
    job_benefits: str = "[]"
    
    # Requirements
    education_requirements: Optional[str] = None
    educational_credential_category: str = "bachelor degree"
    experience_requirements: Optional[str] = None
    months_of_experience: int = 24
    job_location_type: str = "ON-SITE"
    
    # Organization
    org_headquarter: Optional[str] = None
    org_founded: Optional[int] = None
    org_type: Optional[str] = None
    org_web: Optional[str] = None
    about_org: str = ""
    
    # Metadata
    schema: Optional[str] = None
    job_value_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'url': self.url,
            'title': self.title,
            'shortName': self.short_name,
            'longName': self.long_name,
            'shortNameForUrl': self.short_name_for_url,
            'applyURL': self.apply_url,
            'description': self.description,
            'descriptionHtml_body': self.description_html_body,
            'descriptionHtml_Schema': self.description_html_schema,
            'grade': self.grade,
            'Level': self.level,
            'citiesCountries': self.cities_countries,
            'employmentType': self.employment_type,
            'appType': self.app_type,
            'logo': self.logo,
            'postedDate': self.posted_date,
            'datePosted': self.date_posted,
            'deadline': self.deadline,
            'validThrough': self.valid_through,
            'jobCity': self.job_city,
            'jobCountry': self.job_country,
            'addressCountryISO': self.address_country_iso,
            'currency': self.currency,
            'minSalary': self.min_salary,
            'maxSalary': self.max_salary,
            'salaryunittext': self.salary_unit_text,
            'categories': self.categories,
            'RecruitmentPlace': self.recruitment_place,
            'search_description': self.search_description,
            'job_industry': self.job_industry,
            'job_summary': self.job_summary,
            'occupationalCategory': self.occupational_category,
            'responsibilities': json.loads(self.responsibilities) if self.responsibilities else [],
            'skills': json.loads(self.skills) if self.skills else [],
            'qualifications': json.loads(self.qualifications) if self.qualifications else [],
            'educationRequirements': self.education_requirements,
            'EducationalOccupationalCredential_Category': self.educational_credential_category,
            'experienceRequirements': self.experience_requirements,
            'MonthsOfExperience': self.months_of_experience,
            'jobLocationType': self.job_location_type,
            'orgHeadquarter': self.org_headquarter,
            'orgFounded': self.org_founded,
            'orgType': self.org_type,
            'orgWeb': self.org_web,
            'streetAddress': self.street_address,
            'addressLocality': self.address_locality,
            'addressRegion': self.address_region,
            'postalCode': self.postal_code,
            'aboutOrg': self.about_org,
            'keywords': self.keywords,
            'jobBenefits': json.loads(self.job_benefits) if self.job_benefits else [],
            'jobValue_id': self.job_value_id
        }