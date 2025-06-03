import streamlit as st
import PyPDF2
import re
import google.generativeai as genai
import os

# Configure the Gemini API key
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)  # Replace with your actual key

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def analyze_resume_with_gemini(resume_text):
    try:
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

        model = genai.GenerativeModel("gemini-2.0-flash-lite")  # or use "gemini-1.5-pro-latest" if available
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error generating analysis: {e}"

def parse_analysis_sections(analysis_text):
    """Parse the analysis text into different sections."""
    # Default empty sections
    sections = {
        "analysis": "",
        "skill_gaps": "",
        "career_dev": "",
        "ats_score": "",
        "skills": "",
        "resources": ""
    }
    
    # Simple parsing logic - this can be enhanced with more sophisticated regex patterns
    if "Strengths" in analysis_text:
        sections["analysis"] = analysis_text.split("Potential Skill Gaps")[0].strip()
    
    if "Potential Skill Gaps" in analysis_text:
        sections["skill_gaps"] = analysis_text.split("Potential Skill Gaps")[1].split("Career Development")[0].strip()
    
    if "Career Development" in analysis_text:
        sections["career_dev"] = analysis_text.split("Career Development")[1].split("ATS Score")[0].strip()
    
    if "ATS Score" in analysis_text:
        sections["ats_score"] = analysis_text.split("ATS Score")[1].split("Recommended Skills")[0].strip()
    
    if "Recommended Skills" in analysis_text:
        sections["skills"] = analysis_text.split("Recommended Skills")[1].split("YouTube Learning Resources")[0].strip()
    
    if "YouTube Learning Resources" in analysis_text:
        sections["resources"] = analysis_text.split("YouTube Learning Resources")[1].strip()
    
    return sections

# Streamlit App
st.title("🔍 Resume Analyzer Pro")

st.sidebar.header("📌 Quick Tips")
st.sidebar.info("""
- Ensure your resume is clean and well-formatted
- Use clear, professional language
- Quantify your achievements
- Tailor your resume to the job description
""")

# models = genai.list_models()
# for model in models:
#     print(model.name, "-", model.supported_generation_methods)

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
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
            full_analysis = analyze_resume_with_gemini(resume_text)
            parsed = parse_analysis_sections(full_analysis)

        # Display in the correct tabs
        st.markdown("## 📊 Detailed Resume Analysis")
        tab1, tab2, tab3 = st.tabs(["📈 Analysis", "🎓 Skill Recommendations", "🎥 Learning Resources"])

        with tab1:
            st.markdown("### 🔍 Comprehensive Review")
            st.markdown(f"**Strengths and Areas for Improvement**\n\n{parsed['analysis']}")
            st.markdown(f"**Potential Skill Gaps**\n\n{parsed['skill_gaps']}")
            st.markdown(f"**Career Development Recommendations**\n\n{parsed['career_dev']}")
            st.markdown(f"**ATS Score Estimate**\n\n{parsed['ats_score']}")

        with tab2:
            st.markdown("### 🚀 Skills to Learn")
            st.markdown(parsed["skills"])

        with tab3:
            st.markdown("### 📺 Recommended Learning Resources")
            st.markdown(parsed["resources"])
