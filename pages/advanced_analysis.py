import streamlit as st
import sys
import os
from utils.ai_analyzer import AIAnalyzer
from utils.pdf_processor import PDFProcessor
from utils.question_generator import QuestionGenerator

def main():
    st.title("Advanced Resume Analysis")
    
    analyzer = AIAnalyzer()
    pdf_processor = PDFProcessor()
    question_generator = QuestionGenerator()
    
    st.header("🎯 Skills Gap Analysis")
    resume_file = st.file_uploader("Upload Resume", type="pdf")
    job_desc = st.text_area("Enter Job Description")
    
    if resume_file and job_desc and st.button("Analyze Skills Gap"):
        with st.spinner("Analyzing skills gap..."):
            resume_text = pdf_processor.extract_text(resume_file)
            resume_skills = analyzer.extract_skills(resume_text)
            gap_analysis = analyzer.analyze_skills_gap(resume_skills, job_desc)
            
            st.subheader("Skills Analysis")
            st.write("Identified Skills:")
            st.write(", ".join(resume_skills))
            st.write("Gap Analysis:")
            st.write(gap_analysis)
    
    st.header("💰 Market Salary Analysis")
    experience = st.number_input("Years of Experience", min_value=0, max_value=50)
    skills = st.text_input("Key Skills (comma-separated)")
    location = st.text_input("Location")
    
    if st.button("Analyze Salary"):
        with st.spinner("Analyzing market salary..."):
            salary_analysis = analyzer.analyze_salary(experience, skills, location)
            st.write(salary_analysis)
    
    st.header("🎯 Interview Question Generator")
    role = st.text_input("Job Role")
    required_skills = st.text_input("Required Skills")
    experience_level = st.selectbox("Experience Level", 
                                  ["Entry Level", "Mid Level", "Senior Level"])
    
    if st.button("Generate Questions"):
        with st.spinner("Generating interview questions..."):
            questions = question_generator.generate_questions(
                role, required_skills, experience_level
            )
            st.write(questions)

if __name__ == "__main__":
    main()