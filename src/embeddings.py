import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os

class MedicalEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.collection_name = "medical_sentences"
        self.client = None
        self.sentences = []
        
    def initialize_qdrant(self, url=None):
        """Initialize Qdrant client (in-memory for demo)"""
        if url is None:
            self.client = QdrantClient(":memory:")
        else:
            self.client = QdrantClient(url=url)

        
    def load_medical_sentences(self, file_path='data/Assignment-Data-Base.xlsx'):
        """Load the 60 pre-approved sentences from Excel file (unaltered as per PDF)"""
        df = pd.read_excel(file_path, sheet_name='Database')
        self.sentences = []
        
        for _, row in df.iterrows():
            self.sentences.append({
                'id': int(row['#']),
                'content': str(row['Sentence']),
                'category': self._categorize_sentence(str(row['Sentence']))
            })
        
        return self.sentences
    
    def _categorize_sentence(self, content):
        """Categorize sentences into diabetes, cardiac, or renal"""
        content_lower = content.lower()
        
        diabetes_keywords = ['diabetes', 'glucose', 'insulin', 'hypoglycaemia', 'hyperglycaemic', 'ketoacidosis', 'hba1c', 'metformin']
        cardiac_keywords = ['chest pain', 'heart', 'cardiac', 'angina', 'myocardial', 'infarction', 'defibrillation', 'cpr']
        renal_keywords = ['kidney', 'renal', 'creatinine', 'dialysis', 'aki', 'ckd', 'potassium', 'nephro']
        
        if any(keyword in content_lower for keyword in diabetes_keywords):
            return 'diabetes'
        elif any(keyword in content_lower for keyword in cardiac_keywords):
            return 'cardiac'
        elif any(keyword in content_lower for keyword in renal_keywords):
            return 'renal'
        else:
            return 'general'
    
    def create_collection(self):
        """Create collection in Qdrant"""
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.model.get_sentence_embedding_dimension(),
                distance=Distance.COSINE,
            ),
        )
    
    def create_embeddings(self):
        """Create embeddings for all 60 medical sentences"""
        if not self.sentences:
            raise ValueError("No sentences loaded. Call load_medical_sentences first.")
        
        self.create_collection()
        
        points = []
        for sentence in self.sentences:
            vector = self.model.encode(sentence['content']).tolist()
            point = PointStruct(
                id=sentence['id'],
                vector=vector,
                payload={
                    'content': sentence['content'],
                    'category': sentence['category'],
                    'id': sentence['id']
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"Successfully created embeddings for {len(points)} medical sentences")
        return len(points)
    
    def search_similar(self, query, top_k=3):
        """Search for similar medical sentences"""
        query_vector = self.model.encode(query).tolist()
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        
        results = []
        for i, hit in enumerate(search_result):
            results.append({
                'sentence': hit.payload,
                'score': float(hit.score),
                'rank': i + 1
            })
        
        return results
