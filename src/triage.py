import re
from typing import Optional, List

class MedicalTriage:
    
    
    def __init__(self):
        self.condition_keywords = {
            'diabetes': [
                'glucose', 'blood sugar', 'insulin', 'diabetic', 'hypoglycemia', 'hyperglycemia', 
                'ketoacidosis', 'DKA', 'metformin', 'HbA1c', 'glucometer', 'shaky', 'sweating',
                'gestational diabetes', 'type 1', 'type 2', 'mg/dL', 'fasting glucose'
            ],
            'cardiac': [
                'chest pain', 'heart', 'cardiac', 'angina', 'myocardial', 'infarction', 
                'crushing pain', 'left arm', 'nitroglycerin', 'aspirin', 'CPR', 'defibrillation',
                'heart attack', 'heart failure', 'edema', 'shortness of breath', 'ankles swelling'
            ],
            'renal': [
                'kidney', 'renal', 'creatinine', 'urine', 'potassium', 'dialysis', 'AKI', 'CKD',
                'acute kidney injury', 'chronic kidney disease', 'nephrotoxic', 'barely urinated',
                'ibuprofen', 'NSAIDs', 'flank pain', 'mmol/L'
            ]
        }
        
        self.urgency_keywords = [
            'unconscious', 'crushing', 'severe', 'emergency', 'call 112', 'ambulance',
            'cannot breathe', 'chest pain', 'left arm', 'barely urinated'
        ]
    
    def detect_condition(self, query: str) -> Optional[str]:
        
        query_lower = query.lower()
        
        condition_scores = {}
        for condition, keywords in self.condition_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            condition_scores[condition] = score
        
        if max(condition_scores.values()) > 0:
            return max(condition_scores, key=condition_scores.get)
        return None
    
    def assess_urgency(self, query: str) -> str:
        
        query_lower = query.lower()
        urgent_matches = sum(1 for keyword in self.urgency_keywords if keyword in query_lower)
        
        if urgent_matches >= 2:
            return 'Very high'
        elif urgent_matches == 1:
            return 'high'
        else:
            return 'low'
    
    def extract_keywords(self, query: str) -> List[str]:
        
        query_lower = query.lower()
        extracted = []
        
        
        for condition, keywords in self.condition_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    extracted.append(keyword)
        
        
        numbers = re.findall(r'\d+\.?\d*', query)
        extracted.extend(numbers)
        
        return list(set(extracted))
