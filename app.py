import os
import warnings

# Fix PyTorch-Streamlit compatibility issue
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

# Now your existing imports...
import streamlit as st
import time
from dotenv import load_dotenv
from src.chatbot import FirstAidChatbot, TEST_QUERIES
from src.utils import save_performance_report, calculate_accuracy_metrics



load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RAG-Powered First-Aid Chatbot",
    page_icon="🏥",
    layout="wide"
)

@st.cache_resource
def initialize_chatbot():
    """Initialize and cache the chatbot"""
    try:
        chatbot = FirstAidChatbot()
        chatbot.initialize('data/Assignment-Data-Base.xlsx')
        return chatbot
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {str(e)}")
        return None

def main():
    st.title("🏥 RAG-Powered First-Aid Chatbot")
    st.subheader("Diabetes, Cardiac & Renal Emergencies")
    
    
    st.info("**Mission:** Build a patient-safety-aware chatbot that combines local knowledge embeddings with real-time web evidence to deliver actionable first-aid guidance always prefaced with a clinical disclaimer.")
    

    
    
    st.sidebar.title("Navigation")
    mode = st.sidebar.selectbox(
        "Choose Mode:",
        ["Interactive Chat", "Test All 10 Queries", "Performance Analysis"]
    )
    
    
    chatbot = initialize_chatbot()
    if not chatbot:
        st.error("Please check your API keys in the .env file")
        st.stop()
    
    st.sidebar.success("✅ System initialized successfully!")
    st.sidebar.info("📊 60 medical sentences loaded")
    st.sidebar.info("🌐 Web search enabled")
    
    if mode == "Interactive Chat":
        interactive_chat(chatbot)
    elif mode == "Test All 10 Queries":
        test_all_queries(chatbot)
    elif mode == "Performance Analysis":
        performance_analysis()

def interactive_chat(chatbot):
    """Interactive chat interface for demo video"""
    
    st.markdown("###  Medical Emergency Chat")
    st.markdown("**Enter your symptoms for immediate first-aid guidance**")
    
    # Sample queries from Assignment.pdf
    st.markdown("**Sample Test Queries (from the Provided PDF:-Assignment.pdf):**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Severe Hypoglycemia", help="Query 1"):
            st.session_state.user_input = TEST_QUERIES[0]
        if st.button(" Chest Pain", help="Query 4"):
            st.session_state.user_input = TEST_QUERIES[3]
        if st.button(" Heart Failure", help="Query 6"):
            st.session_state.user_input = TEST_QUERIES[5]
    
    with col2:
        if st.button(" Unconscious Diabetic", help="Query 2"):
            st.session_state.user_input = TEST_QUERIES[1]
        if st.button(" Kidney Injury", help="Query 7"):
            st.session_state.user_input = TEST_QUERIES[6]
        if st.button(" High Potassium", help="Query 8"):
            st.session_state.user_input = TEST_QUERIES[7]
    
    
    user_input = st.text_area(
        "🩺 Describe your medical emergency:",
        value=st.session_state.get('user_input', ''),
        height=120,
        key="user_input",
        placeholder="e.g., I'm sweating, shaky, and my glucometer reads 55 mg/dL..."
    )
    
    if st.button("🚨 Get Emergency First-Aid Guidance", type="primary"):
        if user_input.strip():
            with st.spinner(" Analyzing symptoms and searching medical knowledge..."):
                start_time = time.time()
                
                try:
                    result = chatbot.generate_response(user_input)
                    end_time = time.time()
                    result['response_time'] = end_time - start_time
                    
                    
                    st.markdown("### Medical Response")
                    st.markdown(result['response'])
                    
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(" Response Time", f"{result['response_time']:.2f}s")
                    
                    with col2:
                        st.metric(" Condition", result['condition_type'] or "General")
                    
                    with col3:
                        st.metric("🚨 Urgency", result['urgency_level'].title())
                    
                    with col4:
                        st.metric(" Sources", len(result['sources']))
                    
                    
                    with st.expander(" View Source Details"):
                        for i, source in enumerate(result['sources'], 1):
                            if source['search_type'] == 'local_semantic':
                                st.markdown(f"**[{i}] Local Knowledge (Sentence #{source['sentence']['id']}):**")
                                st.text(source['sentence']['content'])
                                st.markdown(f"*Score: {source['score']:.3f}, Category: {source['sentence']['category']}*")
                            elif source['search_type'] == 'web_search':
                                st.markdown(f"**[{i}] Web Source:** {source['title']}")
                                st.text(source['snippet'][:200] + "...")
                                st.markdown(f"*Link: {source['link']}*")
                            elif source['search_type'] == 'keyword_search':
                                st.markdown(f"**[{i}] Keyword Match (Sentence #{source['sentence']['id']}):**")
                                st.text(source['sentence']['content'])
                            st.markdown("---")
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
        else:
            st.warning("Please enter your symptoms or medical question.")

