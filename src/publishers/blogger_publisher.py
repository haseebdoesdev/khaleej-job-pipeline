import time
import requests
import json
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from datetime import datetime
import logging
from typing import Optional
from ..models.job_models import ProcessedJobData

class BloggerPublisher:
    """Publishes job postings to Blogger"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = None
    
    def setup_driver(self) -> Optional[webdriver.Chrome]:
        """Setup Chrome driver for Blogger automation"""
        try:
            url = self.config.selenium_url
            headers = {'Content-Type': 'application/json'}
            
            # Open browser using selenium grid
            json_data = {"id": self.config.browser_id}
            response = requests.post(
                f"{url}/browser/open",
                data=json.dumps(json_data),
                headers=headers
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to open browser: {response.text}")
                return None
            
            res = response.json()
            driver_path = res['data']['driver']
            debugger_address = res['data']['http']
            
            # Setup Chrome options
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            
            chrome_service = Service(driver_path)
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
            
            self.logger.info("Browser setup successful")
            return driver
            
        except Exception as e:
            self.logger.error(f"Error setting up driver: {str(e)}")
            return None
    
    def create_blog_post(self, job_data: ProcessedJobData, html_content: str) -> bool:
        """Create a blog post on Blogger"""
        try:
            if not self.driver:
                self.driver = self.setup_driver()
                if not self.driver:
                    return False
            
            # Navigate to Blogger
            self.driver.get(self.config.blog_base_url)
            time.sleep(2)
            
            # Click "New Post" button
            new_post_elements = self.driver.find_elements(
                By.XPATH,
                '//*[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "new post")]'
            )
            new_post_button = None
            for element in new_post_elements:
                if element.is_displayed():
                    new_post_button = element
                    break
            
            if not new_post_button:
                self.logger.error("Could not find 'New Post' button")
                return False
            
            new_post_button.click()
            time.sleep(8)
            
            # Handle HTML editor setup
            backspace_needed = False
            if not WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="CodeMirror-gutter CodeMirror-linenumbers"]'))
            ).is_displayed():
                # Switch to HTML view
                elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    '[class="MocG8c m5D6Fd LMgvRb KKjvXb"] [class="DPvwYc GHpiyd"]'
                )
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        break
                
                time.sleep(1)
                self.driver.find_element(
                    By.CSS_SELECTOR, 
                    '[ssk="6:Rxil4c"] [class="MocG8c m5D6Fd LMgvRb"]'
                ).click()
                backspace_needed = True
            
            # Wait for editor to be ready
            while True:
                try:
                    self.driver.find_elements(By.CSS_SELECTOR, '[class="CodeMirror-scroll"]')[-1].click()
                    break
                except:
                    time.sleep(1)
            
            time.sleep(2)
            
            # Get input field
            input_field = self.driver.find_elements(By.CSS_SELECTOR, 'textarea[autocorrect="off"]')[-1]
            
            # Clear default content if needed
            if backspace_needed:
                for _ in range(13):
                    input_field.send_keys(Keys.BACKSPACE)
                    time.sleep(0.1)
                time.sleep(1)
            
            # Insert HTML content
            pyperclip.copy(html_content)
            input_field.send_keys(Keys.CONTROL, 'v')
            time.sleep(2)
            
            # Set labels
            labels = self._generate_labels(job_data)
            self._set_labels(labels)
            
            # Set search description
            self._set_search_description(job_data.search_description)
            
            # Set location (country)
            self._set_location(job_data.job_country)
            
            # Set permalink
            permalink = self._generate_permalink(job_data)
            self._set_permalink(permalink)
            
            # Set title
            title = self._generate_title(job_data)
            self._set_title(title)
            
            # Publish post
            self._publish_post()
            
            self.logger.info(f'Post created successfully: "{title}" at {datetime.now().strftime("%H:%M:%S")}')
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating blog post: {str(e)}")
            return False
    
    def _generate_labels(self, job_data: ProcessedJobData) -> str:
        """Generate labels for the blog post"""
        labels_list = []
        
        if job_data.categories:
            labels_list.append(job_data.categories)
        if job_data.job_industry:
            labels_list.append(job_data.job_industry)
        if job_data.app_type:
            labels_list.append(job_data.app_type)
        if job_data.job_location_type and job_data.job_location_type != "ON-SITE":
            labels_list.append(job_data.job_location_type)
        if job_data.job_country:
            labels_list.append(job_data.job_country)
        if job_data.short_name:
            labels_list.append(job_data.short_name)
        
        labels = ', '.join(labels_list)
        
        # Ensure labels don't exceed Blogger's limit
        if len(labels) > 200:
            # Truncate intelligently
            labels_list = labels_list[:4]  # Keep first 4 items
            labels = ', '.join(labels_list)
        
        return labels
    
    def _generate_permalink(self, job_data: ProcessedJobData) -> str:
        """Generate permalink for the blog post"""
        current_date = datetime.now()
        job_id = job_data.job_value_id or 1
        return f'https://www.khaleejtimes.com/{current_date.strftime("%Y/%m")}/{job_id}'
    
    def _generate_title(self, job_data: ProcessedJobData) -> str:
        """Generate title for the blog post"""
        return f'{job_data.title.title()} at {job_data.short_name.strip()} - {job_data.job_country}'
    
    def _set_labels(self, labels: str):
        """Set labels for the blog post"""
        try:
            # Try to find and click labels section
            try:
                labels_elements = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'separate labels')]"
                )
                labels_input = None
                for element in labels_elements:
                    if element.is_displayed():
                        labels_input = element
                        break
                
                if not labels_input:
                    # Click Labels section first
                    self.driver.find_elements(By.XPATH, '//*[contains(text(), "Labels")]')[-1].click()
                    time.sleep(0.7)
                    labels_elements = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'separate labels')]"
                    )
                    labels_input = labels_elements[0] if labels_elements else None
                
                if labels_input:
                    labels_input.click()
                    time.sleep(0.6)
                    labels_input.send_keys(labels)
                    time.sleep(0.7)
                    # Click away from labels
                    self.driver.find_elements(By.XPATH, '//*[contains(text(), "Labels")]')[-1].click()
                    time.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Could not set labels: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error setting labels: {str(e)}")
    
    def _set_search_description(self, description: str):
        """Set search description for the blog post"""
        try:
            # Click Search Description
            search_desc_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(text(), 'Search Description')]"
            )
            for element in search_desc_elements:
                if element.is_displayed():
                    element.click()
                    break
            
            time.sleep(0.9)
            
            # Find and fill description field
            desc_fields = self.driver.find_elements(By.CSS_SELECTOR, '[maxlength="150"]')
            for field in desc_fields:
                if field.is_displayed():
                    field.click()
                    time.sleep(0.5)
                    field.send_keys(description[:150])  # Respect max length
                    break
            
            time.sleep(0.6)
            
            # Click away
            search_desc_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(text(), 'Search Description')]"
            )
            for element in search_desc_elements:
                if element.is_displayed():
                    element.click()
                    break
            
        except Exception as e:
            self.logger.error(f"Error setting search description: {str(e)}")
    
    def _set_location(self, location: str):
        """Set location for the blog post"""
        try:
            # Click Location
            location_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(text(), 'Location')]"
            )
            for element in location_elements:
                if element.is_displayed():
                    element.click()
                    break
            
            time.sleep(0.6)
            
            # Find and fill location field
            location_inputs = self.driver.find_elements(
                By.XPATH, 
                "//input[contains(@aria-label, 'Search input')]"
            )
            for input_field in location_inputs:
                if input_field.is_displayed():
                    input_field.click()
                    time.sleep(0.6)
                    input_field.send_keys(location)
                    break
            
            time.sleep(0.6)
            
            # Click away
            location_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(text(), 'Location')]"
            )
            for element in location_elements:
                if element.is_displayed():
                    element.click()
                    break
            
        except Exception as e:
            self.logger.error(f"Error setting location: {str(e)}")
    
    def _set_permalink(self, permalink: str):
        """Set custom permalink for the blog post"""
        try:
            # Click Links
            self.driver.find_element(By.XPATH, '//*[contains(text(), "Links")]').click()
            time.sleep(0.6)
            
            # Click Custom Permalink
            custom_permalink_elements = self.driver.find_elements(
                By.XPATH,
                "//*[translate(normalize-space(@aria-label), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='custom permalink']"
            )
            for element in custom_permalink_elements:
                if element.is_displayed():
                    element.click()
                    break
            
            time.sleep(0.6)
            
            # Set permalink
            permalink_inputs = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Custom Permalink Input"]')
            if permalink_inputs:
                permalink_input = permalink_inputs[-1]
                permalink_input.click()
                time.sleep(0.8)
                permalink_input.send_keys(permalink)
                time.sleep(0.6)
            
            # Click away
            self.driver.find_elements(By.XPATH, '//*[contains(text(), "Permalink")]')[-1].click()
            time.sleep(0.6)
            
        except Exception as e:
            self.logger.error(f"Error setting permalink: {str(e)}")
    
    def _set_title(self, title: str):
        """Set title for the blog post"""
        try:
            # Set reader comments option
            self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Option')]")[-1].click()
            time.sleep(0.6)
            
            # Select appropriate radio button (allow comments)
            radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[role="radio"]')
            if radio_buttons:
                radio_buttons[-1].click()
            time.sleep(0.6)
            
            # Click away from options
            self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Option')]")[-1].click()
            time.sleep(0.6)
            
            # Set title
            title_fields = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Title"]')
            if title_fields:
                title_field = title_fields[-1]
                title_field.click()
                time.sleep(0.6)
                title_field.send_keys(title)
                time.sleep(0.6)
            
        except Exception as e:
            self.logger.error(f"Error setting title: {str(e)}")
    
    def _publish_post(self):
        """Publish the blog post"""
        try:
            # Click Publish button
            publish_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Publish"]')
            if publish_buttons:
                publish_buttons[-1].click()
                time.sleep(0.6)
            
            # Confirm publish
            confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[class="XfpsVe J9fJmf"] [autofocus]')
            if confirm_buttons:
                confirm_buttons[-1].click()
                time.sleep(3)
            
        except Exception as e:
            self.logger.error(f"Error publishing post: {str(e)}")
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None