import streamlit as st
import requests
import PyPDF2
import re 
from io import BytesIO

# Define API Key and Endpoint
API_KEY = "AIzaSyCYlw-tQRewBF18drILXRNGMLMlVgtqpIM"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"  # Replace with the actual API URL

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def analyze_resume_with_gemini(resume_text):
    try:
        # Comprehensive prompt for detailed analysis
        prompt = f"""
        Act as an experienced HR manager reviewing a resume. Provide a comprehensive analysis including:
        1. Detailed strengths and areas for improvement
        2. Potential skill gaps
        3. Career development recommendations
        4. ATS (Applicant Tracking System) score estimation
        5. Recommended skills to learn
        6. YouTube learning resources for skill enhancement

        Resume Text:
        {resume_text}
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Extract the text from the response
            analysis = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No analysis provided')
            return analysis
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"

# Streamlit App
st.title("🔍 Resume Analyzer Pro")

# Sidebar for additional information
st.sidebar.header("📌 Quick Tips")
st.sidebar.info("""
- Ensure your resume is clean and well-formatted
- Use clear, professional language
- Quantify your achievements
- Tailor your resume to the job description
""")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Processing your resume...")
        resume_text = extract_text_from_pdf(uploaded_file)
    
    if "Error" in resume_text:
        st.error(resume_text)
    else:
        with col2:
            st.write("Extracted Resume Text:")
            st.text_area("Resume Content", resume_text, height=200)
        
        st.write("🚀 Analyzing your resume...")
        with st.spinner('Generating comprehensive analysis...'):
            analysis_result = analyze_resume_with_gemini(resume_text)
        
        #parsing api response into different sections
        skills_pattern = r"(?<=\*\*5\. Recommended Skills to Learn\*\*\n\n)(.*?)(?=\n\n\*\*6\.)"
        skills_match = re.search(skills_pattern, analysis_result, re.DOTALL)
        recommended_skills_section = skills_match.group(1).strip() if skills_match else ""

        resources_pattern = r"(?<=\*\*6\. YouTube Learning Resources for Skill Enhancement\*\*\n\n)(.*)"
        resources_match = re.search(resources_pattern, analysis_result, re.DOTALL)
        resources_section = resources_match.group(1).strip() if resources_match else ""


        # Formatting the analysis result
        st.markdown("## 📊 Detailed Resume Analysis")
        
        # Create tabs for different analysis sections
        tab1, tab2, tab3 = st.tabs(["📈 Analysis", "🎓 Skill Recommendations", "🎥 Learning Resources"])
        
        with tab1:
            st.markdown("### 🔍 Comprehensive Review")
            st.markdown(analysis_result)
        
        with tab2:
            st.markdown("### 🚀 Skills to Learn")
            # You might want to parse the analysis_result to extract skills
            st.markdown(recommended_skills_section)
        
        with tab3:
            st.markdown("### 📺 Recommended Learning Resources")
            st.markdown(resources_section)