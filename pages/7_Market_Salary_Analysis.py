import streamlit as st
from src.agent import SalaryResearchAgent
from src.ui_components import render_input_form

def main():
    st.set_page_config(
        page_title="Market Salary Analysis",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("Market Salary Analysis 💰")
    st.markdown("""
    Analyze market salaries based on role, experience, skills, and location.
    Get detailed insights and compensation recommendations.
    """)
    
    # Render input form and get user inputs
    user_inputs = render_input_form()
    
    # Process analysis if form is submitted
    if user_inputs:
        try:
            salary_agent = SalaryResearchAgent()
            analysis = salary_agent.analyze_compensation(
                job_title=user_inputs['role'],
                yoe=user_inputs['experience'],
                skills=user_inputs['skills'],
                industry=user_inputs['industry'],
                company_size=user_inputs['company_size'],
                location=user_inputs['location']
            )
            st.markdown(analysis)
        except Exception as e:
            st.error(f"Error analyzing compensation data: {str(e)}")
            st.info("Please try again with different parameters or contact support if the issue persists.")

if __name__ == "__main__":
    main()