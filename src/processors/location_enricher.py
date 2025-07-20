import requests
import logging
from typing import Optional, Dict, Any

class LocationEnricher:
    """Enriches job data with Google Places API location information"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_key = config.google_places_api_key
    
    def get_place_info(self, address: str) -> Optional[Dict[str, Any]]:
        """Get place information from Google Places API"""
        try:
            # Find place request
            find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            find_params = {
                "input": address,
                "inputtype": "textquery",
                "fields": "place_id,formatted_address",
                "key": self.api_key
            }
            
            response = requests.get(find_place_url, params=find_params)
            
            if response.status_code == 200:
                place_data = response.json()
                
                if place_data.get('candidates'):
                    place_id = place_data['candidates'][0]['place_id']
                    
                    # Place details request
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        "place_id": place_id,
                        "fields": "formatted_address,address_component",
                        "key": self.api_key
                    }
                    
                    details_response = requests.get(details_url, params=details_params)
                    
                    if details_response.status_code == 200:
                        place_details = details_response.json()
                        return self._extract_address_components(place_details)
            
        except Exception as e:
            self.logger.error(f"Error getting place info for '{address}': {str(e)}")
        
        return None
    
    def _extract_address_components(self, place_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract address components from place details"""
        components = place_details.get('result', {}).get('address_components', [])
        
        address_info = {
            "postal_code": None,
            "street_address": None,
            "region": None,
            "locality": None
        }
        
        route = None
        sublocality = None
        
        for component in components:
            types = component.get('types', [])
            long_name = component.get('long_name')
            
            if "postal_code" in types:
                address_info["postal_code"] = long_name
            elif "route" in types:
                route = long_name
            elif "sublocality" in types:
                sublocality = long_name
            elif "administrative_area_level_1" in types:
                address_info["region"] = long_name
            elif "locality" in types:
                address_info["locality"] = long_name
        
        # Combine route and sublocality for street address
        if route and sublocality:
            address_info["street_address"] = f"{route}, {sublocality}"
        else:
            address_info["street_address"] = route or sublocality
        
        return address_info
    
    def enrich_job_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich job data with location information"""
        try:
            org_name = processed_data.get('shortName', '')
            job_country = processed_data.get('jobCountry', '')
            
            if org_name and job_country:
                search_query = f"{org_name} {job_country}"
                place_info = self.get_place_info(search_query)
                
                if place_info:
                    # Update address fields if they're empty or None
                    if not processed_data.get('streetAddress'):
                        processed_data['streetAddress'] = place_info.get('street_address') or processed_data.get('jobCity') or job_country
                    
                    if not processed_data.get('addressLocality'):
                        processed_data['addressLocality'] = place_info.get('locality') or processed_data.get('jobCity') or job_country
                    
                    if not processed_data.get('addressRegion'):
                        processed_data['addressRegion'] = place_info.get('region') or processed_data.get('jobCity') or job_country
                    
                    if not processed_data.get('postalCode'):
                        processed_data['postalCode'] = place_info.get('postal_code') or "00000"
                
        except Exception as e:
            self.logger.error(f"Error enriching location data: {str(e)}")
        
        return processed_data
