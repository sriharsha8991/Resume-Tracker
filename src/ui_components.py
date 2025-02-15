import streamlit as st
from typing import List, Dict, Any
from . import config

def render_header():
    """Render the application header."""
    st.title(config.APP_TITLE)
    st.markdown(config.APP_DESCRIPTION)
    st.divider()

def render_input_form() -> Dict[str, Any]:
    """Render the input form and return user inputs."""
    with st.form("salary_analysis_form"):
        # Industry and Role Selection
        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox(
                "Industry Sector",
                options=list(config.INDUSTRY_SECTORS.keys())
            )
        with col2:
            role = st.selectbox(
                "Job Role",
                options=config.INDUSTRY_SECTORS[industry]
            )

        # Experience and Company Size
        col3, col4 = st.columns(2)
        with col3:
            experience = st.slider(
                "Years of Experience",
                min_value=min(config.EXPERIENCE_RANGE),
                max_value=max(config.EXPERIENCE_RANGE),
                value=5
            )
        with col4:
            company_size = st.selectbox(
                "Company Size",
                options=config.COMPANY_SIZES
            )
        location = st.text_input("Location", "Remote")

        # Skills Selection
        skills = []
        for category, category_skills in config.SKILLS_BY_CATEGORY.items():
            st.subheader(f"{category} Skills")
            selected_skills = st.multiselect(
                "Select relevant skills",
                options=category_skills,
                default=category_skills[:2],
                key=category
            )
            skills.extend(selected_skills)

        submit_button = st.form_submit_button("Analyze Compensation")

        if submit_button:
            return {
                "industry": industry,
                "role": role,
                "experience": experience,
                "company_size": company_size,
                "skills": skills,
                "location": location
            }
        return None
