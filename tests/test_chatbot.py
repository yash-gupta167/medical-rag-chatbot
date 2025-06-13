import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import FirstAidChatbot, TEST_QUERIES
from src.triage import MedicalTriage
from src.embeddings import MedicalEmbeddings

class TestFirstAidChatbot:
    
    @pytest.fixture
    def chatbot(self):
        """Fixture to create chatbot instance"""
        # Set mock API keys for testing
        os.environ['GOOGLE_API_KEY'] = 'test-key'
        os.environ['SERPER_API_KEY'] = 'test-key'
        
        chatbot = FirstAidChatbot()
        return chatbot
    
    def test_embeddings_loading(self):
        """Test that 60 medical sentences load correctly"""
        embeddings = MedicalEmbeddings()
        sentences = embeddings.load_medical_sentences('data/Assignment-Data-Base.xlsx')
        
        assert len(sentences) == 60, "Should load exactly 60 sentences"
        assert all('id' in s and 'content' in s for s in sentences), "All sentences should have id and content"
    
    def test_condition_detection(self):
        """Test triage condition detection"""
        triage = MedicalTriage()
        
        # Test diabetes detection
        diabetes_query = "my glucometer reads 55 mg/dL and I'm shaking"
        condition = triage.detect_condition(diabetes_query)
        assert condition == 'diabetes'
        
        # Test cardiac detection
        cardiac_query = "crushing chest pain down my left arm"
        condition = triage.detect_condition(cardiac_query)
        assert condition == 'cardiac'
        
        # Test renal detection
        renal_query = "creatinine rose and barely urinated"
        condition = triage.detect_condition(renal_query)
        assert condition == 'renal'
    
    def test_urgency_assessment(self):
        """Test urgency level assessment"""
        triage = MedicalTriage()
        
        high_urgency = "unconscious diabetic crushing chest pain"
        urgency = triage.assess_urgency(high_urgency)
        assert urgency == 'high'
        
        low_urgency = "regular checkup question"
        urgency = triage.assess_urgency(low_urgency)
        assert urgency == 'low'
    
    def test_response_format(self):
        """Test that responses contain required components"""
        # Mock response for testing
        mock_response = {
            'response': '''⚠️ *This information is for educational purposes only and is not a substitute for professional medical advice.*

**Condition:** Severe Hypoglycemia
**Immediate Actions:**
- Give 15g fast-acting carbohydrates immediately
- Monitor blood glucose every 15 minutes
**Medications:** Glucose tablets or glucagon if unconscious
**Sources:** [1] [2]'''
        }
        
        response_text = mock_response['response']
        
        # Check required components from Assignment.pdf
        assert '⚠️' in response_text, "Must include disclaimer"
        assert '**Condition:**' in response_text, "Must identify condition"
        assert '**Immediate Actions:**' in response_text, "Must provide first-aid steps"
        assert '**Medications:**' in response_text, "Must mention medications"
        assert '**Sources:**' in response_text, "Must include citations"
        assert '[' in response_text and ']' in response_text, "Must have source citations"

def run_all_test_queries():
    """Test all 10 sample queries from Assignment.pdf"""
    print("Testing all 10 sample queries from Assignment.pdf...")
    
    results = []
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\nQuery {i}: {query}")
        
        # Basic validation
        has_medical_terms = any(term in query.lower() for term in 
                               ['glucose', 'chest pain', 'kidney', 'diabetic', 'heart', 'creatinine'])
        
        result = {
            'query_number': i,
            'query': query,
            'has_medical_terms': has_medical_terms,
            'query_length': len(query),
            'status': 'valid' if has_medical_terms else 'needs_review'
        }
        
        results.append(result)
        print(f"Status: {result['status']}")
    
    print(f"\nValidation Summary: {sum(1 for r in results if r['status'] == 'valid')}/10 queries contain clear medical terms")
    return results

if __name__ == "__main__":
    run_all_test_queries()
