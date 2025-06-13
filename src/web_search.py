import requests
import os
from typing import List, Dict

class SerperWebSearch:
    """Serper.dev web search integration as required by Assignment.pdf"""
    
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables. Sign up at https://serper.dev/")
        
        self.base_url = "https://google.serper.dev/search"
        
    def search_medical_query(self, query: str, num_results: int = 3) -> List[Dict]:
        """Search for fresh medical evidence using Serper.dev API"""
        
        # Enhance query with medical context for better results
        medical_query = f"{query} first aid emergency medical treatment"
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json',
        }
        
        data = {
            'q': medical_query,
            'num': num_results,
            'gl': 'us',
            'hl': 'en'
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            search_results = []
            
            # Process organic results
            if 'organic' in results:
                for item in results['organic']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'source': 'web_search',
                        'rank': len(search_results) + 1
                    })
            
            # Process knowledge graph if available
            if 'knowledgeGraph' in results:
                kg = results['knowledgeGraph']
                search_results.insert(0, {
                    'title': kg.get('title', ''),
                    'snippet': kg.get('description', ''),
                    'link': kg.get('website', ''),
                    'source': 'knowledge_graph',
                    'rank': 0
                })
            
            return search_results
            
        except requests.exceptions.RequestException as e:
            print(f"Error in web search: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in web search: {e}")
            return []
    
    def search_with_medical_keywords(self, query: str, condition_type: str = None) -> List[Dict]:
        """Enhanced search with condition-specific medical keywords"""
        
        medical_keywords = {
            'diabetes': 'diabetes glucose insulin hypoglycemia ketoacidosis blood sugar emergency',
            'cardiac': 'heart cardiac chest pain angina myocardial infarction CPR defibrillation emergency',
            'renal': 'kidney renal creatinine dialysis AKI CKD hyperkalemia emergency'
        }
        
        enhanced_query = query
        if condition_type and condition_type in medical_keywords:
            enhanced_query += f" {medical_keywords[condition_type]}"
        
        enhanced_query += " first aid treatment emergency medical"
        
        return self.search_medical_query(enhanced_query)
