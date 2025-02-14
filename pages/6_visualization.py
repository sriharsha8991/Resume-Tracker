import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PyPDF2 import PdfReader
import json
from utils.ai_analyzer import AIAnalyzer

class ResumeVisualizer:
    def __init__(self):
        self.analyzer = AIAnalyzer()
    
    def extract_text(self, pdf_path):
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def analyze_resume(self, resume_text):
        skills = self.analyzer.extract_skills(resume_text)
        experience = self.analyzer.determine_experience_level(resume_text)
        scores = self.analyzer.calculate_proficiency(resume_text)
        strengths = self.analyzer.identify_strengths(resume_text)
        education = self.analyzer.determine_education_level(resume_text)
        
        return {
            "key_skills": skills,
            "experience_level": experience,
            "technical_proficiency_score": scores,
            "strengths": strengths,
            "areas_of_improvement": self.analyzer.identify_gaps(resume_text),
            "education_level": education
        }

    def generate_detailed_comparison(self, resumes_data):
        comparison = "### Detailed Comparison of Candidates\n"
        for resume in resumes_data:
            comparison += f"**{resume['filename']}**\n"
            comparison += f"- **Experience Level:** {resume['experience_level']}\n"
            comparison += f"- **Education Level:** {resume['education_level']}\n"
            comparison += f"- **Technical Proficiency Score:** {resume['technical_proficiency_score']}\n"
            comparison += f"- **Key Skills:** {', '.join(resume['key_skills'])}\n"
            comparison += f"- **Strengths:** {', '.join(resume['strengths'])}\n"
            comparison += f"- **Areas of Improvement:** {', '.join(resume['areas_of_improvement'])}\n\n"
        return comparison

def main():
    st.title("Resume Insights Dashboard 📊")
    
    visualizer = ResumeVisualizer()
    
    if not os.path.exists("top_resumes"):
        st.error("No resumes found. Please process resumes first.")
        return

    # Analyze all resumes
    resumes_data = []
    with st.spinner("Analyzing resumes..."):
        for filename in os.listdir("top_resumes"):
            if filename.endswith('.pdf'):
                file_path = os.path.join("top_resumes", filename)
                text = visualizer.extract_text(file_path)
                analysis = visualizer.analyze_resume(text)
                if analysis:
                    analysis['filename'] = filename
                    resumes_data.append(analysis)

    if resumes_data:
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Analysis", "Comparison"])
        
        with tab1:
            st.subheader("Technical Proficiency Comparison")
            fig = px.bar(
                pd.DataFrame(resumes_data),
                x='filename',
                y='technical_proficiency_score',
                color='experience_level',
                title="Technical Proficiency by Candidate"
            )
            st.plotly_chart(fig, key="tech_proficiency")

            # Skills distribution for all candidates
            st.subheader("Skills Distribution for All Candidates")
            all_skills = [skill for resume in resumes_data for skill in resume['key_skills']]
            skills_df = pd.DataFrame(all_skills, columns=['skill']).value_counts().reset_index()
            skills_df.columns = ['skill', 'count']
            
            fig2 = px.pie(skills_df, values='count', names='skill', title="Skills Distribution")
            st.plotly_chart(fig2, key="skills_distribution")

        with tab2:
            st.subheader("Individual Resume Analysis")
            for resume in resumes_data:
                with st.expander(f"📄 {resume['filename']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Strengths:**")
                        for strength in resume['strengths']:
                            st.write(f"- {strength}")
                    with col2:
                        st.write("**Areas for Improvement:**")
                        for area in resume['areas_of_improvement']:
                            st.write(f"- {area}")
                    
                    # Radar chart for skills
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[100, resume['technical_proficiency_score'], 80, 90, 85],
                        theta=['Education', 'Technical Skills', 'Experience', 'Communication', 'Overall Fit'],
                        fill='toself'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False
                    )
                    st.plotly_chart(fig, key=f"radar_{resume['filename']}")

        with tab3:
            st.subheader("Comparative Analysis")
            comparison = visualizer.generate_detailed_comparison(resumes_data)
            st.markdown(comparison)

            # Save detailed analysis
            if st.button("Save Detailed Analysis"):
                detailed_report = os.path.join("top_resumes", "detailed_analysis_report.txt")
                with open(detailed_report, 'w') as f:
                    f.write(comparison)
                st.success(f"Detailed analysis saved to {detailed_report}")

    if st.button("Clear History"):
        if os.path.exists("top_resumes"):
            for file in os.listdir("top_resumes"):
                file_path = os.path.join("top_resumes", file)
                os.remove(file_path)
            st.success("History cleared successfully.")

if __name__ == "__main__":
    main()
