import streamlit as st
import os
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PyPDF2 import PdfReader
import json
from utils.ai_analyzer import AIAnalyzer
import plotly.graph_objects as go
import plotly.express as px

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
    
        
        return {
            "key_skills": skills,
            "experience_level": experience,
            "technical_proficiency_score": scores,
            "strengths": strengths,
            "areas_of_improvement": self.analyzer.identify_gaps(resume_text)
            
        }

    def generate_detailed_comparison(self, resumes_data):
        comparison = "### Detailed Comparison of Candidates\n"
        for resume in resumes_data:
            comparison += f"**{resume['filename']}**\n"
            comparison += f"- **Experience Level:** {resume['experience_level']}\n"
            # comparison += f"- **Education Level:** {resume['education_level']}\n"
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
            st.subheader("Resume Overview Analysis")
            
            # Create a more detailed DataFrame for visualization
            overview_data = pd.DataFrame([{
                'Candidate': resume['filename'],
                'Technical Score': resume['technical_proficiency_score'],
                'Experience': float(resume['experience_level'].split()[0]) if resume['experience_level'][0].isdigit() else 0,
                # 'Education Level': resume['education_level'],
                'Skills Count': len(resume['key_skills']),
                'Strengths Count': len(resume['strengths'])
            } for resume in resumes_data])
            
            # Technical Proficiency Comparison with improved styling
            fig1 = px.bar(
                overview_data,
                x='Candidate',
                y='Technical Score',
                # color='Education Level',
                title="Technical Proficiency by Candidate",
                labels={'Technical Score': 'Technical Proficiency Score (%)'},
                template='plotly_white'
            )
            fig1.update_layout(
                xaxis_tickangle=-45,
                yaxis_range=[0, 100],
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Skills and Experience Matrix
            col1, col2 = st.columns(2)
            
            with col1:
                # Experience Distribution
                fig_exp = px.scatter(
                    overview_data,
                    x='Technical Score',
                    y='Experience',
                    size='Skills Count',
                    # color='Education Level',
                    hover_data=['Candidate'],
                    title="Experience vs Technical Score Matrix"
                )
                st.plotly_chart(fig_exp, use_container_width=True)

            with col2:
                # Skills distribution
                all_skills = [skill for resume in resumes_data for skill in resume['key_skills']]
                skills_df = pd.DataFrame(all_skills, columns=['skill']).value_counts().reset_index()
                skills_df.columns = ['skill', 'count']
                
                fig2 = px.pie(
                    skills_df.head(10),  # Show top 10 skills
                    values='count',
                    names='skill',
                    title="Top 10 Skills Distribution",
                    hole=0.4  # Makes it a donut chart
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True)

            # Summary Statistics
            st.subheader("📊 Summary Statistics")
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                avg_tech_score = overview_data['Technical Score'].mean()
                st.metric("Avg Technical Score", f"{avg_tech_score:.1f}%")
                
            with stats_col2:
                avg_exp = overview_data['Experience'].mean()
                st.metric("Avg Experience (Years)", f"{avg_exp:.1f}")
                
            with stats_col3:
                total_skills = len(set(all_skills))
                st.metric("Unique Skills", total_skills)
                
            # with stats_col4:
                # top_edu = overview_data['Education Level'].mode()[0]
                # st.metric("Most Common Education", top_edu)

            # Top Skills Table
            st.subheader("🎯 Top Skills Analysis")
            top_skills = skills_df.head(10)  # Show top 10 skills
            st.table(top_skills.style.format({'count': '{:,.0f}'}))
            
        with tab2:
            st.subheader("Individual Resume Analysis")
            for resume in resumes_data:
                with st.expander(f"📄 {resume['filename']}"):
                    # Top section - Overview
                    st.markdown(f"""
                    ### Overview
                    - **Experience Level**: {resume['experience_level']}
                    - **Technical Score**: {resume['technical_proficiency_score']}/100
                    """)
                    
                    # Skills and Analysis section
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 💪 Core Strengths")
                        for strength in resume['strengths']:
                            st.markdown(f"- ✓ {strength}")
                        
                        st.markdown("### 🎯 Key Skills")
                        skills_chart = px.bar(
                            x=resume['key_skills'],
                            y=[1] * len(resume['key_skills']),
                            labels={'x': 'Skills', 'y': 'Proficiency'},
                            title="Skills Profile"
                        )
                        skills_chart.update_layout(showlegend=False)
                        st.plotly_chart(skills_chart, use_container_width=True)
                    
                    with col2:
                        st.markdown("### 🔄 Development Areas")
                        for area in resume['areas_of_improvement']:
                            st.markdown(f"- ⚡ {area}")
                        
                        # Updated radar chart with actual values
                        categories = ['Technical Skills', 'Experience',
                                    'Communication', 'Leadership']
                        
                        # Calculate normalized scores using actual data
                        exp_years = float(re.search(r'\d+', resume['experience_level']).group() or 0)
                        edu_scores = {
                            'PhD': 100,
                            "Master's": 85,
                            "Bachelor's": 70,
                            "Associate's": 55,
                            'High School': 40,
                            'Not Specified': 30
                        }
                        
                        scores = [
                            resume['technical_proficiency_score'],  # Technical skills score
                            min(exp_years * 10, 100),  # Experience score
                            # edu_scores.get(resume['education_level'], 30),  # Education score
                            len([s for s in resume['strengths'] if any(k in s.lower() for k in 
                                ['communicate', 'written', 'verbal', 'presentation'])]) * 25,  # Communication
                            len([s for s in resume['strengths'] if any(k in s.lower() for k in 
                                ['lead', 'manage', 'team'])]) * 25  # Leadership
                        ]
                        
                        # Normalize all scores to 0-100 range
                        scores = [min(max(score, 0), 100) for score in scores]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(
                            r=scores,
                            theta=categories,
                            fill='toself',
                            name=resume['filename']
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )
                            ),
                            showlegend=False,
                            title="Candidate Profile Radar"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Bottom section - Detailed Metrics
                    st.markdown("### 📊 Detailed Metrics")
                    metrics_col1, metrics_col2= st.columns(2)
                    with metrics_col1:
                        # Calculate skill match percentage based on the number of relevant skills
                        skill_match = resume['technical_proficiency_score']
                        st.metric("Skills Match", f"{skill_match}%")
                    with metrics_col2:
                        st.metric("Experience", resume['experience_level'])
                    # with metrics_col3:
                        # st.metric("Education", resume['education_level'])

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
