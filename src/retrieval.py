from typing import List, Dict, Tuple
from .embeddings import MedicalEmbeddings
from .web_search import SerperWebSearch
from .triage import MedicalTriage

class HybridRetrieval:
    """
    Hybrid Retrieval System as specified in Assignment.pdf:
    - Local semantic search over 60 provided medical snippets
    - Serper.dev web search for fresh evidence
    - Fuse results and rank by relevance
    """
    
    def __init__(self):
        self.embeddings = MedicalEmbeddings()
        self.web_search = SerperWebSearch()
        self.triage = MedicalTriage()
        
    def initialize(self, file_path='data/Assignment-Data-Base.xlsx'):
        """Initialize the hybrid retrieval system"""
        # Initialize Qdrant
        self.embeddings.initialize_qdrant()
        
        # Load and embed the 60 pre-approved sentences
        self.embeddings.load_medical_sentences(file_path)
        self.embeddings.create_embeddings()
        
        print("Hybrid Retrieval System initialized successfully")
    
    def perform_local_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Local semantic search over the 60 medical snippets"""
        try:
            results = self.embeddings.search_similar(query, top_k)
            
            # Add source information
            for result in results:
                result['source'] = 'local_knowledge'
                result['sentence']['source_type'] = 'verified_medical_content'
            
            return results
        except Exception as e:
            print(f"Error in local search: {e}")
            return []
    
    def perform_web_search(self, query: str, condition_type: str = None) -> List[Dict]:
        """Serper.dev web search for fresh evidence"""
        try:
            if condition_type:
                results = self.web_search.search_with_medical_keywords(query, condition_type)
            else:
                results = self.web_search.search_medical_query(query)
            
            return results
        except Exception as e:
            print(f"Error in web search: {e}")
            return []
    
    def perform_keyword_search(self, query: str) -> List[Dict]:
        """Additional keyword search for bonus points (as mentioned in PDF)"""
        keywords = self.triage.extract_keywords(query)
        
        # Search local sentences for keyword matches
        keyword_results = []
        for sentence in self.embeddings.sentences:
            content_lower = sentence['content'].lower()
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            
            if matches > 0:
                keyword_results.append({
                    'sentence': sentence,
                    'score': matches / len(keywords),  # Relevance score
                    'rank': len(keyword_results) + 1,
                    'source': 'keyword_search'
                })
        
        # Sort by score
        keyword_results.sort(key=lambda x: x['score'], reverse=True)
        return keyword_results[:3]
    
    def fuse_and_rank_results(self, local_results: List[Dict], web_results: List[Dict], 
                             keyword_results: List[Dict], local_weight: float = 0.5, 
                             web_weight: float = 0.3, keyword_weight: float = 0.2) -> List[Dict]:
        """Fuse results (semantic + serper dev results) and rank by relevance"""
        
        all_results = []
        
        # Add local semantic search results
        for result in local_results:
            result['final_score'] = result['score'] * local_weight
            result['search_type'] = 'local_semantic'
            all_results.append(result)
        
        # Add web search results
        for i, result in enumerate(web_results):
            relevance_score = 1.0 - (i * 0.1)  # Decreasing score by rank
            result['final_score'] = relevance_score * web_weight
            result['search_type'] = 'web_search'
            all_results.append(result)
        
        # Add keyword search results
        for result in keyword_results:
            result['final_score'] = result['score'] * keyword_weight
            result['search_type'] = 'keyword_search'
            all_results.append(result)
        
        # Sort by final score and remove duplicates
        all_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return all_results[:5]  # Return top 5 results
    
    def hybrid_search(self, query: str) -> Tuple[List[Dict], str]:
        """
        Main hybrid search function:
        Combines local semantic search + web search + keyword search
        """
        
        # Step 1: Triage - detect condition type
        condition_type = self.triage.detect_condition(query)
        
        # Step 2: Perform all three types of search
        local_results = self.perform_local_search(query, top_k=3)
        web_results = self.perform_web_search(query, condition_type)
        keyword_results = self.perform_keyword_search(query)
        
        # Step 3: Fuse and rank results by relevance
        fused_results = self.fuse_and_rank_results(local_results, web_results, keyword_results)
        
        return fused_results, condition_type
