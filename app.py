import streamlit as st

def main():
    st.set_page_config(page_title="Resume Filtering System", layout="wide")
   
    st.title("Welcome to the Resume Filtering System �")
 
    st.markdown("""
        ## Overview
        This application assists HR professionals in filtering and processing resumes efficiently.
        Utilize the navigation on the left to switch between the various features of the application:
       
        - **Filter Resumes**: Upload and filter resumes based on job descriptions to find the top candidates. 🔍
        - **Feature Analysis**: Dive deep into candidate skills and assess their suitability. ⚙️
        - **Top CVs**: View and manage the resumes that have been identified as top candidates. 🏆
        - **Email Management**: Send notifications to candidates regarding their application status. 📧
        - **Interview Questions**: Generate role-specific interview questions to prepare for assessments. ❓
        - **Visualizations**: Visualize resume ranking and candidate comparisons with dynamic charts. 📊
        - **Market Salary Analysis**: Analyze market salaries based on role, experience, skills, and location.
                                      Get detailed insights and compensation recommendations. 🤖
       
        ## How to Navigate
        Use the left sidebar to navigate between the different pages of the application. Each page is dedicated to a specific function, allowing you to focus on one task at a time.
       
        ## Further Information
        This tool is built to streamline the initial phases of the recruitment process, helping you to focus on engaging with the most promising candidates. 🚀
    """)

    st.sidebar.success("System Status: Active")
    
if __name__ == "__main__":
    main()