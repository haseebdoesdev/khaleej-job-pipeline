import google.generativeai as genai
import json
import logging
from typing import Optional, Dict, Any
from ..models.job_models import RawJobData

class GeminiProcessor:
    """Processor for extracting structured data using Gemini AI"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        genai.configure(api_key=config.gemini_api_key)
        
        self.model = genai.GenerativeModel(
            config.model_name,
            generation_config={"response_mime_type": "application/json"},
            safety_settings=[
                {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
    
    def _get_extraction_prompt(self, job_data: RawJobData) -> str:
        """Generate extraction prompt for Gemini"""
        
        job_info = f"""
        Job URL: {job_data.url}
        Job Description: {job_data.description}
        Industry: {job_data.industry or 'Not specified'}
        Career Level: {job_data.career or 'Not specified'}
        Job Location: {job_data.job_location or 'Not specified'}
        Salary: {job_data.salary or 'Not specified'}
        Experience: {job_data.experience or 'Not specified'}
        Job Type: {job_data.job_type or 'Not specified'}
        Gender: {job_data.gender or 'Not specified'}
        Contact: {job_data.contact_no or 'Not specified'}
        Email: {job_data.email or 'Not specified'}
        Street: {job_data.street or 'Not specified'}
        City: {job_data.city or 'Not specified'}
        Listed: {job_data.listed or 'Not specified'}
        Expires: {job_data.expires or 'Not specified'}
        """
        
        prompt = f"""{job_info}

Your task is to extract the following information from the given job posting and return it in a JSON format:

jobTitle (main title of the job)
orgName (Name of the organization offering the job)
shortName (abbreviation of the Organization name, if available. If it cannot be found, then return the organization name as it is)
RecruitmentPlace (recruitment place)
responsibilities (responsibilities - list of strings)
skills (skills required for the role - list of strings)
qualifications (qualification required for the job - list of strings)
educationRequirements (educational qualification required for the job)
experienceRequirements (professional experience required for the job)
jobLocationType (job location type: ON-SITE, REMOTE, or TELECOMMUTE)
orgHeadquarter (organization headquarter)
orgFounded (organization founded in year)
orgType (organization type)
orgWeb (web domain of the organization)
streetAddress (Address if available)
addressLocality (Area name or city name)
addressRegion (Region of address if available)
postalCode (Postal code if available)
deadLine (Dead line date. Format: DD MMM YYYY.)
postedDate (job posted date. Format: DD MMM YYYY)
MonthsOfExperience (minimum number of months of total experience required)
occupationalCategory (occupational category refer to ISCO-08, just the category name without the code)
industry (category of business and organization)
meta_description (SEO optimized clear and concise, 120-150 characters)
addressCountryISO (ISO country code - for UAE jobs use 'AE')
jobLevel (give job role i.e Intern, General Support, Entry Professional, Mid-level Professional, Director and Top Executive, Chief and Senior Professional)
category (By analyzing the given job posting, Select category(ies) that best represent the job. You can select two categories at most - list of strings)
jobCity (job city)
jobCountry (job country - for UAE jobs use 'United Arab Emirates')
jobSummary (job Summary. Maximum 200 characters long.)
jobGrade (job grade if explicitly mentioned)
jobBenefits (employee benefits provided by the job - list of strings)
currency (currency in which the salary would be paid - for UAE jobs use 'AED')
minSalary (minimum salary - extract numeric value only)
maxSalary (maximum salary - extract numeric value only)
salaryunittext (If the annual salary amount is given, return YEAR. If monthly then return MONTH.)
EducationalOccupationalCredential_Category (The category or type of educational credential required. Choose from ['high school','associate degree','bachelor degree','postgraduate degree','professional certificate'])
employmentType (type of employment. Choose from FULL_TIME, PART_TIME, CONTRACTOR, TEMPORARY, INTERN, VOLUNTEER, OTHER, PER_DIEM)
aboutOrg (give short description of the organization mentioned in the text in clear and concise way)
keywords (list of relevant keywords for SEO)

Please follow these guidelines:
- If a particular piece of information is not present or cannot be accurately determined, set its value to null
- For UAE-based jobs, default jobCountry to 'United Arab Emirates', addressCountryISO to 'AE', and currency to 'AED'
- Extract salary amounts as numeric values only (remove currency symbols and text)
- For jobLocationType, if remote work is mentioned use TELECOMMUTE, otherwise use ON-SITE
- Ensure all list fields return actual lists, not strings
- Be specific and accurate in your extractions

Use this JSON schema:
{{
    "jobTitle": str,
    "orgName": str,
    "shortName": str,
    "RecruitmentPlace": str,
    "responsibilities": [str],
    "skills": [str],
    "qualifications": [str],
    "educationRequirements": str,
    "experienceRequirements": str,
    "MonthsOfExperience": int,
    "jobLocationType": str,
    "orgHeadquarter": str,
    "orgFounded": int,
    "orgType": str,
    "orgWeb": str,
    "streetAddress": str,
    "addressLocality": str,
    "addressRegion": str,
    "postalCode": str,
    "deadLine": str,
    "postedDate": str,
    "occupationalCategory": str,
    "industry": str,
    "meta_description": str,
    "addressCountryISO": str,
    "jobLevel": str,
    "category": [str],
    "jobCity": str,
    "jobCountry": str,
    "jobSummary": str,
    "jobGrade": str,
    "currency": str,
    "minSalary": int,
    "maxSalary": int,
    "salaryunittext": str,
    "EducationalOccupationalCredential_Category": str,
    "employmentType": str,
    "aboutOrg": str,
    "keywords": [str],
    "jobBenefits": [str]
}}

Return a valid JSON with the extracted information.
"""
        return prompt
    
    def process_job(self, job_data: RawJobData) -> Optional[Dict[str, Any]]:
        """Process job data through Gemini and return structured data"""
        try:
            prompt = self._get_extraction_prompt(job_data)
            self.logger.info(f"Processing job: {job_data.url}")
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                try:
                    result = json.loads(response.text)
                    self.logger.info(f"Successfully processed job: {job_data.url}")
                    return result
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for {job_data.url}: {e}")
                    # Try to clean and parse again
                    try:
                        cleaned_text = response.text.strip()
                        if cleaned_text.startswith('```json'):
                            cleaned_text = cleaned_text[7:]
                        if cleaned_text.endswith('```'):
                            cleaned_text = cleaned_text[:-3]
                        result = json.loads(cleaned_text)
                        return result
                    except:
                        self.logger.error(f"Failed to parse response for {job_data.url}")
                        return None
            else:
                self.logger.error(f"Empty response from Gemini for {job_data.url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing job {job_data.url}: {str(e)}")
            return None