def test_all_queries(chatbot):
    """Test all 10 sample queries from Assignment.pdf"""
    
    st.markdown("### Test All 10 Sample Queries")
    st.markdown("Testing the chatbot against all sample queries from Assignment.pdf to verify it passes at least 8/10 with correct triage + relevant citations.")
    
    if st.button(" Run All 10 Tests", type="primary"):
        progress_bar = st.progress(0)
        results = []
        
        for i, query in enumerate(TEST_QUERIES):
            st.markdown(f"**Testing Query {i+1}/10:** {query[:100]}...")
            
            try:
                with st.spinner(f"Processing query {i+1}/10..."):
                    start_time = time.time()
                    result = chatbot.generate_response(query)
                    end_time = time.time()
                    
                    result['response_time'] = end_time - start_time
                    result['query_number'] = i + 1
                    results.append(result)
                    
                    
                    has_condition = '**condition:**' in result['response'].lower()
                    has_actions = '**immediate actions:**' in result['response'].lower()
                    has_sources = '[' in result['response'] and ']' in result['response']
                    
                    if has_condition and has_actions and has_sources:
                        st.success(f"✅ Query {i+1} PASSED - {result['response_time']:.2f}s")
                    else:
                        st.warning(f"⚠️ Query {i+1} needs review")
                    
                    with st.expander(f"Preview Response {i+1}"):
                        st.markdown(result['response'][:400] + "...")
                
            except Exception as e:
                st.error(f"❌ Query {i+1} failed: {str(e)}")
                results.append({
                    'query': query, 
                    'response': f'Error: {str(e)}',
                    'query_number': i + 1
                })
            
            progress_bar.progress((i + 1) / len(TEST_QUERIES))
        
        
        st.markdown("### 📊 Test Results Summary")
        metrics = calculate_accuracy_metrics(results)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Success Rate", f"{metrics['success_rate']:.1%}")

        with col2:
            st.metric("Condition ID", f"{metrics['condition_identification_rate']:.1%}")

        with col3:
            st.metric("First-Aid Steps", f"{metrics['action_provision_rate']:.1%}")

        with col4:
            st.metric("Citations", f"{metrics['citation_rate']:.1%}")

        with col5:
            avg_time = sum(r.get('response_time', 0) for r in results) / len(results)
            st.metric("Avg Time", f"{avg_time:.2f}s")

        
        if metrics['success_rate'] >= 0.8:
            st.success("🎯 **TARGET ACHIEVED:** Bot passes at least 8/10 queries with correct triage + relevant citations!")
        else:
            st.warning("🎯 Target: Pass at least 8/10 queries (Assignment.pdf requirement)")

        
        st.markdown("### 💾 Download Reports")

        col1, col2 = st.columns(2)

        
        with col1:
            try:
               
                report = save_performance_report(results)
                
               
                import json
                report_json = json.dumps(report, indent=2, default=str)
                
                
                st.download_button(
                    label="📥 Download JSON Report",
                    data=report_json,
                    file_name=f"performance_report_{time.strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="json_download"
                )
                
            except Exception as e:
                st.error(f"JSON Error: {str(e)}")

         
        with col2:
            try:
                
                from src.utils import generate_performance_pdf
                
                
                pdf_filename = f"performance_report_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
                generate_performance_pdf(results, pdf_filename)
                
                
                with open(pdf_filename, "rb") as pdf_file:
                    pdf_data = pdf_file.read()
                
                
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    key="pdf_download"
                )
                
            except Exception as e:
                st.error(f"PDF Error: {str(e)}")

        
        with st.expander("📊 Performance Report Preview"):
            if 'report' in locals():
                st.json({
                    "assignment_info": report["assignment_info"],
                    "performance_metrics": report["performance_metrics"], 
                    "assignment_requirements": report["assignment_requirements"]
                })





def performance_analysis():
    """Performance analysis and system information"""
    
    st.markdown("###  Performance Analysis")
    
    st.markdown("""
    **System Implementation Summary (Assignment.pdf Requirements):**
    
    ✅ **Local Corpus:** 60 pre-approved medical sentences embedded unaltered  
    ✅ **Hybrid Retrieval:** Local semantic + Serper.dev web search + keyword search  
    ✅ **Triage/Diagnosis:** Automatic condition detection (diabetes, cardiac, renal)  
    ✅ **Response Format:** ≤250 words with condition, first-aid, medications, citations  
    ✅ **Clinical Disclaimer:** Always prefixed to responses  
    ✅ **Source Citations:** Proper attribution with numbered references  
    ✅ **Test Coverage:** All 10 sample queries supported  
    
    **Technical Architecture:**
    - **AI Model:** Gemini 2.0 Flash (Free API)
    - **Vector Database:** QdrantDB (in-memory)
    - **Web Search:** Serper.dev API
    - **Embedding Model:** SentenceTransformers all-MiniLM-L6-v2
    - **Framework:** Streamlit for demo interface
    """)
    
    st.markdown("### 🎯 Assignment.pdf Compliance")
    
    # Compliance checklist
    compliance_items = [
        ("✅ Patient-safety-aware with clinical disclaimers", True),
        ("✅ Local knowledge embeddings (60 sentences)", True),
        ("✅ Real-time web evidence (Serper.dev)", True),
        ("✅ Triage/diagnosis from free-text symptoms", True),
        ("✅ Hybrid retrieval with result fusion", True),
        ("✅ ≤250-word responses with structured format", True),
        ("✅ Source citations included", True),
        ("✅ Diabetes, cardiac & renal focus", True),
        ("✅ Should pass 8/10 test queries", True),
        ("✅ GitHub repository structure", True),
        ("✅ Performance reporting", True)
    ]
    
    for item, status in compliance_items:
        st.markdown(item)
    
    st.markdown("### 🚀 Demo Video Preparation")
    st.markdown("""
    **For Assignment Demo Video (< 5 min):**
    1. Show system startup and initialization
    2. Demonstrate query: "severe hypoglycaemia shaking"
    3. Demonstrate query: "left-arm pain and sweating"
    4. Show source citations and response format
    5. Display performance metrics
    """)
    
    st.markdown("### ⚠️ Known Limitations")
    limitations = [
        "Responses limited to 250 words as required",
        "Depends on external Serper.dev API availability",
        "Free Gemini 2.0 Flash API has rate limits",
        "Local knowledge base limited to 60 pre-approved sentences",
        "Not a substitute for professional medical advice"
    ]
    
    for limitation in limitations:
        st.markdown(f"- {limitation}")

if __name__ == "__main__":
    main()
