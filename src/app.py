import streamlit as st
from src.agent import SalaryResearchAgent
from src.ui_components import render_header, render_input_form
def main():
    """Main application entry point."""
    # Set page config
    st.set_page_config(
        page_title="Salary Analyzer Pro",
        page_icon="💰",
        layout="wide"
    )

    # Render header
    render_header()

    # Render input form and get user inputs
    user_inputs = render_input_form()
    

    # Process analysis if form is submitted
    if user_inputs:
        with st.spinner("Analyzing compensation data..."):
            try:
                salary_agent = SalaryResearchAgent()
    
            #     # Generate a compensation analysis report
           
                st.markdown(salary_agent.analyze_compensation(
                    job_title=user_inputs['role'],
                    yoe=user_inputs['experience'],
                    skills=user_inputs['skills'],
                    industry=user_inputs['industry'],
                    company_size=user_inputs['company_size'],
                    location=user_inputs['location']
                ))

            except Exception as e:
                st.error(f"Error analyzing compensation data: {str(e)}")

if __name__ == "__main__":
    main()