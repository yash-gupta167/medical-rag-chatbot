import google.generativeai as genai
import os
from typing import Dict, List
from .retrieval import HybridRetrieval
from .triage import MedicalTriage

class FirstAidChatbot:
    """
    RAG-Powered First-Aid Chatbot for Diabetes, Cardiac & Renal Emergencies
    As specified in Assignment.pdf
    """
    
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        if not os.getenv('GOOGLE_API_KEY'):
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
       
        self.retrieval = HybridRetrieval()
        self.triage = MedicalTriage()
        
        
        self.disclaimer = "⚠️ *This information is for educational purposes only and is not a substitute for professional medical advice.*"
        
        
        self.system_prompt = """You are a medical first-aid assistant specializing in diabetes, cardiac, and renal emergencies.

Your role:
1. Analyze symptoms to identify the most likely condition
2. Provide immediate first-aid steps
3. Suggest relevant medications when appropriate
4. Always include proper source citations
5. Keep responses under 250 words
6. Always start with the required medical disclaimer

*Format your response exactly as follows:
⚠️ This information is for educational purposes only and is not a substitute for professional medical advice.

Condition: [Most likely condition based on symptoms]
Immediate Actions:
- [First aid step 1]
- [First aid step 2]
- [First aid step 3]
Medications: [If applicable, mention specific medicines]
Sources: [Citation numbers in square brackets]

Be precise, actionable, and safety-focused. For life-threatening situations, always prioritize calling emergency services."""

    def initialize(self, file_path='data/Assignment-Data-Base.xlsx'):
        
        self.retrieval.initialize(file_path)
    
    def prepare_context(self, search_results: List[Dict]) -> str:
        
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            if result['search_type'] == 'local_semantic':
                sentence = result['sentence']
                context_parts.append(f"[{i}] Local Knowledge (ID {sentence['id']}): {sentence['content']}")
            elif result['search_type'] == 'web_search':
                context_parts.append(f"[{i}] Web Source: {result['title']}: {result['snippet']}")
            elif result['search_type'] == 'keyword_search':
                sentence = result['sentence']
                context_parts.append(f"[{i}] Keyword Match (ID {sentence['id']}): {sentence['content']}")
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, query: str) -> Dict:
        
        
        
        search_results, condition_type = self.retrieval.hybrid_search(query)
        
        
        urgency = self.triage.assess_urgency(query)
        
        
        context = self.prepare_context(search_results)
        
        
        response_text = self.call_gemini(query, context)
        
       
        return {
            'query': query,
            'condition_type': condition_type,
            'urgency_level': urgency,
            'response': response_text,
            'sources': search_results,
            'disclaimer': self.disclaimer
        }
    
    def call_gemini(self, query: str, context: str) -> str:
       
        
        user_prompt = f"""
{self.system_prompt}

User Query: "{query}"

Available Medical Knowledge:
{context}

Please analyze the symptoms, identify the most likely condition, and provide immediate first-aid guidance with proper citations following the exact format specified.
"""

        try:
            response = self.model.generate_content(user_prompt)
            generated_text = response.text.strip()
            
           
            if not generated_text.startswith("⚠️"):
                generated_text = f"{self.disclaimer}\n\n{generated_text}"
            
            return generated_text
            
        except Exception as e:
            return f"{self.disclaimer}\n\nI apologize, but I'm unable to process your query at the moment. Please consult a healthcare professional immediately for medical emergencies. Error: {str(e)}"


TEST_QUERIES = [
    "I'm sweating, shaky, and my glucometer reads 55 mg/dL—what should I do right now?",
    "My diabetic father just became unconscious; we think his sugar crashed. What immediate first-aid should we give?",
    "A pregnant woman with gestational diabetes keeps getting fasting readings around 130 mg/dL. What does this mean and how should we manage it?",
    "Crushing chest pain shooting down my left arm-do I chew aspirin first or call an ambulance?",
    "I'm having angina; how many nitroglycerin tablets can I safely take and when must I stop?",
    "Grandma has chronic heart failure, is suddenly short of breath, and her ankles are swelling. Any first-aid steps before we reach the ER?",
    "After working in the sun all day I've barely urinated and my creatinine just rose 0.4 mg/dL-could this be acute kidney injury and what should I do?",
    "CKD patient with a potassium level of 6.1 mmol/L—what emergency measures can we start right away?",
    "I took ibuprofen for back pain; now my flanks hurt and I'm worried about kidney damage-any immediate precautions?",
    "Type 2 diabetic, extremely thirsty, glucose meter says 'HI' but urine ketone strip is negative-what's happening and what's the first-aid?"
]
